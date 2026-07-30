from sqlalchemy import Column, String
from app.core.database import Base
from app.models.base_model import BaseModelMixin

class Organization(Base, BaseModelMixin):
    __tablename__ = "organizations"

    name = Column(String, index=True, nullable=False)
