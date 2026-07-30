from typing import Optional, List, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exc

from app.repositories.base import BaseRepository
from app.models.capability import Capability, ProductCapability
from app.schemas.capability import CapabilityCreate, CapabilityUpdate

class CapabilityRepository(BaseRepository[Capability, CapabilityCreate, CapabilityUpdate]):
    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[Capability]:
        result = await db.execute(select(self.model).filter(self.model.slug == slug))
        return result.scalars().first()

    async def get_capabilities_for_product(self, db: AsyncSession, product_id: str) -> List[Capability]:
        result = await db.execute(
            select(Capability)
            .join(ProductCapability)
            .filter(ProductCapability.product_id == product_id)
            .filter(Capability.is_deleted == False)
        )
        return list(result.scalars().all())

    async def link_to_product(self, db: AsyncSession, capability_id: str, product_id: str) -> bool:
        link = ProductCapability(product_id=product_id, capability_id=capability_id)
        db.add(link)
        try:
            await db.flush()
            return True
        except exc.IntegrityError:
            await db.rollback()
            return False

    async def unlink_from_product(self, db: AsyncSession, capability_id: str, product_id: str) -> bool:
        result = await db.execute(
            select(ProductCapability)
            .filter(ProductCapability.product_id == product_id)
            .filter(ProductCapability.capability_id == capability_id)
        )
        link = result.scalars().first()
        if link:
            await db.delete(link)
            await db.flush()
            return True
        return False

capability_repository = CapabilityRepository(Capability)
