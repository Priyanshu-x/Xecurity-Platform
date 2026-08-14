from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.repositories.base import BaseRepository
from app.models.trial_token import TrialToken
from app.schemas.trial_token import TrialTokenCreate, TrialTokenUpdate

class TrialTokenRepository(BaseRepository[TrialToken, TrialTokenCreate, TrialTokenUpdate]):
    def __init__(self):
        super().__init__(TrialToken)

    async def get_active_token(self, db: AsyncSession) -> Optional[TrialToken]:
        stmt = select(TrialToken).where(TrialToken.is_active == True).order_by(TrialToken.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().first()
