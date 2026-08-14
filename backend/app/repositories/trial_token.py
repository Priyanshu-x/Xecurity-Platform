from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.repositories.base import BaseRepository
from app.models.trial_token import TrialToken

class TrialTokenRepository(BaseRepository[TrialToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(TrialToken, session)

    async def get_active_token(self) -> Optional[TrialToken]:
        stmt = select(TrialToken).where(TrialToken.is_active == True).order_by(TrialToken.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().first()
