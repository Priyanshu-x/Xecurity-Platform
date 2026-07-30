from app.repositories.base_repository import BaseRepository
from app.models.organization import Organization

class OrganizationRepository(BaseRepository[Organization]):
    pass

organization_repo = OrganizationRepository(Organization)
