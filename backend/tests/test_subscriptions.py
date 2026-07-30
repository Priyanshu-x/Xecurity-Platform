import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.product import Product
from app.models.organization import Organization
from app.models.plan import ProductPlan
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate
from app.schemas.plan import ProductPlanCreate
from app.services.subscription_service import subscription_service
from app.services.plan_service import plan_service
from app.common.enums import SubscriptionStatus

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

@pytest_asyncio.fixture
async def sample_plan(db: AsyncSession, admin_user: User, sample_product: Product) -> ProductPlan:
    plan_in = ProductPlanCreate(
        name="Test Plan",
        slug=f"test-plan-sub-{uuid.uuid4()}",
        product_id=sample_product.id,
        tier="PROFESSIONAL"
    )
    plan_res = await plan_service.create_plan(db, plan_in, admin_user, FakeRequest())
    return plan_res.value

@pytest_asyncio.fixture
async def sample_organization(db: AsyncSession) -> Organization:
    from app.repositories.organization import organization_repository, OrganizationCreate
    org_in = OrganizationCreate(name=f"Test Org {uuid.uuid4()}")
    return await organization_repository.create(db, obj_in=org_in)

@pytest.mark.asyncio
async def test_create_subscription(db: AsyncSession, admin_user: User, sample_plan: ProductPlan, sample_organization: Organization):
    sub_in = SubscriptionCreate(
        product_plan_id=sample_plan.id,
        organization_id=sample_organization.id,
        notes="Test subscription"
    )
    
    sub_res = await subscription_service.create_subscription(db, sub_in, admin_user, FakeRequest())
    assert sub_res.is_success
    subscription = sub_res.value
    
    assert subscription.product_plan_id == sample_plan.id
    assert subscription.organization_id == sample_organization.id
    assert subscription.status == SubscriptionStatus.ACTIVE
    assert subscription.notes == "Test subscription"

@pytest.mark.asyncio
async def test_create_subscription_conflict(db: AsyncSession, admin_user: User, sample_plan: ProductPlan, sample_organization: Organization):
    sub_in = SubscriptionCreate(
        product_plan_id=sample_plan.id,
        organization_id=sample_organization.id,
        notes="Test subscription 1"
    )
    
    sub_res = await subscription_service.create_subscription(db, sub_in, admin_user, FakeRequest())
    assert sub_res.is_success
    
    # Try creating another one for the same plan/org
    sub_res_2 = await subscription_service.create_subscription(db, sub_in, admin_user, FakeRequest())
    assert not sub_res_2.is_success
    assert sub_res_2.error.code == "CONFLICT"

@pytest.mark.asyncio
async def test_get_subscription(db: AsyncSession, admin_user: User, sample_plan: ProductPlan, sample_organization: Organization):
    sub_in = SubscriptionCreate(
        product_plan_id=sample_plan.id,
        organization_id=sample_organization.id
    )
    
    sub_res = await subscription_service.create_subscription(db, sub_in, admin_user, FakeRequest())
    subscription = sub_res.value
    
    get_res = await subscription_service.get_subscription(db, subscription.id)
    assert get_res.is_success
    assert get_res.value.id == subscription.id
    assert get_res.value.product_plan is not None

@pytest.mark.asyncio
async def test_update_subscription(db: AsyncSession, admin_user: User, sample_plan: ProductPlan, sample_organization: Organization):
    sub_in = SubscriptionCreate(
        product_plan_id=sample_plan.id,
        organization_id=sample_organization.id
    )
    
    sub_res = await subscription_service.create_subscription(db, sub_in, admin_user, FakeRequest())
    subscription = sub_res.value
    
    update_in = SubscriptionUpdate(notes="Updated notes")
    update_res = await subscription_service.update_subscription(db, subscription.id, update_in, admin_user, FakeRequest())
    
    assert update_res.is_success
    assert update_res.value.notes == "Updated notes"

@pytest.mark.asyncio
async def test_suspend_subscription(db: AsyncSession, admin_user: User, sample_plan: ProductPlan, sample_organization: Organization):
    sub_in = SubscriptionCreate(
        product_plan_id=sample_plan.id,
        organization_id=sample_organization.id
    )
    
    sub_res = await subscription_service.create_subscription(db, sub_in, admin_user, FakeRequest())
    subscription = sub_res.value
    
    suspend_res = await subscription_service.suspend_subscription(db, subscription.id, admin_user, FakeRequest())
    
    assert suspend_res.is_success
    assert suspend_res.value.status == SubscriptionStatus.SUSPENDED

@pytest.mark.asyncio
async def test_cancel_subscription(db: AsyncSession, admin_user: User, sample_plan: ProductPlan, sample_organization: Organization):
    sub_in = SubscriptionCreate(
        product_plan_id=sample_plan.id,
        organization_id=sample_organization.id
    )
    
    sub_res = await subscription_service.create_subscription(db, sub_in, admin_user, FakeRequest())
    subscription = sub_res.value
    
    cancel_res = await subscription_service.cancel_subscription(db, subscription.id, admin_user, FakeRequest())
    
    assert cancel_res.is_success
    assert cancel_res.value.status == SubscriptionStatus.CANCELLED

@pytest.mark.asyncio
async def test_get_all_subscriptions_eager_loads(
    admin_user: User,
    sample_organization: Organization,
    sample_plan: ProductPlan,
    db: AsyncSession
):
    sub_in = SubscriptionCreate(
        product_plan_id=sample_plan.id,
        organization_id=sample_organization.id,
        notes="Eager load test"
    )
    
    sub_res = await subscription_service.create_subscription(db, sub_in, admin_user, FakeRequest())
    assert sub_res.is_success
    
    # Close and recreate session to ensure everything is purged and we test a true separate fetch
    await db.commit()
    db.expunge_all()
    
    # Fetch all subscriptions via service (which internally calls get_multi)
    res = await subscription_service.get_all_subscriptions(db)
    
    assert res.is_success
    assert len(res.value) > 0
    
    found = False
    for sub in res.value:
        if sub.id == sub_res.value.id:
            found = True
            # Check eager loaded nested model
            assert sub.product_plan is not None
            assert sub.product_plan.id == sample_plan.id
    
    assert found
