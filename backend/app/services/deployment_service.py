from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import Request

from app.models.user import User
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate, DeploymentResponse
from app.repositories.deployment import deployment_repository
from app.repositories.organization import organization_repository
from app.repositories.product import product_repository
from app.common.result import Result, Success, NotFoundError
from app.events.events import DomainEvent
from app.events.bus import event_bus
from app.common.enums import DeploymentStatus

class DeploymentService:
    
    async def create_deployment(
        self, db: AsyncSession, deployment_in: DeploymentCreate, actor: User, request: Request
    ) -> Result[DeploymentResponse]:
        
        # Verify org
        org = await organization_repository.get(db, id=deployment_in.organization_id)
        if not org:
            return NotFoundError("Organization not found")
            
        # Verify product
        prod = await product_repository.get(db, id=deployment_in.product_id)
        if not prod:
            return NotFoundError("Product not found")

        deployment = await deployment_repository.create(db, obj_in=deployment_in)
        
        await event_bus.publish(
            DomainEvent(
                action="DEPLOYMENT_REGISTERED",
                entity="Deployment",
                entity_id=deployment.id,
                new_value={"organization_id": deployment.organization_id, "product_id": deployment.product_id, "environment": deployment.environment},
                actor=str(actor.id),
                organization_id=deployment.organization_id,
            ),
            db=db
        )
        
        deployment_with_rels = await deployment_repository.get_with_relations(db, id=deployment.id)
        return Success(DeploymentResponse.model_validate(deployment_with_rels))

    async def get_deployment(self, db: AsyncSession, deployment_id: str) -> Result[DeploymentResponse]:
        deployment = await deployment_repository.get_with_relations(db, id=deployment_id)
        if not deployment or deployment.is_deleted:
            return NotFoundError("Deployment not found")
            
        return Success(DeploymentResponse.model_validate(deployment))

    async def get_all_deployments(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Result[List[DeploymentResponse]]:
        deployments = await deployment_repository.get_multi(db, skip=skip, limit=limit)
        return Success([DeploymentResponse.model_validate(d) for d in deployments])

    async def update_deployment(
        self, db: AsyncSession, deployment_id: str, update_in: DeploymentUpdate, actor: User, request: Request
    ) -> Result[DeploymentResponse]:
        
        deployment = await deployment_repository.get(db, id=deployment_id)
        if not deployment or deployment.is_deleted:
            return NotFoundError("Deployment not found")
            
        deployment = await deployment_repository.update(db, db_obj=deployment, obj_in=update_in)
        
        await event_bus.publish(
            DomainEvent(
                action="DEPLOYMENT_UPDATED",
                entity="Deployment",
                entity_id=deployment.id,
                new_value=update_in.model_dump(exclude_unset=True),
                actor=str(actor.id),
                organization_id=deployment.organization_id,
            ),
            db=db
        )
        
        deployment_with_rels = await deployment_repository.get_with_relations(db, id=deployment.id)
        return Success(DeploymentResponse.model_validate(deployment_with_rels))

    async def delete_deployment(
        self, db: AsyncSession, deployment_id: str, actor: User, request: Request
    ) -> Result[None]:
        
        deployment = await deployment_repository.get(db, id=deployment_id)
        if not deployment or deployment.is_deleted:
            return NotFoundError("Deployment not found")
            
        await deployment_repository.soft_delete(db, id=deployment_id)
        
        # Optionally, mark as DECOMMISSIONED if deleting?
        deployment.status = DeploymentStatus.DECOMMISSIONED
        await db.commit()
        
        await event_bus.publish(
            DomainEvent(
                action="DEPLOYMENT_DECOMMISSIONED",
                entity="Deployment",
                entity_id=deployment.id,
                new_value={},
                actor=str(actor.id),
                organization_id=deployment.organization_id,
            ),
            db=db
        )
        
        return Success(None)

deployment_service = DeploymentService()
