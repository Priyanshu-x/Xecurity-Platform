from pydantic import BaseModel
from typing import Optional, Dict, Any, TypeVar

class BaseEvent(BaseModel):
    actor: Optional[str] = None # user_id
    organization_id: Optional[str] = None
    request_id: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DomainEvent(BaseEvent):
    entity: str
    entity_id: str
    action: str
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    success: bool = True
    duration_ms: Optional[int] = None
