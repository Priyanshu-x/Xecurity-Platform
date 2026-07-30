import enum
from sqlalchemy import Column, String, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base_model import BaseModelMixin

class ProductStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BETA = "BETA"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"

class Product(Base, BaseModelMixin):
    __tablename__ = "products"

    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    short_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    category = Column(String, nullable=True)
    
    current_stable_release_id = Column(String, nullable=True)
    latest_release_id = Column(String, nullable=True)
    
    website = Column(String, nullable=True)
    repository_url = Column(String, nullable=True)
    documentation_url = Column(String, nullable=True)
    
    status = Column(Enum(ProductStatus), default=ProductStatus.BETA, nullable=False)
    
    plans = relationship("ProductPlan", back_populates="product", cascade="all, delete-orphan")
