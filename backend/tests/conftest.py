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
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    async with TestingSessionLocal() as session:
        yield session
    await engine.dispose()
