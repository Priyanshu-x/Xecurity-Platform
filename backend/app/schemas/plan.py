from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.common.enums import PlanTier, PlanStatus
from app.schemas.capability import CapabilityResponse

class ProductPlanBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    tier: Optional[PlanTier] = Field(default=PlanTier.COMMUNITY)
    status: PlanStatus = Field(default=PlanStatus.ACTIVE)
    max_devices: Optional[int] = Field(default=None, description="Null means unlimited")
    max_users: Optional[int] = Field(default=None, description="Null means unlimited")
    trial_days: Optional[int] = Field(default=0, ge=0)
    duration_months: Optional[int] = Field(default=12, description="Duration in months, e.g. 1, 3, 6, 12, 24")

class ProductPlanCreate(ProductPlanBase):
    slug: str = Field(..., max_length=255)
    product_id: str = Field(..., max_length=36)

class ProductPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    tier: Optional[PlanTier] = None
    status: Optional[PlanStatus] = None
    max_devices: Optional[int] = None
    max_users: Optional[int] = None
    trial_days: Optional[int] = Field(None, ge=0)
    duration_months: Optional[int] = None

class ProductPlanResponse(ProductPlanBase):
    id: str
    slug: str
    product_id: str
    created_at: datetime
    updated_at: datetime
    
    # We might want to embed capabilities when returning a plan
    capabilities: Optional[List[CapabilityResponse]] = []

    model_config = ConfigDict(from_attributes=True)
