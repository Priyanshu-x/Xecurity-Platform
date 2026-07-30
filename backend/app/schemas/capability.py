from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class CapabilityBase(BaseModel):
    name: str = Field(..., description="The human-readable name of the capability")
    slug: str = Field(..., description="A URL-friendly, unique identifier")
    description: Optional[str] = Field(None, description="Detailed description of what this capability grants")
    is_active: bool = Field(True, description="Whether this capability is currently active")

class CapabilityCreate(CapabilityBase):
    pass

class CapabilityUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class CapabilityResponse(CapabilityBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductCapabilityLink(BaseModel):
    product_id: str
    capability_id: str

    model_config = ConfigDict(from_attributes=True)
