import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.core.config import settings

@pytest.fixture(scope="module")
def anyio_backend():
    return 'asyncio'

@pytest_asyncio.fixture
async def db():
    engine = create_async_engine(settings.DATABASE_URL)
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
    async with TestingSessionLocal() as session:
        yield session
    await engine.dispose()

import uuid
from app.models.user import User

@pytest_asyncio.fixture
async def admin_user():
    from app.models.user import UserRole
    return User(
        id=str(uuid.uuid4()),
        email="admin-conftest@test.com",
        role=UserRole.ADMIN,
        organization_id=str(uuid.uuid4())
    )

@pytest_asyncio.fixture
async def test_subscription(db: AsyncSession, admin_user: User):
    from app.models.product import Product
    from app.models.capability import Capability
    from app.models.plan import ProductPlan
    from app.models.subscription import Subscription
    from app.models.deployment import Deployment
    from app.common.enums import PlanTier, SubscriptionStatus, DeploymentEnvironment, DeploymentStatus
    from app.schemas.subscription import SubscriptionCreate
    from app.schemas.plan import ProductPlanCreate
    from app.services.subscription_service import subscription_service
    from app.services.plan_service import plan_service
    from app.repositories.organization import organization_repository, OrganizationCreate
    
    # 1. create org
    org_in = OrganizationCreate(name=f"Test Org {uuid.uuid4()}")
    org = await organization_repository.create(db, obj_in=org_in)
    
    # 2. create product
    product = Product(
        name=f"Test Product {uuid.uuid4()}",
        slug=f"test-product-{uuid.uuid4()}",
        description="test",
        status="ACTIVE"
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    class FakeRequest:
        @property
        def state(self):
            class State:
                request_id = "test-req-123"
            return State()

    # 3. create plan
    plan_in = ProductPlanCreate(
        name="Test Plan",
        slug=f"test-plan-sub-{uuid.uuid4()}",
        product_id=product.id,
        tier="PROFESSIONAL"
    )
    plan_res = await plan_service.create_plan(db, plan_in, admin_user, FakeRequest())
    plan = plan_res.value
    
    # 4. create sub
    sub_in = SubscriptionCreate(
        product_plan_id=plan.id,
        organization_id=org.id,
        notes="Test subscription"
    )
    sub_res = await subscription_service.create_subscription(db, sub_in, admin_user, FakeRequest())
    return sub_res.value

from app.models.organization import Organization
from app.models.product import Product
from app.models.deployment import Deployment
from app.common.enums import DeploymentEnvironment, DeploymentStatus

@pytest_asyncio.fixture(loop_scope="session")
async def sample_deployment(
    db: AsyncSession,
    sample_organization: Organization,
    sample_product: Product
) -> Deployment:
    deployment = Deployment(
        id=str(uuid.uuid4()),
        organization_id=sample_organization.id,
        product_id=sample_product.id,
        name="Test Deployment",
        environment=DeploymentEnvironment.STAGING,
        status=DeploymentStatus.ACTIVE
    )
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)
    return deployment
