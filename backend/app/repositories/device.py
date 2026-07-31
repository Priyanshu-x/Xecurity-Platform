from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.base import BaseRepository
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate

class DeviceRepository(BaseRepository[Device, DeviceCreate, DeviceUpdate]):
    def __init__(self):
        super().__init__(Device)

    async def get_by_fingerprint(self, db: AsyncSession, fingerprint: str) -> Optional[Device]:
        stmt = select(self.model).where(self.model.fingerprint == fingerprint, self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalars().first()

device_repository = DeviceRepository()
