from fastapi import APIRouter
from app.api.auth.routes import router as auth_router
from app.api.users import router as users_router
from app.api.analytics import router as analytics_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(analytics_router)
