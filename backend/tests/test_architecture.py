import pytest
import asyncio
from pydantic import BaseModel
from sqlalchemy import Column, String
from app.core.database import Base
from app.models.base_model import BaseModelMixin
from app.repositories.base import BaseRepository
from app.events.bus import EventBus
from app.events.events import DomainEvent
from app.services.audit_service import audit_listener
from app.models.audit import AuditLog
from sqlalchemy.future import select

# Dummy Model for Repository Testing
class DummyModel(Base, BaseModelMixin):
    __tablename__ = "dummy_models"
    name = Column(String)

class DummyCreate(BaseModel):
    name: str

class DummyUpdate(BaseModel):
    name: str

import pytest_asyncio
@pytest_asyncio.fixture
async def setup_dummy_table(db):
    async with db.bind.begin() as conn:
        await conn.run_sync(DummyModel.__table__.drop, checkfirst=True)
        await conn.run_sync(DummyModel.__table__.create, checkfirst=True)
    yield
    async with db.bind.begin() as conn:
        await conn.run_sync(DummyModel.__table__.drop)

@pytest.mark.asyncio
async def test_base_repository(db, setup_dummy_table):
    repo = BaseRepository[DummyModel, DummyCreate, DummyUpdate](DummyModel)
    
    # Create
    dummy = await repo.create(db, obj_in=DummyCreate(name="Test"))
    assert dummy.id is not None
    assert dummy.name == "Test"
    assert dummy.is_deleted is False
    
    # Get
    fetched = await repo.get(db, dummy.id)
    assert fetched is not None
    assert fetched.name == "Test"
    
    # Update
    updated = await repo.update(db, db_obj=fetched, obj_in={"name": "Updated Test"})
    assert updated.name == "Updated Test"
    
    # Soft Delete
    await repo.soft_delete(db, id=dummy.id)
    
    # Get Multi (should not return soft-deleted by default)
    items = await repo.get_multi(db)
    assert len(items) == 0
    
    # Get still returns it (since get doesn't auto-filter)
    deleted_item = await repo.get(db, dummy.id)
    assert deleted_item.is_deleted is True
    assert deleted_item.deleted_at is not None

@pytest.mark.asyncio
async def test_event_bus_and_audit(db):
    bus = EventBus()
    bus.subscribe(DomainEvent, audit_listener)
    
    event = DomainEvent(
        entity="TestEntity",
        entity_id="123",
        action="TEST_ACTION",
        old_value={"key": "old"},
        new_value={"key": "new"}
    )
    
    await bus.publish(event, db=db)
    await db.commit()
    
    # Verify audit log was created
    result = await db.execute(select(AuditLog).where(AuditLog.action == "TEST_ACTION"))
    audit = result.scalars().first()
    
    assert audit is not None
    assert audit.entity == "TestEntity"
    assert audit.entity_id == "123"
    assert audit.old_value == {"key": "old"}
    assert audit.new_value == {"key": "new"}
