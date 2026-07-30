from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.api.deps import get_current_user, RoleChecker as require_role
from app.models.user import User, UserRole
from app.schemas.capability import CapabilityCreate, CapabilityUpdate, CapabilityResponse
from app.services.capability_service import capability_service
from app.common.responses import handle_result

router = APIRouter()

@router.get("/", response_model=List[CapabilityResponse])
async def list_capabilities(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN, UserRole.SUPPORT]))
):
    result = await capability_service.get_all_capabilities(db)
    return handle_result(result)

@router.get("/{capability_id}", response_model=CapabilityResponse)
async def get_capability(
    capability_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN, UserRole.SUPPORT]))
):
    result = await capability_service.get_capability(db, capability_id)
    return handle_result(result)

@router.post("/", response_model=CapabilityResponse)
async def create_capability(
    capability_in: CapabilityCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await capability_service.create_capability(db, capability_in, current_user, request)
    return handle_result(result)

@router.patch("/{capability_id}", response_model=CapabilityResponse)
async def update_capability(
    capability_id: str,
    capability_in: CapabilityUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await capability_service.update_capability(db, capability_id, capability_in, current_user, request)
    return handle_result(result)

@router.delete("/{capability_id}")
async def delete_capability(
    capability_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await capability_service.delete_capability(db, capability_id, current_user, request)
    return handle_result(result)

@router.post("/{capability_id}/link/{product_id}")
async def link_capability_to_product(
    capability_id: str,
    product_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await capability_service.link_capability_to_product(db, capability_id, product_id, current_user, request)
    return handle_result(result)

@router.delete("/{capability_id}/unlink/{product_id}")
async def unlink_capability_from_product(
    capability_id: str,
    product_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await capability_service.unlink_capability_from_product(db, capability_id, product_id, current_user, request)
    return handle_result(result)

@router.get("/product/{product_id}", response_model=List[CapabilityResponse])
async def get_product_capabilities(
    product_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN, UserRole.SUPPORT]))
):
    result = await capability_service.get_product_capabilities(db, product_id)
    return handle_result(result)
