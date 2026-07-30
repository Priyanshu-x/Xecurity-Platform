import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    request_id = Column(String, nullable=True, index=True)
    
    actor = Column(String, nullable=True, index=True) # user_id
    organization_id = Column(String, nullable=True, index=True)
    
    entity = Column(String, nullable=False, index=True) # resource_type
    entity_id = Column(String, nullable=True, index=True) # resource_id
    action = Column(String, nullable=False, index=True)
    
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    
    ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    duration_ms = Column(Integer, nullable=True)
