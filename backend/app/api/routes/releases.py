from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db_session
from app.models.user import User, UserRole
from app.schemas.release import ReleaseCreate, ReleaseUpdate, ReleaseResponse
from app.api.deps import get_current_active_user, RoleChecker
from app.services.release_service import release_service
from app.common.responses import handle_result

router = APIRouter()

@router.post("/", response_model=ReleaseResponse)
async def create_release(
    request: Request,
    release_in: ReleaseCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await release_service.create_release(db, release_in, current_user, request)
    return handle_result(result)

@router.get("/product/{product_id}", response_model=List[ReleaseResponse])
async def list_releases_for_product(
    product_id: str,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    result = await release_service.list_releases(db, product_id, include_deleted)
    return handle_result(result)

@router.get("/{release_id}", response_model=ReleaseResponse)
async def get_release(
    release_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    result = await release_service.get_release(db, release_id)
    return handle_result(result)

@router.put("/{release_id}", response_model=ReleaseResponse)
async def update_release(
    request: Request,
    release_id: str,
    release_in: ReleaseUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await release_service.update_release(db, release_id, release_in, current_user, request)
    return handle_result(result)

@router.delete("/{release_id}")
async def delete_release(
    request: Request,
    release_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await release_service.delete_release(db, release_id, current_user, request)
    handle_result(result)
    return {"message": "Release deleted successfully"}
