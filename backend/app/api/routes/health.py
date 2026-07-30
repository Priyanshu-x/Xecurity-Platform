from fastapi import APIRouter
from app.api.deps import SessionDep
from sqlalchemy import text

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "Xecurity Platform API"}

@router.get("/api/v1/health")
async def db_health_check(db: SessionDep):
    """Deep health check that verifies database connectivity."""
    try:
        # Simple test query
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "details": str(e)}
