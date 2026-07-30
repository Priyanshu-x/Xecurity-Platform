from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base_model import BaseModelMixin

class Organization(Base, BaseModelMixin):
    __tablename__ = "organizations"

    name = Column(String, index=True, nullable=False)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="organization", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="organization", cascade="all, delete-orphan")
