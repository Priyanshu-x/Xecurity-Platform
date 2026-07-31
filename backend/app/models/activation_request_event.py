import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class ActivationRequestEvent(Base):
    __tablename__ = "activation_request_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    request_id = Column(String, ForeignKey("activation_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status_from = Column(String, nullable=True)
    status_to = Column(String, nullable=False)
    
    actor_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # None means System
    
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    notes = Column(String, nullable=True)

    request = relationship("ActivationRequest", back_populates="events")
    actor = relationship("User")
