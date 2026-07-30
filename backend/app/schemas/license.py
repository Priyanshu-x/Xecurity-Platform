from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.common.enums import LicenseStatus

class LicenseBase(BaseModel):
    notes: Optional[str] = None

class LicenseIssue(LicenseBase):
    subscription_id: str

class LicenseRevoke(BaseModel):
    notes: Optional[str] = None

class LicenseResponse(LicenseBase):
    id: str
    deployment_id: str
    subscription_id: str
    organization_id: str
    product_id: str
    product_plan_id: str
    
    status: LicenseStatus
    
    issued_at: datetime
    expires_at: Optional[datetime] = None
    
    payload_json: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
