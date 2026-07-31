from typing import Optional, List, Tuple
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activation_request import ActivationRequest
from app.repositories.base import BaseRepository
from app.schemas.activation_request import ActivationRequestBase

class ActivationRequestRepository(BaseRepository[ActivationRequest, ActivationRequestBase, ActivationRequestBase]):
    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100, device_id: Optional[str] = None) -> List[ActivationRequest]:
        query = select(self.model).options(selectinload(self.model.events))
        if device_id:
            query = query.filter(self.model.device_id == device_id)
        query = query.offset(skip).limit(limit).order_by(desc(self.model.created_at))
        result = await db.execute(query)
        return list(result.scalars().all())

    async def count(self, db: AsyncSession, device_id: Optional[str] = None) -> int:
        query = select(func.count()).select_from(self.model)
        if device_id:
            query = query.filter(self.model.device_id == device_id)
        result = await db.execute(query)
        return result.scalar() or 0

    async def get_with_events(self, db: AsyncSession, id: str) -> Optional[ActivationRequest]:
        result = await db.execute(
            select(ActivationRequest)
            .options(selectinload(ActivationRequest.events))
            .filter(ActivationRequest.id == id)
        )
        return result.scalars().first()

    async def get_by_request_number(self, db: AsyncSession, request_number: str) -> Optional[ActivationRequest]:
        result = await db.execute(
            select(ActivationRequest)
            .filter(ActivationRequest.request_number == request_number)
        )
        return result.scalars().first()

    async def get_by_sha256(self, db: AsyncSession, sha256: str) -> Optional[ActivationRequest]:
        result = await db.execute(
            select(ActivationRequest)
            .options(selectinload(ActivationRequest.events))
            .filter(ActivationRequest.sha256 == sha256)
        )
        return result.scalars().first()

    async def generate_request_number(self, db: AsyncSession, prefix: str = "WFA-REQ") -> str:
        # Simplistic auto-incrementing logic for now
        # In a real scalable system, use a sequence or dedicated counter table
        result = await db.execute(
            select(ActivationRequest.request_number)
            .filter(ActivationRequest.request_number.like(f"{prefix}-%"))
            .order_by(desc(ActivationRequest.request_number))
            .limit(1)
        )
        last_number = result.scalars().first()
        
        if not last_number:
            next_val = 1
        else:
            try:
                next_val = int(last_number.split("-")[-1]) + 1
            except ValueError:
                next_val = 1
                
        return f"{prefix}-{next_val:06d}"

activation_request_repository = ActivationRequestRepository(ActivationRequest)
