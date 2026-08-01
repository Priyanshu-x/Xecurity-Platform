from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.repositories.base import BaseRepository
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserBase

class UserRepository(BaseRepository[User, UserCreate, UserBase]):
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
        
    async def count_owners(self, db: AsyncSession) -> int:
        stmt = select(func.count(User.id)).where(User.role == UserRole.OWNER, User.is_active == True)
        result = await db.execute(stmt)
        return result.scalar_one()

user_repository = UserRepository(User)
