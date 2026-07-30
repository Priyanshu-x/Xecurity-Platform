from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt, JWTError

from app.api.deps import SessionDep, get_current_active_user, get_db_session
from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from app.models.user import User
from app.schemas.auth import Token, RefreshRequest, ChangePassword
from app.schemas.user import UserResponse

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    db: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "access_token": create_access_token(subject=user.id),
        "refresh_token": create_refresh_token(subject=user.id),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    db: SessionDep,
    request: RefreshRequest
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
        
    return {
        "access_token": create_access_token(subject=user.id),
        "refresh_token": create_refresh_token(subject=user.id),
        "token_type": "bearer",
    }

@router.post("/logout")
async def logout():
    # In a stateless JWT system, logout is mostly handled client-side by deleting the token.
    # To implement server-side logout, we would need a token blocklist in Redis or the DB.
    # For now, we return a success response for the client to act on.
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

@router.post("/change-password")
async def change_password(
    request: ChangePassword,
    db: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid current password")
        
    current_user.hashed_password = get_password_hash(request.new_password)
    await db.commit()
    return {"message": "Password updated successfully"}
