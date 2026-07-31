from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.activation_request import ActivationRequestType, ActivationRequestStatus
from app.schemas.base import BaseResponse

class ActivationRequestEventResponse(BaseModel):
    id: str
    request_id: str
    status_from: Optional[str] = None
    status_to: str
    actor_id: Optional[str] = None
    timestamp: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class ActivationRequestBase(BaseModel):
    # We do not expose everything for creation, creation is done via upload parser
    pass

class ActivationRequestResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    
    request_number: str
    device_id: Optional[str] = None
    request_type: str
    status: str
    
    # Device snapshot
    fingerprint: str
    hostname: Optional[str] = None
    username: Optional[str] = None
    os: Optional[str] = None
    os_version: Optional[str] = None
    architecture: Optional[str] = None
    cpu: Optional[str] = None
    ram: Optional[str] = None
    bios: Optional[str] = None
    mac_address: Optional[str] = None
    windows_sid: Optional[str] = None
    current_build: Optional[int] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    hardware_tokens: Optional[Any] = None

    # Storage
    original_filename: Optional[str] = None
    sha256: str
    size: Optional[int] = None

    # Audit
    reject_reason: Optional[str] = None
    admin_notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    generated_license_id: Optional[str] = None

    events: List[ActivationRequestEventResponse] = []

    class Config:
        from_attributes = True

class ActivationRequestReject(BaseModel):
    reason: str = Field(..., min_length=1, description="Mandatory reason for rejection")
    notes: Optional[str] = None

class LicenseGenerationConfig(BaseModel):
    organization_id: str
    product_id: str
    plan_id: Optional[str] = None
    license_type: str = "TRIAL" # Subscription, Perpetual, etc.
    validity_months: Optional[int] = None # e.g. 3, 6, 12. If None, it might be lifetime
    capabilities_override: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
