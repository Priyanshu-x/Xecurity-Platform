import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.models.capability import Capability, ProductCapability
from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.capability import CapabilityCreate, CapabilityUpdate
from app.services.capability_service import capability_service
from app.repositories.capability import capability_repository

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
        email="admin-cap@test.com",
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
async def test_create_capability(db: AsyncSession, admin_user: User):
    cap_in = CapabilityCreate(
        name="Test Capability",
        slug=f"test-cap-{uuid.uuid4()}",
        description="Test desc"
    )
    result = await capability_service.create_capability(db, cap_in, admin_user, FakeRequest())
    
    assert result.is_success
    assert result.value.name == "Test Capability"
    
    # Duplicate slug check
    cap_in_dup = CapabilityCreate(
        name="Another Name",
        slug=cap_in.slug,
        description="Duplicate slug"
    )
    dup_res = await capability_service.create_capability(db, cap_in_dup, admin_user, FakeRequest())
    assert not dup_res.is_success
    assert dup_res.error.code == "CONFLICT"

@pytest.mark.asyncio
async def test_link_unlink_capability(db: AsyncSession, admin_user: User, sample_product: Product):
    cap_in = CapabilityCreate(
        name="Link Test Cap",
        slug=f"link-test-{uuid.uuid4()}",
    )
    cap_res = await capability_service.create_capability(db, cap_in, admin_user, FakeRequest())
    assert cap_res.is_success
    cap = cap_res.value
    
    # Link
    link_res = await capability_service.link_capability_to_product(db, cap.id, sample_product.id, admin_user, FakeRequest())
    assert link_res.is_success
    
    # Check link
    product_caps = await capability_service.get_product_capabilities(db, sample_product.id)
    assert product_caps.is_success
    assert len(product_caps.value) == 1
    assert product_caps.value[0].id == cap.id
    
    # Unlink
    unlink_res = await capability_service.unlink_capability_from_product(db, cap.id, sample_product.id, admin_user, FakeRequest())
    assert unlink_res.is_success
    
    # Check unlink
    product_caps_after = await capability_service.get_product_capabilities(db, sample_product.id)
    assert len(product_caps_after.value) == 0

@pytest.mark.asyncio
async def test_update_capability(db: AsyncSession, admin_user: User):
    cap_in = CapabilityCreate(
        name="Old Name",
        slug=f"update-test-{uuid.uuid4()}",
    )
    cap = (await capability_service.create_capability(db, cap_in, admin_user, FakeRequest())).value
    
    update_in = CapabilityUpdate(name="New Name")
    update_res = await capability_service.update_capability(db, cap.id, update_in, admin_user, FakeRequest())
    
    assert update_res.is_success
    assert update_res.value.name == "New Name"
    assert update_res.value.slug == cap.slug  # unchanged
