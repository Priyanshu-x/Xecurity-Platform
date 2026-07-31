from typing import List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.common.result import Result, Success, NotFoundError, ConflictError
from app.models.user import User
from app.models.license import License
from app.repositories.license import license_repository
from app.repositories.subscription import subscription_repository
from app.schemas.license import LicenseIssue, LicenseRevoke, LicenseResponse
from app.common.enums import LicenseStatus, SubscriptionStatus
from app.events.bus import EventBus
from app.events.events import DomainEvent

event_bus = EventBus()

class LicenseService:
    async def issue_license(
        self, db: AsyncSession, deployment_id: str, issue_in: LicenseIssue, current_user: User, request: Request
    ) -> Result[LicenseResponse]:
        
        # 1. Load subscription with relations
        subscription = await subscription_repository.get_with_relations(db, id=issue_in.subscription_id)
        if not subscription:
            return NotFoundError("Subscription not found")
        
        # 2. Check subscription status
        if subscription.status not in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL):
            return ConflictError(f"Cannot issue license for subscription in {subscription.status.value} status")
        
        # 3. Prevent duplicate active licenses for the same deployment
        existing_license = await license_repository.get_active_by_deployment(db, deployment_id)
        if existing_license:
            return ConflictError(f"Deployment {deployment_id} already has an active license")
        
        # 4. Resolve capabilities snapshot
        capabilities_snapshot = []
        # In our schema, capabilities are stored via ProductPlanCapability join model which has a capability relationship.
        # But wait, subscription.product_plan.capabilities has ProductPlanCapability objects.
        # We need to load capability details! This means we need to eagerly load capability.
        for ppc in subscription.product_plan.capabilities:
            capabilities_snapshot.append(ppc.capability.slug)
            
        payload = {
            "capabilities": capabilities_snapshot,
            "tier": subscription.product_plan.tier.value,
            "max_devices": subscription.product_plan.max_devices,
            "max_users": subscription.product_plan.max_users
        }
        
        # 5. Create license
        license = License(
            subscription_id=subscription.id,
            deployment_id=deployment_id,
            organization_id=subscription.organization_id,
            product_id=subscription.product_plan.product_id,
            product_plan_id=subscription.product_plan_id,
            status=LicenseStatus.ACTIVE,
            payload_json=payload,
            notes=issue_in.notes,
            expires_at=subscription.expires_at
        )
        db.add(license)
        await db.commit()
        await db.refresh(license)
        
        # 6. Emit event
        await event_bus.publish(DomainEvent(
            entity="License",
            entity_id=license.id,
            action="LICENSE_ISSUED",
            old_value=None,
            new_value=LicenseResponse.model_validate(license).model_dump(mode='json'),
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)
        
        license_with_rels = await license_repository.get_with_relations(db, id=license.id)
        return Success(LicenseResponse.model_validate(license_with_rels))
        
    async def revoke_license(
        self, db: AsyncSession, license_id: str, revoke_in: LicenseRevoke, current_user: User, request: Request
    ) -> Result[LicenseResponse]:
        license = await license_repository.get(db, id=license_id)
        if not license:
            return NotFoundError("License not found")
            
        if license.status == LicenseStatus.REVOKED:
            return ConflictError("License is already revoked")
            
        old_status = license.status
        license.status = LicenseStatus.REVOKED
        if revoke_in.notes:
            license.notes = revoke_in.notes
            
        db.add(license)
        await db.commit()
        await db.refresh(license)
        
        await event_bus.publish(DomainEvent(
            entity="License",
            entity_id=license.id,
            action="LICENSE_REVOKED",
            old_value={"status": old_status.value},
            new_value={"status": LicenseStatus.REVOKED.value},
            actor=current_user.id,
            request_id=getattr(request.state, "request_id", None)
        ), db=db)
        
        license_with_rels = await license_repository.get_with_relations(db, id=license.id)
        return Success(LicenseResponse.model_validate(license_with_rels))
        
    async def get_license(self, db: AsyncSession, license_id: str) -> Result[LicenseResponse]:
        license = await license_repository.get_with_relations(db, id=license_id)
        if not license:
            return NotFoundError("License not found")
        return Success(LicenseResponse.model_validate(license))
        
    async def list_licenses(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Result[List[LicenseResponse]]:
        licenses = await license_repository.get_multi(db, skip=skip, limit=limit)
        return Success([LicenseResponse.model_validate(lic) for lic in licenses])

license_service = LicenseService()
