import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import uuid
from app.main import app
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.models.product import Product, ProductStatus

@pytest_asyncio.fixture
async def auth_tokens(db):
    # Setup owner user
    owner = User(
        email=f"owner_{uuid.uuid4()}@xecurity.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.OWNER,
        is_active=True
    )
    db.add(owner)
    
    # Setup viewer user
    viewer = User(
        email=f"viewer_{uuid.uuid4()}@xecurity.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.VIEWER,
        is_active=True
    )
    db.add(viewer)
    
    await db.commit()
    await db.refresh(owner)
    await db.refresh(viewer)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        owner_resp = await ac.post("/api/v1/auth/login", data={"username": owner.email, "password": "password123"})
        viewer_resp = await ac.post("/api/v1/auth/login", data={"username": viewer.email, "password": "password123"})
        
    return {
        "owner": owner_resp.json()["access_token"],
        "viewer": viewer_resp.json()["access_token"]
    }

@pytest.mark.asyncio
async def test_product_crud_flow(db, auth_tokens):
    owner_token = auth_tokens["owner"]
    viewer_token = auth_tokens["viewer"]
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
        
        # 1. VIEWER cannot create product
        product_data = {
            "name": "Test Product",
            "slug": "test-product",
            "status": "ACTIVE"
        }
        r = await ac.post("/api/v1/products/", json=product_data, headers=viewer_headers)
        assert r.status_code == 403
        
        # 2. OWNER can create product
        r = await ac.post("/api/v1/products/", json=product_data, headers=owner_headers)
        assert r.status_code == 200
        product_id = r.json()["id"]
        assert r.json()["name"] == "Test Product"
        
        # 3. VIEWER can list products
        r = await ac.get("/api/v1/products/", headers=viewer_headers)
        assert r.status_code == 200
        assert len(r.json()) >= 1
        
        # 4. OWNER can update product
        r = await ac.put(f"/api/v1/products/{product_id}", json={"description": "Updated"}, headers=owner_headers)
        assert r.status_code == 200
        assert r.json()["description"] == "Updated"
        
        # 5. VIEWER cannot delete product
        r = await ac.delete(f"/api/v1/products/{product_id}", headers=viewer_headers)
        assert r.status_code == 403
        
        # 6. OWNER can delete product (soft delete)
        r = await ac.delete(f"/api/v1/products/{product_id}", headers=owner_headers)
        assert r.status_code == 200
        
        # 7. List should not show deleted product
        r = await ac.get("/api/v1/products/", headers=viewer_headers)
        assert product_id not in [p["id"] for p in r.json()]
        
        # 8. Dashboard stats should exclude deleted
        r = await ac.get("/api/v1/products/dashboard/stats", headers=owner_headers)
        assert r.status_code == 200
        assert "total_products" in r.json()
