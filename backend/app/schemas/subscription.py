from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.common.enums import SubscriptionStatus
from app.schemas.plan import ProductPlanResponse
from app.schemas.organization import OrganizationResponse

class SubscriptionBase(BaseModel):
    product_plan_id: str
    organization_id: str
    notes: Optional[str] = None
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[SubscriptionStatus] = None
    expires_at: Optional[datetime] = None

class SubscriptionResponse(SubscriptionBase):
    id: str
    status: SubscriptionStatus
    starts_at: datetime
    activated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    product_plan: Optional[ProductPlanResponse] = None
    organization: Optional[OrganizationResponse] = None

    model_config = ConfigDict(from_attributes=True)
