from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.base_model import BaseModelMixin
from app.common.enums import BaseEnum

class DeviceStatus(BaseEnum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    BLOCKED = "BLOCKED"
    REVOKED = "REVOKED"
    UNKNOWN = "UNKNOWN"

class Device(BaseModelMixin, Base):
    __tablename__ = "devices"
    
    # Core Identification
    fingerprint = Column(String, unique=True, index=True, nullable=False)
    machine_guid = Column(String, nullable=True)
    public_key = Column(String, nullable=True)
    
    # Hardware/Software details
    device_name = Column(String, nullable=True)
    hostname = Column(String, nullable=True)
    username = Column(String, nullable=True)
    
    os = Column(String, nullable=True)
    os_version = Column(String, nullable=True)
    architecture = Column(String, nullable=True)
    
    cpu = Column(String, nullable=True)
    ram = Column(String, nullable=True)
    bios = Column(String, nullable=True)
    is_virtual_machine = Column(Boolean, nullable=True)
    
    # Telemetry and Location
    last_ip = Column(String, nullable=True)
    last_country = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    locale = Column(String, nullable=True)
    
    install_date = Column(DateTime(timezone=True), nullable=True)
    last_boot = Column(DateTime(timezone=True), nullable=True)
    uptime = Column(Integer, nullable=True) # Usually in seconds
    
    # LMS State
    current_build = Column(Integer, nullable=True)
    current_version = Column(String, nullable=True)
    current_channel = Column(String, nullable=True)
    
    # Lifecycle
    status = Column(String, default=DeviceStatus.UNKNOWN.value, nullable=False)
    first_seen = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    last_seen = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    trial_started = Column(DateTime(timezone=True), nullable=True)
    trial_ends = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    # Note: A device may optionally be bound to an organization (e.g. after trial/activation)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    # The active license currently governing this device
    active_license_id = Column(String, ForeignKey("licenses.id", ondelete="SET NULL"), nullable=True)
    
    organization = relationship("Organization")
    activation_requests = relationship("ActivationRequest", back_populates="device")
    # Avoid circular dependency initialization issue here, we use backref on license.py or configure explicitly
    
