import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI

from app.models.release import Release, ReleaseChannel, ReleasePlatform, ReleaseArchitecture
from app.models.product import Product
from app.repositories.release import release_repository
from app.services.release_service import release_service
from app.schemas.release import ReleaseCreate

import pytest_asyncio
@pytest_asyncio.fixture
async def sample_product(db: AsyncSession):
    import uuid
    product = Product(
        name=f"Test Product {uuid.uuid4()}",
        slug=f"test-release-{uuid.uuid4()}",
        description="test",
        status="ACTIVE"
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@pytest_asyncio.fixture
async def admin_user():
    from app.models.user import User, UserRole
    import uuid
    return User(
        id=str(uuid.uuid4()),
        email="admin@test.com",
        role=UserRole.ADMIN,
        organization_id=str(uuid.uuid4())
    )

@pytest.mark.asyncio
async def test_release_service_create(db: AsyncSession, sample_product: Product, admin_user):
    from app.models.user import User
    
    release_in = ReleaseCreate(
        product_id=sample_product.id,
        version="1.0.0",
        version_code=100,
        channel=ReleaseChannel.STABLE,
        platform=ReleasePlatform.WINDOWS,
        architecture=ReleaseArchitecture.X64,
        installer_type=InstallerType.INSTALLER,
        filename="setup.exe",
        download_path="/downloads/setup.exe",
        sha256="fakehash123",
        filesize=1024,
        is_latest=True
    )
    
    class FakeRequest:
        class Client:
            host = "127.0.0.1"
        client = Client()

    result = await release_service.create_release(db, release_in, admin_user, FakeRequest())
    assert result.is_success
    assert result.value.version == "1.0.0"
    assert result.value.is_latest == True

@pytest.mark.asyncio
async def test_release_demotion(db: AsyncSession, sample_product: Product, admin_user):
    release_in_1 = ReleaseCreate(
        product_id=sample_product.id,
        version="1.0.0",
        version_code=100,
        channel=ReleaseChannel.STABLE,
        platform=ReleasePlatform.WINDOWS,
        architecture=ReleaseArchitecture.X64,
        installer_type=InstallerType.INSTALLER,
        filename="setup1.exe",
        download_path="/downloads/setup1.exe",
        sha256="hash1",
        filesize=1024,
        is_latest=True
    )
    
    class FakeRequest:
        class Client:
            host = "127.0.0.1"
        client = Client()

    res1 = await release_service.create_release(db, release_in_1, admin_user, FakeRequest())
    assert res1.is_success
    assert res1.value.is_latest == True
    
    # Second release should demote the first one
    release_in_2 = ReleaseCreate(
        product_id=sample_product.id,
        version="1.1.0",
        version_code=110,
        channel=ReleaseChannel.STABLE,
        platform=ReleasePlatform.WINDOWS,
        architecture=ReleaseArchitecture.X64,
        installer_type=InstallerType.INSTALLER,
        filename="setup2.exe",
        download_path="/downloads/setup2.exe",
        sha256="hash2",
        filesize=1024,
        is_latest=True
    )
    
    res2 = await release_service.create_release(db, release_in_2, admin_user, FakeRequest())
    assert res2.is_success
    
    # Reload first release
    await db.refresh(res1.value)
    assert res1.value.is_latest == False
    assert res2.value.is_latest == True

@pytest.mark.asyncio
async def test_duplicate_version_prevention(db: AsyncSession, sample_product: Product, admin_user):
    release_in = ReleaseCreate(
        product_id=sample_product.id,
        version="2.0.0",
        version_code=200,
        channel=ReleaseChannel.STABLE,
        platform=ReleasePlatform.WINDOWS,
        architecture=ReleaseArchitecture.X64,
        installer_type=InstallerType.INSTALLER,
        filename="setup.exe",
        download_path="/downloads/setup.exe",
        sha256="hash3",
        filesize=1024
    )
    
    class FakeRequest:
        class Client:
            host = "127.0.0.1"
        client = Client()

    res1 = await release_service.create_release(db, release_in, admin_user, FakeRequest())
    assert res1.is_success
    
    release_in.sha256 = "hash4" # change hash to bypass sha256 check
    res2 = await release_service.create_release(db, release_in, admin_user, FakeRequest())
    assert not res2.is_success
    assert res2.error.code == "CONFLICT"
