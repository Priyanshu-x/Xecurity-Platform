from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from typing import List, Optional

from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.repositories.organization_repository import organization_repo
from app.common.result import Result
from app.services.event_service import event_service
from app.models.audit import ActionType, EntityType

class OrganizationService:
    async def create_organization(self, db: AsyncSession, org_in: OrganizationCreate, current_user: User, request: Request) -> Result[Organization]:
        org = await organization_repo.create(db, obj_in=org_in, created_by=current_user.id)
        
        await event_service.log_event(
            db=db,
            action=ActionType.CREATE,
            entity_type=EntityType.ORGANIZATION,
            entity_id=org.id,
            actor_id=current_user.id,
            organization_id=org.id, # Organization belongs to itself essentially
            request=request,
            details={"name": org.name}
        )
        return Result.ok(org)

    async def get_organization(self, db: AsyncSession, org_id: str) -> Result[Organization]:
        org = await organization_repo.get(db, id=org_id)
        if not org:
            return Result.fail("Organization not found", status_code=404)
        return Result.ok(org)

    async def list_organizations(self, db: AsyncSession, include_deleted: bool = False) -> Result[List[Organization]]:
        orgs = await organization_repo.get_multi(db, include_deleted=include_deleted)
        return Result.ok(orgs)

    async def update_organization(self, db: AsyncSession, org_id: str, org_in: OrganizationUpdate, current_user: User, request: Request) -> Result[Organization]:
        org = await organization_repo.get(db, id=org_id)
        if not org:
            return Result.fail("Organization not found", status_code=404)
        
        updated_org = await organization_repo.update(db, db_obj=org, obj_in=org_in, updated_by=current_user.id)
        
        await event_service.log_event(
            db=db,
            action=ActionType.UPDATE,
            entity_type=EntityType.ORGANIZATION,
            entity_id=updated_org.id,
            actor_id=current_user.id,
            organization_id=updated_org.id,
            request=request,
            details=org_in.model_dump(exclude_unset=True)
        )
        return Result.ok(updated_org)

    async def delete_organization(self, db: AsyncSession, org_id: str, current_user: User, request: Request) -> Result[None]:
        org = await organization_repo.get(db, id=org_id)
        if not org:
            return Result.fail("Organization not found", status_code=404)
            
        await organization_repo.soft_delete(db, id=org_id, deleted_by=current_user.id)
        
        await event_service.log_event(
            db=db,
            action=ActionType.DELETE,
            entity_type=EntityType.ORGANIZATION,
            entity_id=org_id,
            actor_id=current_user.id,
            organization_id=org_id,
            request=request
        )
        return Result.ok(None)

organization_service = OrganizationService()
