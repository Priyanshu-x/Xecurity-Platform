import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.common.enums import BaseEnum
from app.models.base_model import BaseModelMixin

class ActivationRequestType(BaseEnum):
    ACTIVATION = "ACTIVATION"
    RENEWAL = "RENEWAL"
    TRANSFER = "TRANSFER"
    UPGRADE = "UPGRADE"
    RECOVERY = "RECOVERY"
    EMERGENCY = "EMERGENCY"

class ActivationRequestStatus(BaseEnum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    LICENSE_GENERATED = "LICENSE_GENERATED"
    DOWNLOADED = "DOWNLOADED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class ActivationRequest(BaseModelMixin, Base):
    __tablename__ = "activation_requests"

    # Core
    request_number = Column(String, unique=True, index=True, nullable=False) # e.g. WFA-REQ-000001
    device_id = Column(String, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    request_type = Column(String, default=ActivationRequestType.ACTIVATION.value, nullable=False)
    status = Column(String, default=ActivationRequestStatus.PENDING.value, nullable=False)
    
    # Device Snapshot (Frozen at request time)
    fingerprint = Column(String, nullable=False)
    hostname = Column(String, nullable=True)
    username = Column(String, nullable=True)
    os = Column(String, nullable=True)
    os_version = Column(String, nullable=True)
    architecture = Column(String, nullable=True)
    cpu = Column(String, nullable=True)
    ram = Column(String, nullable=True)
    bios = Column(String, nullable=True)
    mac_address = Column(String, nullable=True)
    windows_sid = Column(String, nullable=True)
    current_build = Column(Integer, nullable=True)
    timezone = Column(String, nullable=True)
    locale = Column(String, nullable=True)
    hardware_tokens = Column(JSON, nullable=True)

    # File Storage
    original_filename = Column(String, nullable=True)
    storage_path = Column(String, nullable=True)
    sha256 = Column(String, nullable=False)
    size = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)

    # Audit & Approval
    reject_reason = Column(String, nullable=True)
    admin_notes = Column(String, nullable=True)
    
    approved_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    rejected_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    generated_license_id = Column(String, ForeignKey("licenses.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    device = relationship("Device", back_populates="activation_requests")
    events = relationship("ActivationRequestEvent", back_populates="request", cascade="all, delete-orphan")
    generated_license = relationship("License")
