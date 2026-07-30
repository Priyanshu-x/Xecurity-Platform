import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.capability import CapabilityCreate
from app.schemas.plan import ProductPlanCreate, ProductPlanUpdate
from app.services.capability_service import capability_service
from app.services.plan_service import plan_service

class FakeRequest:
    class Client:
        host = "127.0.0.1"
    client = Client()
    
    @property
    def state(self):
        class State:
            request_id = "test-req-123"
        return State()

@pytest_asyncio.fixture
async def admin_user():
    return User(
        id=str(uuid.uuid4()),
        email="admin-plan@test.com",
        role=UserRole.ADMIN,
        organization_id=str(uuid.uuid4())
    )

@pytest_asyncio.fixture
async def sample_product(db: AsyncSession):
    product = Product(
        name=f"Test Product {uuid.uuid4()}",
        slug=f"test-product-{uuid.uuid4()}",
        description="test",
        status="ACTIVE"
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@pytest.mark.asyncio
async def test_create_plan(db: AsyncSession, admin_user: User, sample_product: Product):
    product_id = sample_product.id
    plan_in = ProductPlanCreate(
        name="Enterprise Plan",
        slug=f"plan-test-prod-enterprise-{uuid.uuid4()}",
        description="Top tier plan",
        tier="ENTERPRISE",
        status="ACTIVE",
        product_id=product_id,
        max_devices=100
    )
    
    plan_res = await plan_service.create_plan(db, plan_in, admin_user, FakeRequest())
    assert plan_res.is_success
    plan = plan_res.value
    
    assert plan.name == "Enterprise Plan"
    assert plan.tier == "ENTERPRISE"
    assert plan.max_devices == 100

@pytest.mark.asyncio
async def test_link_capability_to_plan(db: AsyncSession, admin_user: User, sample_product: Product):
    product_id = sample_product.id
    
    # 1. Create a global capability
    cap_in = CapabilityCreate(
        name="OCR Scanning",
        slug=f"ocr-scan-plan-link-{uuid.uuid4()}",
        description="OCR capability"
    )
    cap_res = await capability_service.create_capability(db, cap_in, admin_user, FakeRequest())
    capability = cap_res.value
    capability_id = capability.id

    # 2. Create a plan
    plan_in = ProductPlanCreate(
        name="Pro Plan",
        slug=f"plan-link-test-prod-pro-{uuid.uuid4()}",
        product_id=product_id,
        tier="PROFESSIONAL"
    )
    plan_res = await plan_service.create_plan(db, plan_in, admin_user, FakeRequest())
    plan = plan_res.value
    plan_id = plan.id

    # 3. Try to link capability to plan (should fail because capability is not linked to product yet)
    link_fail_res = await plan_service.link_capability(db, plan_id, capability_id, admin_user, FakeRequest())
    assert not link_fail_res.is_success
    assert link_fail_res.error.code == "CONFLICT"
    assert "does not belong to the product" in link_fail_res.error.message

    # 4. Link capability to product first
    prod_link_res = await capability_service.link_capability_to_product(db, capability_id, product_id, admin_user, FakeRequest())
    assert prod_link_res.is_success

    # 5. Now try to link capability to plan (should succeed)
    link_success_res = await plan_service.link_capability(db, plan_id, capability_id, admin_user, FakeRequest())
    assert link_success_res.is_success

    # 6. Fetch the plan and verify capability is there
    get_plan_res = await plan_service.get_plan(db, plan_id)
    assert get_plan_res.is_success
    plan_data = get_plan_res.value
    assert len(plan_data.capabilities) == 1
    assert plan_data.capabilities[0].id == capability_id
