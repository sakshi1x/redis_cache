from fastapi import APIRouter, Request, HTTPException
from app.api.users.routes import RedisUserProfiles
from app.utils.helpers import require_authentication, get_authenticated_employee

router = APIRouter(prefix="/users", tags=["User Profiles"])
user_profiles = RedisUserProfiles()

@router.get("/profile")
async def get_user_profile(request: Request):
    """Get current user's profile"""
    employee = get_authenticated_employee(request)
    profile = user_profiles.get_user_profile(employee.employee_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    return {"success": True, "profile": profile}

@router.get("/stats")
async def get_user_stats(request: Request):
    """Get current user's statistics"""
    employee = get_authenticated_employee(request)
    stats = user_profiles.get_user_stats(employee.employee_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="User statistics not found")
    
    return {"success": True, "stats": stats}

@router.get("/all")
async def get_all_users(request: Request):
    """Get all users (admin only)"""
    require_authentication(request)
    users = user_profiles.get_all_users()
    return {"success": True, "users": users}
