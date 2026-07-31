from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db_session
from app.schemas.device import DeviceResponse, DeviceUpdate
from app.repositories.device import device_repository

router = APIRouter(prefix="/devices", tags=["Admin Devices"])

@router.get("/", response_model=List[DeviceResponse])
async def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    organization_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """List all registered devices. Admins can view all, or filter by organization."""
    if organization_id:
        items, _ = await device_repository.paginate(db, page=(skip // limit) + 1, size=limit, organization_id=organization_id)
    else:
        items, _ = await device_repository.paginate(db, page=(skip // limit) + 1, size=limit)
        
    return items

@router.get("/{id}", response_model=DeviceResponse)
async def get_device(id: str, db: AsyncSession = Depends(get_db_session)):
    """Get device details."""
    device = await device_repository.get(db, id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.patch("/{id}", response_model=DeviceResponse)
async def update_device(id: str, req: DeviceUpdate, db: AsyncSession = Depends(get_db_session)):
    """Update device details (e.g. status, active_license_id)."""
    device = await device_repository.get(db, id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    return await device_repository.update(db, db_obj=device, obj_in=req.model_dump(exclude_unset=True))

