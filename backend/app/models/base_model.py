import uuid
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_mixin

@declarative_mixin
class BaseModelMixin:
    """Base mixin for all models with UUID, timestamps, soft-delete, and audit tracing."""
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)

@declarative_mixin
class TenantModelMixin(BaseModelMixin):
    """Base mixin for tenant-specific models (tied to an Organization)."""
    # Note: organization_id is indexed for fast tenant-based filtering
    organization_id = Column(String, index=True, nullable=False)
