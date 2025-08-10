from fastapi import APIRouter, Request, Response, HTTPException
from app.auth_models import (
    EmployeeSignup, EmployeeLogin, AuthResponse, Employee, AskRequest, AskResponse,
    EmployeeProfile, UserStats, ProfileUpdateRequest, ProfileResponse
)
from app.session import get_session_data, set_session_data
from app.user_profiles import user_profiles

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(request: Request, response: Response, signup_data: EmployeeSignup):
    """Employee signup endpoint with Redis Hash profiles"""
    
    # Check if username already exists using Redis
    existing_user = user_profiles.get_user_by_username(signup_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user profile in Redis Hash
    success = user_profiles.create_user_profile(
        employee_id=signup_data.employee_id,
        username=signup_data.username,
        password=signup_data.password,
        department=signup_data.department,
        role=signup_data.role
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create user profile")
    
    # Create employee object for session
    employee = Employee(
        employee_id=signup_data.employee_id,
        username=signup_data.username
    )
    
    # Store employee in session
    session_data = {
        "employee_id": employee.employee_id,
        "username": employee.username,
        "password": signup_data.password,
        "authenticated": True
    }
    
    set_session_data(request, response, session_data)
    
    # Get created profile for response
    profile_data = user_profiles.get_user_profile(signup_data.employee_id)
    profile = None
    if profile_data:
        profile = EmployeeProfile(**profile_data)
    
    return AuthResponse(
        success=True,
        message="Signup successful",
        employee=employee,
        profile=profile
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: Request, response: Response, login_data: EmployeeLogin):
    """Employee login endpoint with Redis Hash profiles"""
    
    # Check if employee exists and password is correct using Redis
    user_data = user_profiles.get_user_by_username(login_data.username)
    if not user_data or user_data["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update login activity in Redis Hash
    user_profiles.update_login_activity(user_data["employee_id"])
    
    # Create employee object for session
    employee = Employee(
        employee_id=user_data["employee_id"],
        username=user_data["username"]
    )
    
    # Store employee in session
    session_data = {
        "employee_id": employee.employee_id,
        "username": employee.username,
        "password": user_data["password"],
        "authenticated": True
    }
    
    set_session_data(request, response, session_data)
    
    # Get updated profile for response
    profile_data = user_profiles.get_user_profile(user_data["employee_id"])
    profile = None
    if profile_data:
        profile = EmployeeProfile(**profile_data)
    
    return AuthResponse(
        success=True,
        message="Login successful",
        employee=employee,
        profile=profile
    )


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: Request, ask_data: AskRequest):
    """Ask a question - requires authentication with Redis Hash tracking"""
    
    # Check authentication
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Create employee object
    employee = Employee(
        employee_id=session_data["employee_id"],
        username=session_data["username"]
    )
    
    # Increment questions asked counter in Redis Hash
    user_profiles.increment_questions_asked(session_data["employee_id"])
    
    # Simple answer logic
    answer = f"Hello {employee.username} (ID: {employee.employee_id}), you asked: '{ask_data.question}'. This is a simple response."
    
    # Get user stats for response
    user_stats_data = user_profiles.get_user_stats(session_data["employee_id"])
    user_stats = None
    if user_stats_data:
        user_stats = UserStats(**user_stats_data)
    
    return AskResponse(
        success=True,
        answer=answer,
        employee=employee,
        user_stats=user_stats
    )


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(request: Request):
    """Get user profile from Redis Hash"""
    
    # Check authentication
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get user profile from Redis Hash
    profile_data = user_profiles.get_user_profile(session_data["employee_id"])
    if not profile_data:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    profile = EmployeeProfile(**profile_data)
    
    return ProfileResponse(
        success=True,
        message="Profile retrieved successfully",
        profile=profile
    )


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(request: Request, profile_update: ProfileUpdateRequest):
    """Update user profile in Redis Hash"""
    
    # Check authentication
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Update profile fields in Redis Hash
    if profile_update.department:
        user_profiles.update_user_field(session_data["employee_id"], "department", profile_update.department)
    
    if profile_update.role:
        user_profiles.update_user_field(session_data["employee_id"], "role", profile_update.role)
    
    # Get updated profile
    profile_data = user_profiles.get_user_profile(session_data["employee_id"])
    if not profile_data:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    profile = EmployeeProfile(**profile_data)
    
    return ProfileResponse(
        success=True,
        message="Profile updated successfully",
        profile=profile
    )


@router.get("/stats", response_model=ProfileResponse)
async def get_user_stats(request: Request):
    """Get user statistics from Redis Hash"""
    
    # Check authentication
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get user stats from Redis Hash
    stats_data = user_profiles.get_user_stats(session_data["employee_id"])
    if not stats_data:
        raise HTTPException(status_code=404, detail="User stats not found")
    
    # Create profile object with stats
    profile_data = user_profiles.get_user_profile(session_data["employee_id"])
    if profile_data:
        profile = EmployeeProfile(**profile_data)
    else:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    return ProfileResponse(
        success=True,
        message="User statistics retrieved successfully",
        profile=profile
    )
