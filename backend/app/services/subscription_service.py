from typing import List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.common.result import Result, Success, NotFoundError, ConflictError
from app.models.user import User
from app.models.subscription import Subscription
from app.repositories.subscription import subscription_repository
from app.repositories.plan import plan_repository
from app.repositories.organization import organization_repository
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
from app.common.enums import SubscriptionStatus
from app.events.bus import EventBus
from app.events.events import DomainEvent

event_bus = EventBus()

class SubscriptionService:
    async def create_subscription(
        self, db: AsyncSession, sub_in: SubscriptionCreate, current_user: User, request: Request
    ) -> Result[SubscriptionResponse]:
        
        # Validate Organization
        org = await organization_repository.get(db, id=sub_in.organization_id)
        if not org:
            return NotFoundError(f"Organization with ID {sub_in.organization_id} not found")

        # Validate ProductPlan
        plan = await plan_repository.get(db, id=sub_in.product_plan_id)
        if not plan:
            return NotFoundError(f"ProductPlan with ID {sub_in.product_plan_id} not found")

        # Check if already active/trial for this plan
        existing = await subscription_repository.get_active_by_organization_and_plan(db, sub_in.organization_id, sub_in.product_plan_id)
        if existing:
            return ConflictError(f"Organization already has an active subscription for plan {sub_in.product_plan_id}")

        # Create
        subscription = await subscription_repository.create(db, obj_in=sub_in)
        
        # To get relationships loaded
        subscription = await subscription_repository.get_with_relations(db, id=subscription.id)

        await event_bus.publish(DomainEvent(
            entity="Subscription",
            entity_id=subscription.id,
            action="SUBSCRIPTION_CREATED",
            old_value=None,
            new_value=sub_in.model_dump(),
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)

        return Success(SubscriptionResponse.model_validate(subscription))

    async def get_subscription(self, db: AsyncSession, subscription_id: str) -> Result[SubscriptionResponse]:
        subscription = await subscription_repository.get_with_relations(db, id=subscription_id)
        if not subscription:
            return NotFoundError("Subscription not found")
        return Success(SubscriptionResponse.model_validate(subscription))

    async def get_all_subscriptions(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Result[List[SubscriptionResponse]]:
        subscriptions = await subscription_repository.get_multi(db, skip=skip, limit=limit)
        return Success([SubscriptionResponse.model_validate(sub) for sub in subscriptions])

    async def get_subscriptions_by_organization(
        self, db: AsyncSession, organization_id: str, skip: int = 0, limit: int = 100
    ) -> Result[List[SubscriptionResponse]]:
        subscriptions = await subscription_repository.get_by_organization(db, organization_id=organization_id, skip=skip, limit=limit)
        return Success([SubscriptionResponse.model_validate(sub) for sub in subscriptions])

    async def update_subscription(
        self, db: AsyncSession, subscription_id: str, sub_in: SubscriptionUpdate, current_user: User, request: Request
    ) -> Result[SubscriptionResponse]:
        subscription = await subscription_repository.get_with_relations(db, id=subscription_id)
        if not subscription:
            return NotFoundError("Subscription not found")

        old_value = {
            "status": subscription.status,
            "notes": subscription.notes,
            "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None
        }

        updated_subscription = await subscription_repository.update(db, db_obj=subscription, obj_in=sub_in)

        new_value = sub_in.model_dump(exclude_unset=True)
        if new_value:
            await event_bus.publish(DomainEvent(
                entity="Subscription",
                entity_id=updated_subscription.id,
                action="SUBSCRIPTION_UPDATED",
                old_value=old_value,
                new_value=new_value,
                actor=current_user.id,
                request_id=getattr(request.state, "request_id", None)
            ), db=db)

        return Success(SubscriptionResponse.model_validate(updated_subscription))

    async def suspend_subscription(
        self, db: AsyncSession, subscription_id: str, current_user: User, request: Request
    ) -> Result[SubscriptionResponse]:
        subscription = await subscription_repository.get_with_relations(db, id=subscription_id)
        if not subscription:
            return NotFoundError("Subscription not found")

        if subscription.status == SubscriptionStatus.SUSPENDED:
            return ConflictError("Subscription is already suspended")

        old_status = subscription.status
        subscription.status = SubscriptionStatus.SUSPENDED
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

        await event_bus.publish(DomainEvent(
            entity="Subscription",
            entity_id=subscription.id,
            action="SUBSCRIPTION_SUSPENDED",
            old_value={"status": old_status},
            new_value={"status": SubscriptionStatus.SUSPENDED},
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)

        return Success(SubscriptionResponse.model_validate(subscription))

    async def cancel_subscription(
        self, db: AsyncSession, subscription_id: str, current_user: User, request: Request
    ) -> Result[SubscriptionResponse]:
        subscription = await subscription_repository.get_with_relations(db, id=subscription_id)
        if not subscription:
            return NotFoundError("Subscription not found")

        if subscription.status == SubscriptionStatus.CANCELLED:
            return ConflictError("Subscription is already cancelled")

        old_status = subscription.status
        subscription.status = SubscriptionStatus.CANCELLED
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

        await event_bus.publish(DomainEvent(
            entity="Subscription",
            entity_id=subscription.id,
            action="SUBSCRIPTION_CANCELLED",
            old_value={"status": old_status},
            new_value={"status": SubscriptionStatus.CANCELLED},
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)

        return Success(SubscriptionResponse.model_validate(subscription))

subscription_service = SubscriptionService()
