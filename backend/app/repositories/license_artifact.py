from app.models.license_artifact import LicenseArtifact
from app.repositories.base import BaseRepository
from pydantic import BaseModel

class LicenseArtifactBase(BaseModel):
    pass

class LicenseArtifactRepository(BaseRepository[LicenseArtifact, LicenseArtifactBase, LicenseArtifactBase]):
    pass

license_artifact_repository = LicenseArtifactRepository(LicenseArtifact)
