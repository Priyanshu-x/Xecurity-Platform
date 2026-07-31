import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class LicenseArtifact(Base):
    __tablename__ = "license_artifacts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    license_id = Column(String, ForeignKey("licenses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    sha256 = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    license = relationship("License", back_populates="artifacts")
