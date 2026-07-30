from typing import List, Any
from fastapi import APIRouter, Depends, Request

from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user, RoleChecker
from app.models.user import User
from app.common.enums import UserRole
from app.schemas.license import LicenseResponse, LicenseIssue, LicenseRevoke
from app.services.license_service import license_service
from app.common.result import handle_result

router = APIRouter()

allow_admin_owner = RoleChecker([UserRole.OWNER, UserRole.ADMIN])
allow_support_up = RoleChecker([UserRole.OWNER, UserRole.ADMIN, UserRole.SUPPORT])

@router.post("/{deployment_id}/issue", response_model=LicenseResponse, dependencies=[Depends(allow_admin_owner)])
async def issue_license(
    deployment_id: str,
    issue_in: LicenseIssue,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Issue a new license for a deployment from a subscription."""
    result = await license_service.issue_license(db, deployment_id, issue_in, current_user, request)
    return handle_result(result)

@router.post("/{license_id}/revoke", response_model=LicenseResponse, dependencies=[Depends(allow_admin_owner)])
async def revoke_license(
    license_id: str,
    revoke_in: LicenseRevoke,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Revoke an active license."""
    result = await license_service.revoke_license(db, license_id, revoke_in, current_user, request)
    return handle_result(result)

@router.get("/{license_id}", response_model=LicenseResponse, dependencies=[Depends(allow_support_up)])
async def get_license(
    license_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get a license by ID."""
    result = await license_service.get_license(db, license_id)
    return handle_result(result)

@router.get("/", response_model=List[LicenseResponse], dependencies=[Depends(allow_support_up)])
async def list_licenses(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List licenses."""
    result = await license_service.list_licenses(db, skip=skip, limit=limit)
    return handle_result(result)
