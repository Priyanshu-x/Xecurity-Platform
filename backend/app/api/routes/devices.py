from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db_session
from app.schemas.device import DeviceResponse, DeviceUpdate
from app.repositories.device import device_repository
from app.models.user import User, UserRole
from app.api.deps import RoleChecker

require_owner = RoleChecker([UserRole.OWNER])

router = APIRouter(prefix="/devices", tags=["Admin Devices"])

@router.get("/", response_model=List[DeviceResponse])
async def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    organization_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_owner)
):
    """List all registered devices. Admins can view all, or filter by organization."""
    if organization_id:
        items, _ = await device_repository.paginate(db, page=(skip // limit) + 1, size=limit, organization_id=organization_id)
    else:
        items, _ = await device_repository.paginate(db, page=(skip // limit) + 1, size=limit)
        
    return items

@router.get("/{id}", response_model=DeviceResponse)
async def get_device(id: str, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(require_owner)):
    """Get device details."""
    device = await device_repository.get(db, id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.patch("/{id}", response_model=DeviceResponse)
async def update_device(id: str, req: DeviceUpdate, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(require_owner)):
    """Update device details (e.g. status, active_license_id)."""
    device = await device_repository.get(db, id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    return await device_repository.update(db, db_obj=device, obj_in=req.model_dump(exclude_unset=True))

@router.delete("/{fingerprint}")
async def delete_device(fingerprint: str, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(require_owner)):
    """Delete a device by machine fingerprint."""
    device = await device_repository.get_by_fingerprint(db, fingerprint)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    await device_repository.remove(db, id=device.id)
    return {"success": True, "message": "Device deleted successfully"}

from app.schemas.device import DeviceHeartbeatPayload, DeviceHeartbeatResponse
from app.models.device import DeviceStatus
from sqlalchemy.sql import func

@router.post("/heartbeat", response_model=DeviceHeartbeatResponse)
async def device_heartbeat(payload: DeviceHeartbeatPayload, db: AsyncSession = Depends(get_db_session)):
    """Receive a heartbeat from a device, updating its online status and metadata."""
    device = await device_repository.get_by_fingerprint(db, payload.machine_fingerprint)
    
    STATUS_MAP = {
        "TRIAL_ACTIVE": DeviceStatus.TRIAL,
        "COMMUNITY_TRIAL": DeviceStatus.TRIAL,
        "TRIAL": DeviceStatus.TRIAL,
        "GRACE_PERIOD": DeviceStatus.TRIAL,
        "ACTIVATED": DeviceStatus.ACTIVE,
        "ACTIVE": DeviceStatus.ACTIVE,
        "EXPIRED": DeviceStatus.EXPIRED,
        "CLOCK_TAMPERED": DeviceStatus.EXPIRED,
        "BLOCKED": DeviceStatus.BLOCKED,
        "REVOKED": DeviceStatus.REVOKED,
    }

    status_enum = DeviceStatus.UNKNOWN
    if payload.license_state:
        raw_state = payload.license_state.upper()
        if raw_state in STATUS_MAP:
            status_enum = STATUS_MAP[raw_state]
        else:
            try:
                status_enum = DeviceStatus(raw_state)
            except ValueError:
                pass

    if not device:
        # Create new device
        from app.schemas.device import DeviceCreate
        device_in = DeviceCreate(
            fingerprint=payload.machine_fingerprint,
            hostname=payload.hostname,
            username=payload.username,
            os=payload.os,
            os_version=payload.os_version,
            current_version=payload.app_version,
            status=status_enum,
        )
        device = await device_repository.create(db, obj_in=device_in)
    else:
        # Update existing device
        device.last_seen = func.now()
        if payload.hostname: device.hostname = payload.hostname
        if payload.username: device.username = payload.username
        if payload.os: device.os = payload.os
        if payload.os_version: device.os_version = payload.os_version
        if payload.app_version: device.current_version = payload.app_version
        if payload.license_state: device.status = status_enum.value
        
        await db.commit()
        await db.refresh(device)
        
    return DeviceHeartbeatResponse(
        success=True,
        status=DeviceStatus(device.status) if isinstance(device.status, str) else device.status
    )
