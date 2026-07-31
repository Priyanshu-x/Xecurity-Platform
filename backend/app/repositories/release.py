from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sa_update, func
from sqlalchemy.orm import selectinload

from app.models.release import Release
from app.schemas.release import ReleaseCreate, ReleaseUpdate
from app.repositories.base import BaseRepository

class ReleaseRepository(BaseRepository[Release, ReleaseCreate, ReleaseUpdate]):
    def __init__(self):
        super().__init__(Release)

    async def get(self, db: AsyncSession, id: Any) -> Optional[Release]:
        result = await db.execute(
            select(self.model).options(selectinload(self.model.artifacts)).where(self.model.id == id)
        )
        return result.scalars().first()

    async def paginate(self, db: AsyncSession, page: int = 1, size: int = 50, include_deleted: bool = False, **kwargs) -> tuple[List[Release], int]:
        stmt = select(self.model).options(selectinload(self.model.artifacts))
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)
            
        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
            
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()
        
        skip = (page - 1) * size
        stmt = stmt.offset(skip).limit(size)
        items = list((await db.execute(stmt)).scalars().all())
        
        return items, total

    async def get_latest_release(self, db: AsyncSession, product_id: str, channel: str) -> Optional[Release]:
        """Get the release marked as is_latest=True for a specific product and channel."""
        stmt = select(self.model).options(selectinload(self.model.artifacts)).where(
            self.model.product_id == product_id,
            self.model.channel == channel,
            self.model.is_latest == True,
            self.model.is_deleted == False
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def demote_latest_release(self, db: AsyncSession, product_id: str, channel: str) -> None:
        """Sets is_latest=False for any release matching the criteria."""
        stmt = (
            sa_update(self.model)
            .where(
                self.model.product_id == product_id,
                self.model.channel == channel,
                self.model.is_latest == True
            )
            .values(is_latest=False)
        )
        await db.execute(stmt)
        await db.flush()

release_repository = ReleaseRepository()
