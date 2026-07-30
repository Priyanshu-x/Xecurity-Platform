from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.repositories.base import BaseRepository
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate

class DeploymentRepository(BaseRepository[Deployment, DeploymentCreate, DeploymentUpdate]):
    
    async def get_by_organization(
        self, db: AsyncSession, organization_id: str, skip: int = 0, limit: int = 100
    ) -> List[Deployment]:
        result = await db.execute(
            select(Deployment)
            .where(Deployment.organization_id == organization_id)
            .where(Deployment.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_product(
        self, db: AsyncSession, product_id: str, skip: int = 0, limit: int = 100
    ) -> List[Deployment]:
        result = await db.execute(
            select(Deployment)
            .where(Deployment.product_id == product_id)
            .where(Deployment.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

deployment_repository = DeploymentRepository(Deployment)
