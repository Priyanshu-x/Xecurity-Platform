from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.api.deps import get_current_user, RoleChecker as require_role
from app.models.user import User, UserRole
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
from app.services.subscription_service import subscription_service
from app.common.responses import handle_result

router = APIRouter()

@router.get("/", response_model=List[SubscriptionResponse])
async def list_subscriptions(
    organization_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN, UserRole.SUPPORT]))
):
    if organization_id:
        result = await subscription_service.get_subscriptions_by_organization(db, organization_id, skip, limit)
    else:
        result = await subscription_service.get_all_subscriptions(db, skip, limit)
    return handle_result(result)

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN, UserRole.SUPPORT]))
):
    result = await subscription_service.get_subscription(db, subscription_id)
    return handle_result(result)

@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    sub_in: SubscriptionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await subscription_service.create_subscription(db, sub_in, current_user, request)
    return handle_result(result)

@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    sub_in: SubscriptionUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await subscription_service.update_subscription(db, subscription_id, sub_in, current_user, request)
    return handle_result(result)

@router.post("/{subscription_id}/suspend", response_model=SubscriptionResponse)
async def suspend_subscription(
    subscription_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await subscription_service.suspend_subscription(db, subscription_id, current_user, request)
    return handle_result(result)

@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    subscription_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await subscription_service.cancel_subscription(db, subscription_id, current_user, request)
    return handle_result(result)
