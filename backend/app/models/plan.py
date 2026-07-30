from sqlalchemy import Column, String, Text, Integer, ForeignKey, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base_model import BaseModelMixin
from app.common.enums import PlanTier, PlanStatus

class ProductPlan(BaseModelMixin, Base):
    __tablename__ = "product_plans"

    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    tier = Column(SQLEnum(PlanTier), nullable=False, default=PlanTier.COMMUNITY)
    status = Column(SQLEnum(PlanStatus), nullable=False, default=PlanStatus.ACTIVE)
    
    max_devices = Column(Integer, nullable=True) # Null means unlimited
    max_users = Column(Integer, nullable=True) # Null means unlimited
    trial_days = Column(Integer, nullable=True, default=0)

    # Relationships
    product = relationship("Product", backref="plans")
    capabilities = relationship("ProductPlanCapability", back_populates="plan", cascade="all, delete-orphan")

class ProductPlanCapability(BaseModelMixin, Base):
    __tablename__ = "product_plan_capabilities"
    
    plan_id = Column(String(36), ForeignKey("product_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    capability_id = Column(String(36), ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    plan = relationship("ProductPlan", back_populates="capabilities")
    capability = relationship("Capability")

    __table_args__ = (
        UniqueConstraint('plan_id', 'capability_id', name='uq_plan_capability'),
    )
