from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class TrialTokenBase(BaseModel):
    token_string: str
    expires_at: datetime
    is_active: bool = True

class TrialTokenCreate(TrialTokenBase):
    pass

class TrialTokenUpdate(BaseModel):
    is_active: Optional[bool] = None

class TrialTokenResponse(TrialTokenBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ManifestResponse(BaseModel):
    version: int
    active: bool
    token: str
    expires_at: Optional[datetime]
