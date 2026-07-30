from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db_session
from app.models.user import User
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate, DeploymentResponse
from app.services.deployment_service import deployment_service
from app.api.dependencies import RoleChecker
from app.common.enums import Role
from app.api.routes.utils import handle_result

router = APIRouter(prefix="/deployments", tags=["deployments"])
admin_only = RoleChecker([Role.ADMIN])

@router.post("/", response_model=DeploymentResponse)
async def create_deployment(
    request: Request,
    deployment_in: DeploymentCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_only)
):
    result = await deployment_service.create_deployment(db, deployment_in, current_user, request)
    return handle_result(result)

@router.get("/", response_model=List[DeploymentResponse])
async def list_deployments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_only)
):
    result = await deployment_service.get_all_deployments(db, skip, limit)
    return handle_result(result)

@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_only)
):
    result = await deployment_service.get_deployment(db, deployment_id)
    return handle_result(result)

@router.patch("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    request: Request,
    deployment_id: str,
    update_in: DeploymentUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_only)
):
    result = await deployment_service.update_deployment(db, deployment_id, update_in, current_user, request)
    return handle_result(result)

@router.delete("/{deployment_id}", status_code=204)
async def delete_deployment(
    request: Request,
    deployment_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_only)
):
    result = await deployment_service.delete_deployment(db, deployment_id, current_user, request)
    handle_result(result)
