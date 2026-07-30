from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.models.capability import Capability
from app.models.user import User
from app.schemas.capability import CapabilityCreate, CapabilityUpdate
from app.repositories.capability import capability_repository
from app.repositories.product import product_repository
from app.common.result import Result, Success, NotFoundError, ConflictError
from app.events.bus import EventBus
from app.events.events import DomainEvent


event_bus = EventBus()

class CapabilityService:
    async def get_capability(self, db: AsyncSession, capability_id: str) -> Result[Capability]:
        capability = await capability_repository.get(db, capability_id)
        if not capability:
            return NotFoundError("Capability not found")
        return Success(capability)

    async def get_all_capabilities(self, db: AsyncSession) -> Result[List[Capability]]:
        capabilities = await capability_repository.get_multi(db, limit=100)
        return Success(capabilities)

    async def create_capability(
        self, db: AsyncSession, capability_in: CapabilityCreate, current_user: User, request: Request
    ) -> Result[Capability]:
        existing = await capability_repository.get_by_slug(db, capability_in.slug)
        if existing:
            return ConflictError("Capability with this slug already exists")

        capability = await capability_repository.create(db, obj_in=capability_in)
        
        await event_bus.publish(DomainEvent(
            entity="Capability",
            entity_id=capability.id,
            action="CAPABILITY_CREATED",
            old_value=None,
            new_value=capability_in.model_dump(),
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)
        
        return Success(capability)

    async def update_capability(
        self, db: AsyncSession, capability_id: str, capability_in: CapabilityUpdate, current_user: User, request: Request
    ) -> Result[Capability]:
        capability = await capability_repository.get(db, capability_id)
        if not capability:
            return NotFoundError("Capability not found")

        if capability_in.slug and capability_in.slug != capability.slug:
            existing = await capability_repository.get_by_slug(db, capability_in.slug)
            if existing:
                return ConflictError("Capability with this slug already exists")
                
        old_value = {
            "name": capability.name,
            "slug": capability.slug,
            "description": capability.description,
            "is_active": capability.is_active
        }

        updated_capability = await capability_repository.update(db, db_obj=capability, obj_in=capability_in)

        await event_bus.publish(DomainEvent(
            entity="Capability",
            entity_id=capability.id,
            action="CAPABILITY_UPDATED",
            old_value=old_value,
            new_value=capability_in.model_dump(exclude_unset=True),
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)

        return Success(updated_capability)
        
    async def delete_capability(
        self, db: AsyncSession, capability_id: str, current_user: User, request: Request
    ) -> Result[None]:
        capability = await capability_repository.get(db, capability_id)
        if not capability:
            return NotFoundError("Capability not found")
            
        await capability_repository.soft_delete(db, id=capability_id)
        
        await event_bus.publish(DomainEvent(
            entity="Capability",
            entity_id=capability.id,
            action="CAPABILITY_DELETED",
            old_value=None,
            new_value=None,
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)
        
        return Success(None)

    async def link_capability_to_product(
        self, db: AsyncSession, capability_id: str, product_id: str, current_user: User, request: Request
    ) -> Result[None]:
        capability = await capability_repository.get(db, capability_id)
        if not capability:
            return NotFoundError("Capability not found")
            
        product = await product_repository.get(db, product_id)
        if not product:
            return NotFoundError("Product not found")
            
        success = await capability_repository.link_to_product(db, capability_id, product_id)
        if not success:
            return ConflictError("Capability is already linked to this product")
            
        await event_bus.publish(DomainEvent(
            entity="ProductCapability",
            entity_id=product_id,
            action="CAPABILITY_LINKED_TO_PRODUCT",
            old_value=None,
            new_value={"capability_id": capability_id, "product_id": product_id},
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)
        
        return Success(None)
        
    async def unlink_capability_from_product(
        self, db: AsyncSession, capability_id: str, product_id: str, current_user: User, request: Request
    ) -> Result[None]:
        capability = await capability_repository.get(db, capability_id)
        if not capability:
            return NotFoundError("Capability not found")
            
        product = await product_repository.get(db, product_id)
        if not product:
            return NotFoundError("Product not found")
            
        success = await capability_repository.unlink_from_product(db, capability_id, product_id)
        if not success:
            return NotFoundError("Capability is not linked to this product")
            
        await event_bus.publish(DomainEvent(
            entity="ProductCapability",
            entity_id=product_id,
            action="CAPABILITY_UNLINKED_FROM_PRODUCT",
            old_value={"capability_id": capability_id, "product_id": product_id},
            new_value=None,
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)
        
        return Success(None)

    async def get_product_capabilities(
        self, db: AsyncSession, product_id: str
    ) -> Result[List[Capability]]:
        product = await product_repository.get(db, product_id)
        if not product:
            return NotFoundError("Product not found")
            
        capabilities = await capability_repository.get_capabilities_for_product(db, product_id)
        return Success(capabilities)

capability_service = CapabilityService()
