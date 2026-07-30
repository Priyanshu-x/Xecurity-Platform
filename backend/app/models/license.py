import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.common.enums import LicenseStatus

class License(Base):
    __tablename__ = "licenses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id", ondelete="RESTRICT"), nullable=False, index=True)
    deployment_id = Column(String, ForeignKey("deployments.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_plan_id = Column(String, ForeignKey("product_plans.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    status = Column(Enum(LicenseStatus), default=LicenseStatus.ACTIVE, nullable=False)
    
    issued_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    payload_json = Column(JSON, nullable=False)
    notes = Column(String, nullable=True)

    # Relationships
    subscription = relationship("Subscription", backref="licenses")
    deployment = relationship("Deployment", backref="licenses")
    organization = relationship("Organization", backref="licenses")
    product = relationship("Product", backref="licenses")
    product_plan = relationship("ProductPlan", backref="licenses")
