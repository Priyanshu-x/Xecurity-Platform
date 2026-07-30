import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
import uuid

from app.main import app
from app.core.config import settings
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password

# Database fixtures moved to conftest.py

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_password_hashing():
    password = "supersecret"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

@pytest.mark.asyncio
async def test_owner_login_and_me():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Login
        response = await ac.post(
            "/api/v1/auth/login", 
            data={"username": "admin@xecurity.com", "password": "changeme123"}
        )
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        # Verify /me endpoint
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        me_resp = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "admin@xecurity.com"
        assert me_resp.json()["role"] == "OWNER"

@pytest.mark.asyncio
async def test_inactive_user_cannot_login(db):
    # Setup inactive user
    inactive_user = User(
        email=f"inactive_{uuid.uuid4()}@xecurity.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.VIEWER,
        is_active=False
    )
    db.add(inactive_user)
    await db.commit()
    await db.refresh(inactive_user)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/login", 
            data={"username": inactive_user.email, "password": "password123"}
        )
        assert response.status_code == 400
        assert "Inactive" in response.json()["detail"]

@pytest.mark.asyncio
async def test_refresh_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/login", 
            data={"username": "admin@xecurity.com", "password": "changeme123"}
        )
        refresh_token = response.json()["refresh_token"]
        
        refresh_resp = await ac.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_resp.status_code == 200
        assert "access_token" in refresh_resp.json()

@pytest.mark.asyncio
async def test_role_based_authorization(db):
    # To test RBAC, we need a test endpoint that requires a specific role.
    from fastapi import Depends
    from app.api.deps import RoleChecker
    
    @app.get("/api/v1/test/admin-only")
    async def admin_only_endpoint(user: User = Depends(RoleChecker([UserRole.ADMIN]))):
        return {"msg": "success"}

    # Setup viewer user
    viewer_user = User(
        email=f"viewer_{uuid.uuid4()}@xecurity.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.VIEWER,
        is_active=True
    )
    db.add(viewer_user)
    await db.commit()
    await db.refresh(viewer_user)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Viewer login
        resp = await ac.post("/api/v1/auth/login", data={"username": viewer_user.email, "password": "password123"})
        viewer_token = resp.json()["access_token"]
        
        # Owner login
        resp = await ac.post("/api/v1/auth/login", data={"username": "admin@xecurity.com", "password": "changeme123"})
        owner_token = resp.json()["access_token"]
        
        # Viewer trying to access ADMIN endpoint -> 403 Forbidden
        viewer_resp = await ac.get("/api/v1/test/admin-only", headers={"Authorization": f"Bearer {viewer_token}"})
        assert viewer_resp.status_code == 403
        
        # Owner trying to access ADMIN endpoint -> 200 OK (OWNER bypasses RBAC)
        owner_resp = await ac.get("/api/v1/test/admin-only", headers={"Authorization": f"Bearer {owner_token}"})
        assert owner_resp.status_code == 200
