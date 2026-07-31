from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from fastapi.responses import FileResponse
from app.repositories.license_artifact import license_artifact_repository
from app.services.storage_service import storage_service
import os

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.user import User, UserRole
from app.api.deps import get_current_active_user, RoleChecker
from app.schemas.activation_request import (
    ActivationRequestResponse,
    ActivationRequestReject,
    LicenseGenerationConfig
)
from app.schemas.base import PaginatedResponse
from app.services.activation_request_service import activation_request_service

admin_checker = RoleChecker([UserRole.ADMIN, UserRole.OWNER])

router = APIRouter(prefix="/activation-requests", tags=["Activation Requests"])

@router.post("/upload", response_model=ActivationRequestResponse)
async def upload_request(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_checker)
):
    return await activation_request_service.create_from_upload(db, file)

@router.get("/", response_model=PaginatedResponse[ActivationRequestResponse])
async def list_requests(
    skip: int = 0,
    limit: int = 100,
    device_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_checker)
):
    requests, total = await activation_request_service.get_all(db, skip=skip, limit=limit, device_id=device_id)
    return PaginatedResponse(items=requests, total=total, skip=skip, limit=limit)

@router.get("/{id}", response_model=ActivationRequestResponse)
async def get_request(
    id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_checker)
):
    request = await activation_request_service.get(db, id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request

@router.post("/{id}/review", response_model=ActivationRequestResponse)
async def review_request(
    id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_checker)
):
    return await activation_request_service.review(db, id, current_user.id)

@router.post("/{id}/reject", response_model=ActivationRequestResponse)
async def reject_request(
    id: str,
    payload: ActivationRequestReject,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_checker)
):
    return await activation_request_service.reject(db, id, payload.reason, current_user.id, payload.notes)

@router.post("/{id}/generate", response_model=ActivationRequestResponse)
async def generate_license(
    id: str,
    config: LicenseGenerationConfig,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_checker)
):
    return await activation_request_service.generate_license(db, id, config.model_dump(), current_user.id)


@router.get("/{id}/download")
async def download_license(
    id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(admin_checker)
):
    request = await activation_request_service.get(db, id)
    if not request or not request.generated_license_id:
        raise HTTPException(status_code=404, detail="License not generated for this request")
        
    artifacts = await license_artifact_repository.get_multi(db, limit=1, license_id=request.generated_license_id)
    if not artifacts:
        raise HTTPException(status_code=404, detail="License artifact not found")
        
    artifact = artifacts[0]
    
    # The storage_path returned by LocalDiskStorageService is already the correct path
    file_path = os.path.abspath(artifact.storage_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing from storage")
        
    return FileResponse(
        path=file_path,
        filename=artifact.filename,
        media_type=artifact.mime_type or "application/octet-stream"
    )
