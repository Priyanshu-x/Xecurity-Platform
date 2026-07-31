from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.common.enums import DeploymentEnvironment, DeploymentStatus
from app.schemas.organization import OrganizationResponse
from app.schemas.product import ProductResponse

class DeploymentBase(BaseModel):
    name: str
    environment: Optional[DeploymentEnvironment] = DeploymentEnvironment.PRODUCTION
    current_release_version: Optional[str] = None

class DeploymentCreate(DeploymentBase):
    organization_id: str
    product_id: str

class DeploymentUpdate(BaseModel):
    name: Optional[str] = None
    environment: Optional[DeploymentEnvironment] = None
    status: Optional[DeploymentStatus] = None
    current_release_version: Optional[str] = None

class DeploymentResponse(DeploymentBase):
    id: str
    organization_id: str
    product_id: str
    status: DeploymentStatus
    last_ping_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    organization: Optional[OrganizationResponse] = None
    product: Optional[ProductResponse] = None

    model_config = ConfigDict(from_attributes=True)
