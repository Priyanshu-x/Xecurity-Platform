from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.subscription import Subscription
from app.models.plan import ProductPlan
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate
from app.common.enums import SubscriptionStatus
from app.models.plan import ProductPlanCapability

class SubscriptionRepository(BaseRepository[Subscription, SubscriptionCreate, SubscriptionUpdate]):
    
    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Subscription]:
        result = await db.execute(
            select(Subscription)
            .options(
                selectinload(Subscription.product_plan).selectinload(ProductPlan.capabilities).selectinload(ProductPlanCapability.capability),
                selectinload(Subscription.organization)
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_relations(self, db: AsyncSession, id: str) -> Optional[Subscription]:
        result = await db.execute(
            select(Subscription)
            .options(
                selectinload(Subscription.product_plan).selectinload(ProductPlan.capabilities).selectinload(ProductPlanCapability.capability),
                selectinload(Subscription.organization)
            )
            .where(Subscription.id == id)
        )
        return result.scalars().first()
        
    async def get_by_organization(
        self, db: AsyncSession, organization_id: str, skip: int = 0, limit: int = 100
    ) -> List[Subscription]:
        result = await db.execute(
            select(Subscription)
            .options(
                selectinload(Subscription.product_plan).selectinload(ProductPlan.capabilities).selectinload(ProductPlanCapability.capability),
                selectinload(Subscription.organization)
            )
            .where(Subscription.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_product_plan(
        self, db: AsyncSession, product_plan_id: str, skip: int = 0, limit: int = 100
    ) -> List[Subscription]:
        result = await db.execute(
            select(Subscription)
            .where(Subscription.product_plan_id == product_plan_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_active_by_organization_and_plan(
        self, db: AsyncSession, organization_id: str, product_plan_id: str
    ) -> Optional[Subscription]:
        result = await db.execute(
            select(Subscription)
            .where(
                Subscription.organization_id == organization_id,
                Subscription.product_plan_id == product_plan_id,
                Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
            )
        )
        return result.scalars().first()

subscription_repository = SubscriptionRepository(Subscription)
