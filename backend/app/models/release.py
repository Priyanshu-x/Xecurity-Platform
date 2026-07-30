from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base_model import BaseModelMixin
from app.common.enums import BaseEnum

class ReleaseChannel(BaseEnum):
    STABLE = "STABLE"
    BETA = "BETA"
    ALPHA = "ALPHA"
    NIGHTLY = "NIGHTLY"
    INTERNAL = "INTERNAL"

class ReleasePlatform(BaseEnum):
    WINDOWS = "WINDOWS"
    LINUX = "LINUX"
    MACOS = "MACOS"

class ReleaseArchitecture(BaseEnum):
    X64 = "x64"
    ARM64 = "ARM64"

class InstallerType(BaseEnum):
    INSTALLER = "Installer"
    PORTABLE = "Portable"
    ZIP = "ZIP"
    MSI = "MSI"
    EXE = "EXE"

class Release(BaseModelMixin, Base):
    __tablename__ = "releases"

    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    version = Column(String, nullable=False)
    version_code = Column(Integer, nullable=False)
    channel = Column(String, nullable=False) # ReleaseChannel
    platform = Column(String, nullable=False) # ReleasePlatform
    architecture = Column(String, nullable=False) # ReleaseArchitecture
    installer_type = Column(String, nullable=False) # InstallerType
    
    filename = Column(String, nullable=False)
    download_path = Column(String, nullable=False)
    sha256 = Column(String, nullable=False, index=True)
    filesize = Column(Integer, nullable=False)
    
    release_notes = Column(Text, nullable=True)
    mandatory = Column(Boolean, default=False, nullable=False)
    minimum_license_plan = Column(String, nullable=True)
    
    published_at = Column(DateTime(timezone=True), nullable=True)
    published_by = Column(String, nullable=True)
    is_latest = Column(Boolean, default=False, nullable=False, index=True)

    product = relationship("Product", backref="releases")

    __table_args__ = (
        # Prevent duplicate versions for the same platform/architecture
        UniqueConstraint("product_id", "version", "platform", "architecture", name="uq_release_version_platform_arch"),
    )
