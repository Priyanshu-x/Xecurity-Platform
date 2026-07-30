from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.organization import Organization
from pydantic import BaseModel

class OrganizationCreate(BaseModel):
    name: str

class OrganizationUpdate(BaseModel):
    name: str

class OrganizationRepository(BaseRepository[Organization, OrganizationCreate, OrganizationUpdate]):
    pass

organization_repository = OrganizationRepository(Organization)
