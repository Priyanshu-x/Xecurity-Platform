from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db_session
from app.models.user import User, UserRole
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.api.deps import get_current_active_user, RoleChecker
from app.services.organization_service import organization_service
from app.common.responses import handle_result

router = APIRouter()

@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    request: Request,
    org_in: OrganizationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await organization_service.create_organization(db, org_in, current_user, request)
    return handle_result(result)

@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await organization_service.list_organizations(db, include_deleted)
    return handle_result(result)

@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await organization_service.get_organization(db, org_id)
    return handle_result(result)

@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    request: Request,
    org_id: str,
    org_in: OrganizationUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await organization_service.update_organization(db, org_id, org_in, current_user, request)
    return handle_result(result)

@router.delete("/{org_id}")
async def delete_organization(
    request: Request,
    org_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await organization_service.delete_organization(db, org_id, current_user, request)
    handle_result(result)
    return {"message": "Organization deleted successfully"}
