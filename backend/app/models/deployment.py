from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base_model import BaseModelMixin
from app.common.enums import DeploymentEnvironment, DeploymentStatus

class Deployment(Base, BaseModelMixin):
    __tablename__ = "deployments"

    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String, nullable=False)
    environment = Column(Enum(DeploymentEnvironment), default=DeploymentEnvironment.PRODUCTION, nullable=False)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.ACTIVE, nullable=False)
    
    current_release_version = Column(String, nullable=True)
    last_ping_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="deployments")
    product = relationship("Product", back_populates="deployments")
