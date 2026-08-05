from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.api.deps import get_current_user, RoleChecker as require_role
from app.models.user import User, UserRole
from app.schemas.plan import ProductPlanCreate, ProductPlanUpdate, ProductPlanResponse
from app.services.plan_service import plan_service
from app.common.responses import handle_result

router = APIRouter()

@router.get("/", response_model=List[ProductPlanResponse])
async def list_plans(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN, UserRole.VIEWER]))
):
    result = await plan_service.get_all_plans(db)
    return handle_result(result)

@router.get("/{plan_id}", response_model=ProductPlanResponse)
async def get_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN, UserRole.VIEWER]))
):
    result = await plan_service.get_plan(db, plan_id)
    return handle_result(result)

@router.post("/", response_model=ProductPlanResponse)
async def create_plan(
    plan_in: ProductPlanCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await plan_service.create_plan(db, plan_in, current_user, request)
    return handle_result(result)

@router.patch("/{plan_id}", response_model=ProductPlanResponse)
async def update_plan(
    plan_id: str,
    plan_in: ProductPlanUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await plan_service.update_plan(db, plan_id, plan_in, current_user, request)
    return handle_result(result)

@router.post("/{plan_id}/capabilities/{capability_id}")
async def link_capability_to_plan(
    plan_id: str,
    capability_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await plan_service.link_capability(db, plan_id, capability_id, current_user, request)
    return handle_result(result)

@router.delete("/{plan_id}/capabilities/{capability_id}")
async def unlink_capability_from_plan(
    plan_id: str,
    capability_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await plan_service.unlink_capability(db, plan_id, capability_id, current_user, request)
    return handle_result(result)
