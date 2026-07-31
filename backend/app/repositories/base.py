from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sa_update, delete as sa_delete
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Repository object with default methods to Create, Read, Update, Delete (CRUD).
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        # Filter out deleted if 'is_deleted' exists
        stmt = select(self.model)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        obj_in_data = obj_in.model_dump()
        obj_in_data.update(kwargs)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]], **kwargs
    ) -> ModelType:
        obj_data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType:
        """Hard delete an entity"""
        obj = await self.get(db=db, id=id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj

    async def soft_delete(self, db: AsyncSession, *, id: Any, **kwargs) -> Optional[ModelType]:
        """Soft delete an entity if it supports is_deleted"""
        from datetime import datetime, timezone
        obj = await self.get(db=db, id=id)
        if obj and hasattr(obj, "is_deleted"):
            obj.is_deleted = True
            if hasattr(obj, "deleted_at"):
                obj.deleted_at = datetime.now(timezone.utc)
            db.add(obj)
            await db.flush()
            await db.refresh(obj)
        return obj

    async def restore(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """Restore a soft-deleted entity"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        obj = result.scalars().first()
        if obj and hasattr(obj, "is_deleted"):
            obj.is_deleted = False
            if hasattr(obj, "deleted_at"):
                obj.deleted_at = None
            db.add(obj)
            await db.flush()
            await db.refresh(obj)
        return obj

    async def exists(self, db: AsyncSession, **kwargs) -> bool:
        """Check if an entity exists by exact match kwargs"""
        stmt = select(self.model)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalars().first() is not None

    async def count(self, db: AsyncSession, include_deleted: bool = False, **kwargs) -> int:
        """Count entities matching kwargs"""
        from sqlalchemy import func
        stmt = select(func.count(self.model.id))
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one()

    async def search(self, db: AsyncSession, *, search_str: str, search_fields: List[str], skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Simple ILIKE search across specified string fields"""
        from sqlalchemy import or_
        stmt = select(self.model)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
            
        if search_str and search_fields:
            conditions = []
            for field in search_fields:
                column = getattr(self.model, field)
                conditions.append(column.ilike(f"%{search_str}%"))
            stmt = stmt.where(or_(*conditions))
            
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def paginate(self, db: AsyncSession, page: int = 1, size: int = 50, include_deleted: bool = False, **kwargs) -> tuple[List[ModelType], int]:
        """Return (items, total_count) for pagination"""
        stmt = select(self.model)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)
            
        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
            
        # Get count
        from sqlalchemy import func
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()
        
        # Get items
        skip = (page - 1) * size
        stmt = stmt.offset(skip).limit(size)
        items = list((await db.execute(stmt)).scalars().all())
        
        return items, total

    async def bulk_create(self, db: AsyncSession, *, objs_in: List[CreateSchemaType], **kwargs) -> List[ModelType]:
        """Create multiple entities efficiently"""
        db_objs = []
        for obj_in in objs_in:
            obj_in_data = obj_in.model_dump()
            obj_in_data.update(kwargs)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db_objs.append(db_obj)
        await db.flush()
        for db_obj in db_objs:
            await db.refresh(db_obj)
        return db_objs

    async def bulk_update(self, db: AsyncSession, *, objs_data: List[Dict[str, Any]]) -> List[ModelType]:
        """Update multiple entities given a list of dictionaries. Each dict MUST contain 'id'."""
        # A simple implementation - in real life, PostgreSQL allows more efficient bulk updates.
        updated_objs = []
        for data in objs_data:
            if "id" not in data:
                continue
            obj = await self.get(db, data["id"])
            if obj:
                for key, value in data.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                db.add(obj)
                updated_objs.append(obj)
        await db.flush()
        return updated_objs

    async def bulk_soft_delete(self, db: AsyncSession, *, ids: List[Any]) -> None:
        """Soft delete multiple entities by IDs"""
        from datetime import datetime, timezone
        if not hasattr(self.model, "is_deleted"):
            return
            
        stmt = (
            sa_update(self.model)
            .where(self.model.id.in_(ids))
            .values(is_deleted=True, deleted_at=datetime.now(timezone.utc))
        )
        await db.execute(stmt)
        await db.flush()
