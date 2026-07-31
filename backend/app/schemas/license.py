from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.common.enums import LicenseStatus
from app.schemas.organization import OrganizationResponse
from app.schemas.product import ProductResponse
from app.schemas.subscription import SubscriptionResponse
from app.schemas.deployment import DeploymentResponse

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

    organization: Optional[OrganizationResponse] = None
    product: Optional[ProductResponse] = None
    subscription: Optional[SubscriptionResponse] = None
    deployment: Optional[DeploymentResponse] = None

    model_config = ConfigDict(from_attributes=True)
