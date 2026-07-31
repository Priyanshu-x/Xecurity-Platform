from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.models.device import Device, DeviceStatus
from app.repositories.device import device_repository
from app.schemas.device import (
    DeviceRegistrationRequest,
    DeviceRegistrationResponse,
    DeviceHeartbeatRequest,
    DeviceHeartbeatResponse,
)
from app.repositories.release import release_repository

class DeviceService:
    async def register_device(self, db: AsyncSession, req: DeviceRegistrationRequest, client_ip: str) -> DeviceRegistrationResponse:
        device = await device_repository.get_by_fingerprint(db, req.fingerprint)
        
        now = datetime.now(timezone.utc)
        
        if not device:
            # Create new device with trial
            create_data = req.model_dump()
            create_data["last_ip"] = client_ip
            create_data["first_seen"] = now
            create_data["last_seen"] = now
            create_data["trial_started"] = now
            create_data["trial_ends"] = now + timedelta(days=30)
            create_data["status"] = DeviceStatus.TRIAL.value
            
            device = await device_repository.create(db, obj_in=create_data)
        else:
            # Update existing device basic telemetry on re-registration
            update_data = {
                "last_seen": now,
                "last_ip": client_ip,
            }
            # Update hardware fields if they changed
            for field in ["machine_guid", "os", "os_version", "architecture", "cpu", "ram", "bios"]:
                if getattr(req, field) is not None:
                    update_data[field] = getattr(req, field)
                    
            device = await device_repository.update(db, db_obj=device, obj_in=update_data)
            
        # Determine trial days remaining
        trial_days_remaining = None
        if device.status == DeviceStatus.TRIAL.value and device.trial_ends:
            # Convert naive trial_ends to UTC aware if necessary, but it should be aware
            trial_ends_utc = device.trial_ends
            if trial_ends_utc.tzinfo is None:
                trial_ends_utc = trial_ends_utc.replace(tzinfo=timezone.utc)
                
            delta = trial_ends_utc - now
            trial_days_remaining = max(0, delta.days)
            if trial_days_remaining == 0 and delta.total_seconds() < 0:
                # Trial expired
                device = await device_repository.update(db, db_obj=device, obj_in={"status": DeviceStatus.EXPIRED.value})
                trial_days_remaining = 0
                
        # Check for updates
        update_available = False
        minimum_build = None
        latest_build = None
        
        if req.current_channel:
            # Ideally we'd need a product_id. Just use a placeholder or remove it since it's hardcoded for LMS.
            # Assuming product_id 'wfa-core' or we just skip this feature for now.
            # For LMS, we might not have it cleanly available here without looking it up.
            pass
            
        return DeviceRegistrationResponse(
            device_id=device.id,
            status=DeviceStatus(device.status),
            trial_days_remaining=trial_days_remaining,
            active_license_id=device.active_license_id,
            update_available=update_available,
            minimum_build=minimum_build,
            latest_build=latest_build,
            heartbeat_interval=3600
        )

    async def process_heartbeat(self, db: AsyncSession, req: DeviceHeartbeatRequest, client_ip: str) -> DeviceHeartbeatResponse:
        device = await device_repository.get_by_fingerprint(db, req.fingerprint)
        if not device:
            # Heartbeat from unknown device
            return DeviceHeartbeatResponse(success=False, status=DeviceStatus.UNKNOWN)
            
        now = datetime.now(timezone.utc)
        update_data = {
            "last_seen": now,
            "last_ip": client_ip,
            "current_build": req.current_build
        }
        
        if req.current_version is not None:
            update_data["current_version"] = req.current_version
        if req.current_channel is not None:
            update_data["current_channel"] = req.current_channel
        if req.uptime is not None:
            update_data["uptime"] = req.uptime
        if req.os_version is not None:
            update_data["os_version"] = req.os_version
            
        device = await device_repository.update(db, db_obj=device, obj_in=update_data)
        
        # Check updates
        update_available = False
        latest_build = None
        mandatory_update = False
        
        return DeviceHeartbeatResponse(
            success=True,
            status=DeviceStatus(device.status),
            update_available=update_available,
            latest_build=latest_build,
            mandatory_update=mandatory_update
        )

device_service = DeviceService()
