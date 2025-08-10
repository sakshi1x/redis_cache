import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.auth_routes import router as auth_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Employee API with Redis Hash Profiles",
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "signup": "POST /api/v1/auth/signup",
            "login": "POST /api/v1/auth/login", 
            "ask": "POST /api/v1/auth/ask",
            "get_profile": "GET /api/v1/auth/profile",
            "update_profile": "PUT /api/v1/auth/profile",
            "get_stats": "GET /api/v1/auth/stats"
        },
        "features": {
            "redis_hash_profiles": "Enhanced user profiles with Redis Hash data structure",
            "user_statistics": "Track login count, questions asked, and activity",
            "profile_management": "Update department and role information",
            "persistent_storage": "Data persists across server restarts"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.__main__:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
