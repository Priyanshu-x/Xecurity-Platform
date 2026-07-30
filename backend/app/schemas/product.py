from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.product import ProductStatus

class ProductBase(BaseModel):
    name: str
    slug: str
    short_name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    website: Optional[str] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    status: ProductStatus = ProductStatus.BETA

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    short_name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    website: Optional[str] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    status: Optional[ProductStatus] = None

class ProductResponse(ProductBase):
    id: str
    current_stable_release_id: Optional[str] = None
    latest_release_id: Optional[str] = None
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
