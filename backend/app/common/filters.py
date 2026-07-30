from typing import Optional, List, Any
from pydantic import BaseModel, Field
from app.common.enums import SortOrder

class BaseFilters(BaseModel):
    search: Optional[str] = Field(None, description="Search query string")
    sort_by: Optional[str] = Field("created_at", description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Sort order (asc/desc)")
    include_deleted: bool = Field(False, description="Include soft-deleted records")
