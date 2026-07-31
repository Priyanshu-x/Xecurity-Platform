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

class ReleaseStatus(BaseEnum):
    DRAFT = "DRAFT"
    TESTING = "TESTING"
    RELEASE_CANDIDATE = "RELEASE_CANDIDATE"
    PUBLISHED = "PUBLISHED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"

class ReleasePlatform(BaseEnum):
    WINDOWS = "WINDOWS"
    LINUX = "LINUX"
    MACOS = "MACOS"

class ReleaseArchitecture(BaseEnum):
    X64 = "x64"
    ARM64 = "ARM64"
    X86 = "x86"

class ArtifactType(BaseEnum):
    EXE = "EXE"
    ZIP = "ZIP"
    MSI = "MSI"
    PKG = "PKG"
    DEB = "DEB"
    RPM = "RPM"
    DOCS = "DOCS"
    SYMBOLS = "SYMBOLS"

class Release(BaseModelMixin, Base):
    __tablename__ = "releases"

    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    version = Column(String, nullable=False)
    build_number = Column(Integer, nullable=False)
    channel = Column(String, nullable=False) # ReleaseChannel
    status = Column(String, default=ReleaseStatus.DRAFT.value, nullable=False) # ReleaseStatus
    
    release_notes = Column(Text, nullable=True)
    mandatory = Column(Boolean, default=False, nullable=False)
    
    minimum_license_build = Column(Integer, nullable=True)
    minimum_lms_build = Column(Integer, nullable=True)
    
    published_at = Column(DateTime(timezone=True), nullable=True)
    published_by = Column(String, nullable=True)
    is_latest = Column(Boolean, default=False, nullable=False, index=True)

    product = relationship("Product", backref="releases")
    artifacts = relationship("ReleaseArtifact", backref="release", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("product_id", "version", "build_number", name="uq_release_version_build"),
    )

class ReleaseArtifact(BaseModelMixin, Base):
    __tablename__ = "release_artifacts"

    release_id = Column(String, ForeignKey("releases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    platform = Column(String, nullable=False) # ReleasePlatform
    architecture = Column(String, nullable=False) # ReleaseArchitecture
    artifact_type = Column(String, nullable=False) # ArtifactType
    
    filename = Column(String, nullable=False)
    download_path = Column(String, nullable=False)
    sha256 = Column(String, nullable=False, index=True)
    filesize = Column(Integer, nullable=False)

    # Placeholders for future cryptographic signatures
    signature = Column(String, nullable=True)
    signature_algorithm = Column(String, nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("release_id", "platform", "architecture", "artifact_type", name="uq_release_artifact"),
    )
