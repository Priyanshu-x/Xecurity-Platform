from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import global_exception_handler
from app.api.main import api_router
from app.api.routes import health
from app.services.audit_service import setup_audit_logging

import os
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.future import select
from app.core.database import engine, Base, AsyncSessionLocal
import app.models  # Ensure all SQLAlchemy models are registered
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# Initialize event listeners
setup_audit_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist & patch schema if new columns were added
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE product_plans ADD COLUMN IF NOT EXISTS duration_months INTEGER DEFAULT 12;"))
            await conn.execute(text("ALTER TYPE plantier ADD VALUE IF NOT EXISTS 'CUSTOM';"))
        except Exception as e:
            print(f"[INFO] Schema patch notice: {e}")
    
    # Ensure storage directory exists
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)

    # Ensure default Platform OWNER exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.role == UserRole.OWNER))
        owner = result.scalar_one_or_none()
        if not owner:
            print("[INFO] Creating default Platform OWNER (admin@xecurity.com)...")
            db.add(User(
                email="admin@xecurity.com",
                hashed_password=get_password_hash("changeme123"),
                role=UserRole.OWNER,
                is_active=True,
            ))
            await db.commit()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Xecurity Platform Backend API",
    version="0.1.0",
    lifespan=lifespan
)

# Parse CORS origins from settings
_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
_allow_credentials = _origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(api_router, prefix="/api/v1")
