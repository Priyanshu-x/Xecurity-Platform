from fastapi import APIRouter
from app.api.routes import health, auth, products, releases, capabilities, plans, subscriptions, licenses, deployments, organizations

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(releases.router, prefix="/releases", tags=["releases"])
api_router.include_router(capabilities.router, prefix="/capabilities", tags=["capabilities"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(deployments.router, prefix="/deployments", tags=["deployments"])
api_router.include_router(licenses.router, prefix="/licenses", tags=["licenses"])
