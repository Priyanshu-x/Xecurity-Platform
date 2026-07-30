from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.plan import ProductPlan, ProductPlanCapability
from app.models.capability import Capability
from app.schemas.plan import ProductPlanCreate, ProductPlanUpdate

class PlanRepository(BaseRepository[ProductPlan, ProductPlanCreate, ProductPlanUpdate]):
    
    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[ProductPlan]:
        result = await db.execute(
            select(ProductPlan)
            .options(selectinload(ProductPlan.capabilities).selectinload(ProductPlanCapability.capability))
            .where(ProductPlan.slug == slug)
        )
        return result.scalars().first()
        
    async def get_with_capabilities(self, db: AsyncSession, plan_id: str) -> Optional[ProductPlan]:
        result = await db.execute(
            select(ProductPlan)
            .options(selectinload(ProductPlan.capabilities).selectinload(ProductPlanCapability.capability))
            .where(ProductPlan.id == plan_id)
        )
        return result.scalars().first()

    async def get_by_product_id(self, db: AsyncSession, product_id: str) -> List[ProductPlan]:
        result = await db.execute(
            select(ProductPlan)
            .options(selectinload(ProductPlan.capabilities).selectinload(ProductPlanCapability.capability))
            .where(ProductPlan.product_id == product_id)
        )
        return list(result.scalars().all())

    async def link_capability(self, db: AsyncSession, plan_id: str, capability_id: str) -> ProductPlanCapability:
        link = ProductPlanCapability(plan_id=plan_id, capability_id=capability_id)
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return link

    async def unlink_capability(self, db: AsyncSession, plan_id: str, capability_id: str) -> bool:
        result = await db.execute(
            select(ProductPlanCapability)
            .where(
                ProductPlanCapability.plan_id == plan_id,
                ProductPlanCapability.capability_id == capability_id
            )
        )
        link = result.scalars().first()
        if link:
            await db.delete(link)
            await db.commit()
            return True
        return False

plan_repository = PlanRepository(ProductPlan)
