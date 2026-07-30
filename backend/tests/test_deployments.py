import pytest
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate
from app.services.deployment_service import deployment_service
from app.common.enums import DeploymentEnvironment, DeploymentStatus
from sqlalchemy import select
from app.models.plan import ProductPlan

class FakeRequest:
    @property
    def state(self):
        class State:
            request_id = "test-req-123"
        return State()

@pytest.mark.asyncio
async def test_create_deployment(
    admin_user: User,
    test_subscription: Any,
    db: AsyncSession
):
    plan_result = await db.execute(select(ProductPlan).where(ProductPlan.id == test_subscription.product_plan_id))
    plan = plan_result.scalars().first()
    
    dep_in = DeploymentCreate(
        organization_id=test_subscription.organization_id,
        product_id=plan.product_id,
        name="Test Deployment",
        environment=DeploymentEnvironment.STAGING,
        current_release_version="1.0.0"
    )
    
    result = await deployment_service.create_deployment(db, dep_in, admin_user, FakeRequest())
    assert result.is_success
    dep = result.value
    assert dep.name == "Test Deployment"
    assert dep.organization_id == test_subscription.organization_id
    assert dep.product_id == plan.product_id
    assert dep.environment == DeploymentEnvironment.STAGING
    assert dep.status == DeploymentStatus.ACTIVE

@pytest.mark.asyncio
async def test_get_deployment(
    admin_user: User,
    test_subscription: Any,
    db: AsyncSession
):
    plan_result = await db.execute(select(ProductPlan).where(ProductPlan.id == test_subscription.product_plan_id))
    plan = plan_result.scalars().first()
    
    dep_in = DeploymentCreate(
        organization_id=test_subscription.organization_id,
        product_id=plan.product_id,
        name="Test Get",
        environment=DeploymentEnvironment.PRODUCTION
    )
    create_res = await deployment_service.create_deployment(db, dep_in, admin_user, FakeRequest())
    dep_id = create_res.value.id
    
    get_res = await deployment_service.get_deployment(db, dep_id)
    assert get_res.is_success
    assert get_res.value.name == "Test Get"

@pytest.mark.asyncio
async def test_update_deployment(
    admin_user: User,
    test_subscription: Any,
    db: AsyncSession
):
    plan_result = await db.execute(select(ProductPlan).where(ProductPlan.id == test_subscription.product_plan_id))
    plan = plan_result.scalars().first()
    
    dep_in = DeploymentCreate(
        organization_id=test_subscription.organization_id,
        product_id=plan.product_id,
        name="Test Update",
    )
    create_res = await deployment_service.create_deployment(db, dep_in, admin_user, FakeRequest())
    dep_id = create_res.value.id
    
    update_in = DeploymentUpdate(
        name="Updated Name",
        status=DeploymentStatus.INACTIVE
    )
    update_res = await deployment_service.update_deployment(db, dep_id, update_in, admin_user, FakeRequest())
    assert update_res.is_success
    assert update_res.value.name == "Updated Name"
    assert update_res.value.status == DeploymentStatus.INACTIVE

@pytest.mark.asyncio
async def test_delete_deployment(
    admin_user: User,
    test_subscription: Any,
    db: AsyncSession
):
    plan_result = await db.execute(select(ProductPlan).where(ProductPlan.id == test_subscription.product_plan_id))
    plan = plan_result.scalars().first()
    
    dep_in = DeploymentCreate(
        organization_id=test_subscription.organization_id,
        product_id=plan.product_id,
        name="Test Delete",
    )
    create_res = await deployment_service.create_deployment(db, dep_in, admin_user, FakeRequest())
    dep_id = create_res.value.id
    
    delete_res = await deployment_service.delete_deployment(db, dep_id, admin_user, FakeRequest())
    assert delete_res.is_success
    
    get_res = await deployment_service.get_deployment(db, dep_id)
    assert not get_res.is_success
    assert get_res.error.code == "NOT_FOUND"

