from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.api.deps import RoleChecker, get_current_active_user
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])

# Only OWNER can access these routes
require_owner = Depends(RoleChecker([UserRole.OWNER]))

@router.get("/", response_model=List[UserResponse], dependencies=[require_owner])
async def list_users(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all users.
    """
    return await user_service.get_all(db)

@router.get("/{id}", response_model=UserResponse, dependencies=[require_owner])
async def get_user(
    id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get a specific user by ID.
    """
    user = await user_service.get_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse, dependencies=[require_owner])
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new user.
    """
    return await user_service.create(db, user_in)

@router.patch("/{id}", response_model=UserResponse)
async def update_user(
    id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    _ = require_owner
):
    """
    Update a user.
    """
    return await user_service.update(db, id, user_in, current_user.id)

@router.post("/{id}/disable", response_model=UserResponse)
async def disable_user(
    id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    _ = require_owner
):
    """
    Soft delete / Disable a user.
    """
    return await user_service.disable(db, id, current_user.id)
