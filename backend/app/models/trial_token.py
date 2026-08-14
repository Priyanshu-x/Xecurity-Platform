from sqlalchemy import Column, String, DateTime, Boolean
from app.models.base_model import BaseModelMixin
from app.core.database import Base

class TrialToken(BaseModelMixin, Base):
    __tablename__ = "trial_tokens"

    token_string = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
