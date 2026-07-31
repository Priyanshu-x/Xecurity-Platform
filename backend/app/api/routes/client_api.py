from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.schemas.device import (
    DeviceRegistrationRequest,
    DeviceRegistrationResponse,
    DeviceHeartbeatRequest,
    DeviceHeartbeatResponse,
)
from app.schemas.activation_request import ActivationRequestResponse
from app.services.device_service import device_service
from app.services.activation_request_service import activation_request_service

router = APIRouter(prefix="/client", tags=["Client API"])

def get_client_ip(request: Request) -> str:
    # In production, check X-Forwarded-For if behind proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"

@router.post("/requests", response_model=ActivationRequestResponse)
async def upload_activation_request(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        return await activation_request_service.create_from_upload(db, file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register", response_model=DeviceRegistrationResponse)
async def register_device(
    req: DeviceRegistrationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Public endpoint for initial device registration on first launch.
    """
    client_ip = get_client_ip(request)
    return await device_service.register_device(db, req, client_ip)

@router.post("/heartbeat", response_model=DeviceHeartbeatResponse)
async def heartbeat(
    req: DeviceHeartbeatRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Public endpoint for telemetry updates.
    """
    client_ip = get_client_ip(request)
    return await device_service.process_heartbeat(db, req, client_ip)

@router.post("/activate")
async def activate_license():
    """
    Reserved endpoint for uploading .wfareq or license activation payloads.
    """
    raise HTTPException(status_code=501, detail="License activation endpoint reserved for Phase 3.4")
