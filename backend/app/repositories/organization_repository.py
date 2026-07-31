from app.repositories.base import BaseRepository
from app.models.organization import Organization
from pydantic import BaseModel

class OrganizationRepository(BaseRepository[Organization, BaseModel, BaseModel]):
    pass

organization_repo = OrganizationRepository(Organization)
