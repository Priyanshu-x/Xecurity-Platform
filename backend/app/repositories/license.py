from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.license import License
from app.schemas.license import LicenseIssue, LicenseRevoke
from app.common.enums import LicenseStatus

class LicenseRepository(BaseRepository[License, LicenseIssue, LicenseRevoke]):
    
    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[License]:
        result = await db.execute(
            select(License)
            .options(
                selectinload(License.organization),
                selectinload(License.product),
                selectinload(License.subscription),
                selectinload(License.deployment)
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_relations(self, db: AsyncSession, id: str) -> Optional[License]:
        result = await db.execute(
            select(License)
            .options(
                selectinload(License.organization),
                selectinload(License.product),
                selectinload(License.subscription),
                selectinload(License.deployment)
            )
            .where(License.id == id)
        )
        return result.scalars().first()

    async def get_active_by_deployment(self, db: AsyncSession, deployment_id: str) -> Optional[License]:
        result = await db.execute(
            select(License).where(
                License.deployment_id == deployment_id,
                License.status == LicenseStatus.ACTIVE
            )
        )
        return result.scalars().first()

    async def get_by_subscription(self, db: AsyncSession, subscription_id: str, skip: int = 0, limit: int = 100) -> List[License]:
        result = await db.execute(
            select(License)
            .options(
                selectinload(License.organization),
                selectinload(License.product),
                selectinload(License.subscription),
                selectinload(License.deployment)
            )
            .where(
                License.subscription_id == subscription_id
            ).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

license_repository = LicenseRepository(License)
