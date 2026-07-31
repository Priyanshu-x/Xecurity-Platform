from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activation_request_event import ActivationRequestEvent
from app.repositories.base import BaseRepository
from pydantic import BaseModel

class ActivationRequestEventBase(BaseModel):
    pass

class ActivationRequestEventRepository(BaseRepository[ActivationRequestEvent, ActivationRequestEventBase, ActivationRequestEventBase]):
    async def get_by_request_id(self, db: AsyncSession, request_id: str) -> List[ActivationRequestEvent]:
        result = await db.execute(
            select(ActivationRequestEvent)
            .filter(ActivationRequestEvent.request_id == request_id)
            .order_by(ActivationRequestEvent.timestamp.asc())
        )
        return list(result.scalars().all())

activation_request_event_repository = ActivationRequestEventRepository(ActivationRequestEvent)
