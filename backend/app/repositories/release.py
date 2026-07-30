from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sa_update

from app.models.release import Release
from app.schemas.release import ReleaseCreate, ReleaseUpdate
from app.repositories.base import BaseRepository

class ReleaseRepository(BaseRepository[Release, ReleaseCreate, ReleaseUpdate]):
    def __init__(self):
        super().__init__(Release)

    async def get_latest_release(self, db: AsyncSession, product_id: str, channel: str, platform: str) -> Optional[Release]:
        """Get the release marked as is_latest=True for a specific product, channel, and platform."""
        stmt = select(self.model).where(
            self.model.product_id == product_id,
            self.model.channel == channel,
            self.model.platform == platform,
            self.model.is_latest == True,
            self.model.is_deleted == False
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def demote_latest_release(self, db: AsyncSession, product_id: str, channel: str, platform: str) -> None:
        """Sets is_latest=False for any release matching the criteria."""
        stmt = (
            sa_update(self.model)
            .where(
                self.model.product_id == product_id,
                self.model.channel == channel,
                self.model.platform == platform,
                self.model.is_latest == True
            )
            .values(is_latest=False)
        )
        await db.execute(stmt)
        await db.flush()

release_repository = ReleaseRepository()
