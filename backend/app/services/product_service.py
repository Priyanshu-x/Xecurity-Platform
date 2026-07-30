from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.models.product import Product, ProductStatus
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate
from app.repositories.product import product_repository
from app.events.bus import event_bus
from app.events.events import DomainEvent
from app.common.result import Result, Success, Failure, ConflictError, NotFoundError, ValidationError

class ProductService:
    @staticmethod
    async def create_product(db: AsyncSession, product_in: ProductCreate, current_user: User, request: Request) -> Result[Product]:
        if await product_repository.exists(db, slug=product_in.slug):
            return ConflictError(message="Product with this slug already exists.")
            
        product = await product_repository.create(db, obj_in=product_in)
        
        await event_bus.publish(
            DomainEvent(
                actor=current_user.id,
                organization_id=current_user.organization_id,
                entity="Product",
                entity_id=product.id,
                action="CREATED_PRODUCT",
                new_value={"name": product.name, "slug": product.slug},
                ip=request.client.host if request and request.client else None
            ),
            db=db
        )
        return Success(product)

    @staticmethod
    async def list_products(db: AsyncSession, include_deleted: bool = False) -> Result[List[Product]]:
        products, _ = await product_repository.paginate(db, page=1, size=1000, include_deleted=include_deleted)
        return Success(products)

    @staticmethod
    async def get_product(db: AsyncSession, product_id: str) -> Result[Product]:
        product = await product_repository.get(db, id=product_id)
        if not product or product.is_deleted:
            return NotFoundError(message="Product not found")
        return Success(product)

    @staticmethod
    async def update_product(db: AsyncSession, product_id: str, product_in: ProductUpdate, current_user: User, request: Request) -> Result[Product]:
        product = await product_repository.get(db, id=product_id)
        if not product or product.is_deleted:
            return NotFoundError(message="Product not found")
            
        update_data = product_in.model_dump(exclude_unset=True)
        if "slug" in update_data and update_data["slug"] != product.slug:
            if await product_repository.exists(db, slug=update_data["slug"]):
                return ConflictError(message="Product with this slug already exists.")
                
        product = await product_repository.update(db, db_obj=product, obj_in=product_in)
        
        await event_bus.publish(
            DomainEvent(
                actor=current_user.id,
                organization_id=current_user.organization_id,
                entity="Product",
                entity_id=product.id,
                action="UPDATED_PRODUCT",
                new_value={"updated_fields": list(update_data.keys())},
                ip=request.client.host if request and request.client else None
            ),
            db=db
        )
        return Success(product)

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: str, current_user: User, request: Request) -> Result[bool]:
        product = await product_repository.get(db, id=product_id)
        if not product or product.is_deleted:
            return NotFoundError(message="Product not found")
            
        # Update status to ARCHIVED before soft deleting
        await product_repository.update(db, db_obj=product, obj_in={"status": ProductStatus.ARCHIVED})
        await product_repository.soft_delete(db, id=product_id)
        
        await event_bus.publish(
            DomainEvent(
                actor=current_user.id,
                organization_id=current_user.organization_id,
                entity="Product",
                entity_id=product.id,
                action="DELETED_PRODUCT",
                ip=request.client.host if request and request.client else None
            ),
            db=db
        )
        return Success(True)

product_service = ProductService()
