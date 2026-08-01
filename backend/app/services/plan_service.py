import uuid
from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect
from fastapi import Request

from app.common.result import Result, Success, NotFoundError, ConflictError
from app.models.user import User
from app.models.plan import ProductPlan, ProductPlanCapability
from app.repositories.plan import plan_repository
from app.repositories.product import product_repository
from app.repositories.capability import capability_repository
from app.schemas.plan import ProductPlanCreate, ProductPlanUpdate, ProductPlanResponse
from app.events.bus import EventBus
from app.events.events import DomainEvent

event_bus = EventBus()

class PlanService:
    async def create_plan(
        self, db: AsyncSession, plan_in: ProductPlanCreate, current_user: User, request: Request
    ) -> Result[ProductPlanResponse]:
        
        # Validate product exists
        product = await product_repository.get(db, id=plan_in.product_id)
        if not product:
            return NotFoundError(f"Product with ID {plan_in.product_id} not found")

        # Validate slug uniqueness globally or per product? The model says unique=True globally
        existing = await plan_repository.get_by_slug(db, slug=plan_in.slug)
        if existing:
            return ConflictError(f"Plan with slug '{plan_in.slug}' already exists")

        # Create
        plan = ProductPlan(**plan_in.model_dump())
        plan.id = str(uuid.uuid4())
        
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        await event_bus.publish(DomainEvent(
            entity="ProductPlan",
            entity_id=plan.id,
            action="PLAN_CREATED",
            old_value=None,
            new_value=plan_in.model_dump(),
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)

        return Success(self._to_response(plan))

    async def get_plan(self, db: AsyncSession, plan_id: str) -> Result[ProductPlanResponse]:
        plan = await plan_repository.get_with_capabilities(db, plan_id=plan_id)
        if not plan:
            return NotFoundError("Plan not found")
        
        return Success(self._to_response(plan))

    async def get_all_plans(self, db: AsyncSession) -> Result[List[ProductPlanResponse]]:
        plans = await plan_repository.get_multi(db)
        return Success([self._to_response(p) for p in plans])

    async def get_plans_for_product(self, db: AsyncSession, product_id: str) -> Result[List[ProductPlanResponse]]:
        plans = await plan_repository.get_by_product_id(db, product_id=product_id)
        return Success([self._to_response(p) for p in plans])

    async def update_plan(
        self, db: AsyncSession, plan_id: str, plan_in: ProductPlanUpdate, current_user: User, request: Request
    ) -> Result[ProductPlanResponse]:
        plan = await plan_repository.get(db, id=plan_id)
        if not plan:
            return NotFoundError("Plan not found")

        old_value = {
            "name": plan.name,
            "description": plan.description,
            "tier": plan.tier,
            "status": plan.status,
            "max_devices": plan.max_devices,
            "max_users": plan.max_users,
            "trial_days": plan.trial_days
        }

        updated_plan = await plan_repository.update(db, db_obj=plan, obj_in=plan_in)

        # Audit
        new_value = plan_in.model_dump(exclude_unset=True)
        if new_value:
            await event_bus.publish(DomainEvent(
                entity="ProductPlan",
                entity_id=updated_plan.id,
                action="PLAN_UPDATED",
                old_value=old_value,
                new_value=new_value,
                actor=current_user.id,
                request_id=getattr(request.state, "request_id", None)
            ), db=db)

        return Success(self._to_response(updated_plan))

    async def link_capability(
        self, db: AsyncSession, plan_id: str, capability_id: str, current_user: User, request: Request
    ) -> Result[dict]:
        plan = await plan_repository.get(db, id=plan_id)
        if not plan:
            return NotFoundError("Plan not found")

        capability = await capability_repository.get(db, id=capability_id)
        if not capability:
            return NotFoundError("Capability not found")

        # Architectural Rule: Only Capabilities belonging to the same Product can be attached
        product_caps = await capability_repository.get_capabilities_for_product(db, product_id=plan.product_id)
        if not any(c.id == capability_id for c in product_caps):
            return ConflictError(f"Capability '{capability.name}' does not belong to the product associated with this plan.")

        # Check if already linked
        existing = await plan_repository.get_with_capabilities(db, plan_id=plan_id)
        if any(pc.capability_id == capability_id for pc in existing.capabilities):
            return ConflictError("Capability is already linked to this plan")

        await plan_repository.link_capability(db, plan_id=plan_id, capability_id=capability_id)

        await event_bus.publish(DomainEvent(
            entity="ProductPlanCapability",
            entity_id=plan_id,
            action="PLAN_CAPABILITY_LINKED",
            old_value=None,
            new_value={"capability_id": capability_id},
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)

        return Success({"message": "Capability linked to plan successfully"})

    async def unlink_capability(
        self, db: AsyncSession, plan_id: str, capability_id: str, current_user: User, request: Request
    ) -> Result[dict]:
        plan = await plan_repository.get(db, id=plan_id)
        if not plan:
            return NotFoundError("Plan not found")
            
        success = await plan_repository.unlink_capability(db, plan_id=plan_id, capability_id=capability_id)
        if not success:
            return NotFoundError("Capability is not linked to this plan")

        await event_bus.publish(DomainEvent(
            entity="ProductPlanCapability",
            entity_id=plan_id,
            action="PLAN_CAPABILITY_UNLINKED",
            old_value={"capability_id": capability_id},
            new_value=None,
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)

        return Success({"message": "Capability unlinked from plan successfully"})

    def _to_response(self, plan: ProductPlan) -> ProductPlanResponse:
        capabilities = []
        # Check if capabilities are loaded to prevent MissingGreenlet lazy load exception
        insp = inspect(plan)
        if "capabilities" not in insp.unloaded and plan.capabilities:
            capabilities = [pc.capability for pc in plan.capabilities]
            
        plan_dict = {
            "id": plan.id,
            "product_id": plan.product_id,
            "name": plan.name,
            "slug": plan.slug,
            "description": plan.description,
            "tier": plan.tier,
            "status": plan.status,
            "max_devices": plan.max_devices,
            "max_users": plan.max_users,
            "trial_days": plan.trial_days,
            "duration_months": getattr(plan, "duration_months", 12),
            "created_at": plan.created_at,
            "updated_at": plan.updated_at,
            "capabilities": capabilities
        }
        return ProductPlanResponse.model_validate(plan_dict)

plan_service = PlanService()
