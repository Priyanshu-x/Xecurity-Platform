from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db_session
from app.models.user import User, UserRole
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.api.deps import get_current_active_user, RoleChecker
from app.services.product_service import product_service
from app.common.responses import handle_result

router = APIRouter()

@router.post("/", response_model=ProductResponse)
async def create_product(
    request: Request,
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await product_service.create_product(db, product_in, current_user, request)
    return handle_result(result)

@router.get("/", response_model=List[ProductResponse])
async def list_products(
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await product_service.list_products(db, include_deleted)
    return handle_result(result)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await product_service.get_product(db, product_id)
    return handle_result(result)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    request: Request,
    product_id: str,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await product_service.update_product(db, product_id, product_in, current_user, request)
    return handle_result(result)

@router.delete("/{product_id}")
async def delete_product(
    request: Request,
    product_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.OWNER, UserRole.ADMIN]))
):
    result = await product_service.delete_product(db, product_id, current_user, request)
    handle_result(result)
    return {"message": "Product deleted successfully"}
