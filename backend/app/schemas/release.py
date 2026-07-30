from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.release import ReleaseChannel, ReleasePlatform, ReleaseArchitecture, InstallerType

class ReleaseBase(BaseModel):
    product_id: str
    version: str
    version_code: int
    channel: ReleaseChannel
    platform: ReleasePlatform
    architecture: ReleaseArchitecture
    installer_type: InstallerType
    
    filename: str
    download_path: str
    sha256: str
    filesize: int
    
    release_notes: Optional[str] = None
    mandatory: bool = False
    minimum_license_plan: Optional[str] = None
    is_latest: bool = False

class ReleaseCreate(ReleaseBase):
    pass

class ReleaseUpdate(BaseModel):
    version: Optional[str] = None
    version_code: Optional[int] = None
    channel: Optional[ReleaseChannel] = None
    platform: Optional[ReleasePlatform] = None
    architecture: Optional[ReleaseArchitecture] = None
    installer_type: Optional[InstallerType] = None
    
    filename: Optional[str] = None
    download_path: Optional[str] = None
    sha256: Optional[str] = None
    filesize: Optional[int] = None
    
    release_notes: Optional[str] = None
    mandatory: Optional[bool] = None
    minimum_license_plan: Optional[str] = None
    is_latest: Optional[bool] = None

class ReleaseResponse(ReleaseBase):
    id: str
    published_at: Optional[datetime] = None
    published_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True
