import calendar
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException

from app.models.trial_token import TrialToken
from app.repositories.trial_token import TrialTokenRepository
from app.services.github_service import GitHubService
from app.schemas.trial_token import TrialTokenCreate, TrialTokenResponse, ManifestResponse

class TrialTokenService:
    def __init__(self, repository: TrialTokenRepository):
        self.repository = repository
        self.github_service = GitHubService()

    async def get_active_manifest(self) -> ManifestResponse:
        token = await self.repository.get_active_token()
        
        if not token or token.expires_at < datetime.now(timezone.utc):
            return ManifestResponse(
                version=1,
                active=False,
                token="",
                expires_at=None
            )
            
        return ManifestResponse(
            version=1,
            active=True,
            token=token.token_string,
            expires_at=token.expires_at
        )

    async def sync_github_manifest(self) -> None:
        manifest = await self.get_active_manifest()
        # Ensure we convert the pydantic model to a dict, handling datetimes properly
        manifest_dict = manifest.model_dump(mode="json")
        await self.github_service.push_manifest(manifest_dict)

    async def get_all_tokens(self) -> List[TrialToken]:
        # Using the base repository get_multi
        return await self.repository.get_multi(limit=100)

    async def generate_token(self, month: int, year: int) -> TrialToken:
        # Validate month
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="Invalid month")
            
        month_abbr = calendar.month_abbr[month].upper()
        token_string = f"WFA-TRIAL-{month_abbr}-{year}"
        
        # Check if exists
        existing = await self.repository.get_multi(limit=100)
        for t in existing:
            if t.token_string == token_string:
                raise HTTPException(status_code=400, detail=f"Token {token_string} already exists")

        # Expiry is end of the selected month
        last_day = calendar.monthrange(year, month)[1]
        expires_at = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

        # Invalidate existing active tokens
        active_token = await self.repository.get_active_token()
        if active_token:
            await self.repository.update(db_obj=active_token, obj_in={"is_active": False})

        # Create new token
        new_token = await self.repository.create(
            obj_in=TrialTokenCreate(
                token_string=token_string,
                expires_at=expires_at,
                is_active=True
            )
        )
        
        # Sync with GitHub
        await self.sync_github_manifest()
        return new_token

    async def revoke_token(self, token_id: str) -> TrialToken:
        token = await self.repository.get(id=token_id)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
            
        updated = await self.repository.update(db_obj=token, obj_in={"is_active": False})
        
        # Sync with GitHub
        await self.sync_github_manifest()
        return updated
