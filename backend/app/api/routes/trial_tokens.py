from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db_session
from app.models.user import User, UserRole
from app.api.dependencies import require_role
from app.repositories.trial_token import TrialTokenRepository
from app.services.trial_token_service import TrialTokenService
from app.schemas.trial_token import TrialTokenResponse, ManifestResponse

router = APIRouter()
require_admin = require_role([UserRole.OWNER, UserRole.ADMIN])

class GenerateTokenRequest(BaseModel):
    month: int
    year: int

def get_trial_token_service(db: AsyncSession = Depends(get_db_session)) -> TrialTokenService:
    repository = TrialTokenRepository(db)
    return TrialTokenService(repository)

@router.get("", response_model=List[TrialTokenResponse])
async def get_all_tokens(
    service: TrialTokenService = Depends(get_trial_token_service),
    current_user: User = Depends(require_admin)
):
    return await service.get_all_tokens()

@router.post("", response_model=TrialTokenResponse)
async def generate_token(
    request: GenerateTokenRequest,
    service: TrialTokenService = Depends(get_trial_token_service),
    current_user: User = Depends(require_admin)
):
    return await service.generate_token(request.month, request.year)

@router.patch("/{token_id}/revoke", response_model=TrialTokenResponse)
async def revoke_token(
    token_id: str,
    service: TrialTokenService = Depends(get_trial_token_service),
    current_user: User = Depends(require_admin)
):
    return await service.revoke_token(token_id)

@router.get("/manifest", response_model=ManifestResponse)
async def get_manifest(
    service: TrialTokenService = Depends(get_trial_token_service),
    current_user: User = Depends(require_admin)
):
    return await service.get_active_manifest()
