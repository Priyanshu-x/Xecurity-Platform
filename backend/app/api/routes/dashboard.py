from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, require_role
from app.models.user import UserRole
from app.schemas.dashboard import DashboardStatsResponse
from app.services.dashboard_service import dashboard_service

router = APIRouter()

@router.get("/", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    # Allow all authenticated roles to hit this endpoint
    current_user = Depends(require_role([UserRole.OWNER, UserRole.ADMIN, UserRole.SUPPORT, UserRole.VIEWER]))
):
    """
    Get aggregated statistics and system health for the operational dashboard.
    The frontend will use the user's role to determine which stats to display.
    """
    stats = await dashboard_service.get_dashboard_stats(db)
    return stats
