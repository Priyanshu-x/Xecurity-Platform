from app.repositories.base import BaseRepository
from app.models.organization import Organization
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class OrganizationRepository(BaseRepository[Organization, BaseModel, BaseModel]):
    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> list[Organization]:
        stmt = select(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

organization_repo = OrganizationRepository(Organization)
