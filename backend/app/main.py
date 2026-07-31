from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import global_exception_handler
from app.api.main import api_router
from app.api.routes import health
from app.services.audit_service import setup_audit_logging

# Initialize event listeners
setup_audit_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Xecurity Platform Backend API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(api_router, prefix="/api/v1")
