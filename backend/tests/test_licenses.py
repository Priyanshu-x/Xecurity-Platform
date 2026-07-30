import pytest
import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.license import License
from app.models.user import User
from app.schemas.license import LicenseIssue, LicenseRevoke
from app.services.license_service import license_service
from app.common.enums import LicenseStatus, SubscriptionStatus, DeploymentEnvironment, DeploymentStatus
from app.models.deployment import Deployment
from sqlalchemy import select
from app.models.plan import ProductPlan

class FakeRequest:
    @property
    def state(self):
        class State:
            request_id = "test-req-123"
        return State()

@pytest.mark.asyncio
async def test_issue_license_success(
    admin_user: User,
    test_subscription: Any,
    db: AsyncSession
):
    issue_data = LicenseIssue(
        subscription_id=test_subscription.id,
        notes="Test license"
    )
    
    # Get product_id from plan
    plan_result = await db.execute(select(ProductPlan).where(ProductPlan.id == test_subscription.product_plan_id))
    plan = plan_result.scalars().first()
    
    deployment_id = str(uuid.uuid4())
    dep = Deployment(id=deployment_id, organization_id=test_subscription.organization_id, product_id=plan.product_id, name="Test", environment=DeploymentEnvironment.STAGING, status=DeploymentStatus.ACTIVE)
    db.add(dep)
    await db.commit()
    
    result = await license_service.issue_license(db, deployment_id, issue_data, admin_user, FakeRequest())
    
    assert result.is_success
    data = result.value
    assert data.id is not None
    assert data.deployment_id == deployment_id
    assert data.subscription_id == test_subscription.id
    assert data.status == LicenseStatus.ACTIVE
    assert "capabilities" in data.payload_json
    assert "tier" in data.payload_json
    
@pytest.mark.asyncio
async def test_prevent_duplicate_active_license(
    admin_user: User,
    test_subscription: Any,
    db: AsyncSession
):
    issue_data = LicenseIssue(
        subscription_id=test_subscription.id,
        notes="Test license 1"
    )
    
    # Get product_id from plan
    plan_result = await db.execute(select(ProductPlan).where(ProductPlan.id == test_subscription.product_plan_id))
    plan = plan_result.scalars().first()
    
    deployment_id = str(uuid.uuid4())
    dep = Deployment(id=deployment_id, organization_id=test_subscription.organization_id, product_id=plan.product_id, name="Test", environment=DeploymentEnvironment.STAGING, status=DeploymentStatus.ACTIVE)
    db.add(dep)
    await db.commit()
    
    # Issue first license
    result1 = await license_service.issue_license(db, deployment_id, issue_data, admin_user, FakeRequest())
    assert result1.is_success
    
    # Try to issue second license for SAME deployment
    result2 = await license_service.issue_license(db, deployment_id, issue_data, admin_user, FakeRequest())
    assert not result2.is_success
    assert result2.error.code == "CONFLICT"

@pytest.mark.asyncio
async def test_revoke_license(
    admin_user: User,
    test_subscription: Any,
    db: AsyncSession
):
    # Issue a license first
    issue_data = LicenseIssue(
        subscription_id=test_subscription.id,
        notes="To be revoked"
    )
    
    # Get product_id from plan
    plan_result = await db.execute(select(ProductPlan).where(ProductPlan.id == test_subscription.product_plan_id))
    plan = plan_result.scalars().first()
    
    deployment_id = str(uuid.uuid4())
    dep = Deployment(id=deployment_id, organization_id=test_subscription.organization_id, product_id=plan.product_id, name="Test", environment=DeploymentEnvironment.STAGING, status=DeploymentStatus.ACTIVE)
    db.add(dep)
    await db.commit()
    
    issue_resp = await license_service.issue_license(db, deployment_id, issue_data, admin_user, FakeRequest())
    assert issue_resp.is_success
    license_id = issue_resp.value.id
    
    # Revoke it
    revoke_data = LicenseRevoke(notes="Revoking it")
    revoke_resp = await license_service.revoke_license(db, license_id, revoke_data, admin_user, FakeRequest())
    
    assert revoke_resp.is_success
    assert revoke_resp.value.status == LicenseStatus.REVOKED
    
    # Revoking again should be a conflict
    revoke_again = await license_service.revoke_license(db, license_id, revoke_data, admin_user, FakeRequest())
    assert not revoke_again.is_success
    assert revoke_again.error.code == "CONFLICT"
