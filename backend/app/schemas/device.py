from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.common.enums import BaseEnum
from app.models.device import DeviceStatus

# -------------------------------------
# Admin / Management Schemas
# -------------------------------------

class DeviceBase(BaseModel):
    fingerprint: str
    machine_guid: Optional[str] = None
    public_key: Optional[str] = None
    
    device_name: Optional[str] = None
    hostname: Optional[str] = None
    username: Optional[str] = None
    
    os: Optional[str] = None
    os_version: Optional[str] = None
    architecture: Optional[str] = None
    
    cpu: Optional[str] = None
    ram: Optional[str] = None
    bios: Optional[str] = None
    is_virtual_machine: Optional[bool] = None
    
    last_ip: Optional[str] = None
    last_country: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    
    install_date: Optional[datetime] = None
    last_boot: Optional[datetime] = None
    uptime: Optional[int] = None
    
    current_build: Optional[int] = None
    current_version: Optional[str] = None
    current_channel: Optional[str] = None

class DeviceCreate(DeviceBase):
    organization_id: Optional[str] = None
    active_license_id: Optional[str] = None
    status: DeviceStatus = DeviceStatus.UNKNOWN

class DeviceUpdate(BaseModel):
    organization_id: Optional[str] = None
    active_license_id: Optional[str] = None
    status: Optional[DeviceStatus] = None
    notes: Optional[str] = None

class DeviceResponse(DeviceBase):
    id: str
    organization_id: Optional[str] = None
    active_license_id: Optional[str] = None
    
    status: DeviceStatus
    first_seen: datetime
    last_seen: datetime
    
    trial_started: Optional[datetime] = None
    trial_ends: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# -------------------------------------
# Client Registration / Telemetry Schemas
# -------------------------------------

class DeviceRegistrationRequest(BaseModel):
    fingerprint: str = Field(..., description="Unique hardware hash")
    machine_guid: Optional[str] = None
    public_key: Optional[str] = None
    
    device_name: Optional[str] = None
    hostname: Optional[str] = None
    username: Optional[str] = None
    
    os: Optional[str] = None
    os_version: Optional[str] = None
    architecture: Optional[str] = None
    
    cpu: Optional[str] = None
    ram: Optional[str] = None
    bios: Optional[str] = None
    is_virtual_machine: Optional[bool] = None
    
    timezone: Optional[str] = None
    locale: Optional[str] = None
    
    current_build: Optional[int] = None
    current_version: Optional[str] = None
    current_channel: Optional[str] = None

class DeviceRegistrationResponse(BaseModel):
    device_id: str
    status: DeviceStatus
    trial_days_remaining: Optional[int] = None
    active_license_id: Optional[str] = None
    update_available: bool = False
    minimum_build: Optional[int] = None
    latest_build: Optional[int] = None
    heartbeat_interval: int = 3600

class DeviceHeartbeatRequest(BaseModel):
    fingerprint: str
    current_build: int
    current_version: Optional[str] = None
    current_channel: Optional[str] = None
    uptime: Optional[int] = None
    os_version: Optional[str] = None

class DeviceHeartbeatResponse(BaseModel):
    success: bool
    status: DeviceStatus
    update_available: bool = False
    latest_build: Optional[int] = None
    mandatory_update: bool = False
