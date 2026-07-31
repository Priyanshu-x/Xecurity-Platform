from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from typing import List, Optional

from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.repositories.organization_repository import organization_repo
from app.common.result import Result, Success, NotFoundError
from app.events.bus import EventBus
from app.events.events import DomainEvent

event_bus = EventBus()

class OrganizationService:
    async def create_organization(self, db: AsyncSession, org_in: OrganizationCreate, current_user: User, request: Request) -> Result[Organization]:
        org = await organization_repo.create(db, obj_in=org_in, created_by=current_user.id)
        
        await event_bus.publish(DomainEvent(
            entity="Organization",
            entity_id=org.id,
            action="ORGANIZATION_CREATED",
            old_value=None,
            new_value=org_in.model_dump(exclude_unset=True),
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)
        return Success(org)

    async def get_organization(self, db: AsyncSession, org_id: str) -> Result[Organization]:
        org = await organization_repo.get(db, id=org_id)
        if not org:
            return NotFoundError("Organization not found")
        return Success(org)

    async def list_organizations(self, db: AsyncSession, include_deleted: bool = False) -> Result[List[Organization]]:
        orgs = await organization_repo.get_multi(db, include_deleted=include_deleted)
        return Success(orgs)

    async def update_organization(self, db: AsyncSession, org_id: str, org_in: OrganizationUpdate, current_user: User, request: Request) -> Result[Organization]:
        org = await organization_repo.get(db, id=org_id)
        if not org:
            return NotFoundError("Organization not found")
        
        updated_org = await organization_repo.update(db, db_obj=org, obj_in=org_in, updated_by=current_user.id)
        
        await event_bus.publish(DomainEvent(
            entity="Organization",
            entity_id=updated_org.id,
            action="ORGANIZATION_UPDATED",
            old_value=None,
            new_value=org_in.model_dump(exclude_unset=True),
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)
        return Success(updated_org)

    async def delete_organization(self, db: AsyncSession, org_id: str, current_user: User, request: Request) -> Result[None]:
        org = await organization_repo.get(db, id=org_id)
        if not org:
            return NotFoundError("Organization not found")
            
        await organization_repo.soft_delete(db, id=org_id, deleted_by=current_user.id)
        
        await event_bus.publish(DomainEvent(
            entity="Organization",
            entity_id=org_id,
            action="ORGANIZATION_DELETED",
            old_value=None,
            new_value=None,
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)
        return Success(None)

organization_service = OrganizationService()
