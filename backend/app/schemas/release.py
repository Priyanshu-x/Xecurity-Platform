from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.release import ReleaseChannel, ReleaseStatus, ReleasePlatform, ReleaseArchitecture, ArtifactType

class ReleaseArtifactBase(BaseModel):
    platform: ReleasePlatform
    architecture: ReleaseArchitecture
    artifact_type: ArtifactType
    
    filename: str
    download_path: str
    sha256: str
    filesize: int
    
    signature: Optional[str] = None
    signature_algorithm: Optional[str] = None
    signed_at: Optional[datetime] = None

class ReleaseArtifactCreate(ReleaseArtifactBase):
    pass

class ReleaseArtifactResponse(ReleaseArtifactBase):
    id: str
    release_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReleaseBase(BaseModel):
    product_id: str
    version: str
    build_number: int
    channel: ReleaseChannel
    status: ReleaseStatus = ReleaseStatus.DRAFT
    
    release_notes: Optional[str] = None
    mandatory: bool = False
    
    minimum_license_build: Optional[int] = None
    minimum_lms_build: Optional[int] = None
    is_latest: bool = False

class ReleaseCreate(ReleaseBase):
    artifacts: List[ReleaseArtifactCreate] = []

class ReleaseUpdate(BaseModel):
    version: Optional[str] = None
    build_number: Optional[int] = None
    channel: Optional[ReleaseChannel] = None
    status: Optional[ReleaseStatus] = None
    
    release_notes: Optional[str] = None
    mandatory: Optional[bool] = None
    
    minimum_license_build: Optional[int] = None
    minimum_lms_build: Optional[int] = None
    is_latest: Optional[bool] = None

class ReleaseResponse(ReleaseBase):
    id: str
    published_at: Optional[datetime] = None
    published_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    artifacts: List[ReleaseArtifactResponse] = []

    class Config:
        from_attributes = True

class CheckUpdateResponse(BaseModel):
    update_available: bool
    mandatory: bool = False
    reason: Optional[str] = None
    current_build: int
    latest_build: Optional[int] = None
    release: Optional[ReleaseResponse] = None
