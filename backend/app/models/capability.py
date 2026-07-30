import uuid
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base_model import BaseModelMixin

class Capability(BaseModelMixin, Base):
    __tablename__ = "capabilities"

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Products associated with this capability
    product_links = relationship("ProductCapability", back_populates="capability", cascade="all, delete-orphan")

class ProductCapability(BaseModelMixin, Base):
    __tablename__ = "product_capabilities"
    
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    capability_id = Column(String(36), ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False, index=True)

    # Allow mapping capability to specific product versions if needed in future
    # For now, it's just a mapping table with its own ID (from BaseModelMixin)
    
    product = relationship("Product", backref="capability_links")
    capability = relationship("Capability", back_populates="product_links")

    __table_args__ = (
        UniqueConstraint('product_id', 'capability_id', name='uq_product_capability'),
    )
