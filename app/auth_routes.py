from fastapi import APIRouter, Request, Response, HTTPException, Query
from app.auth_models import (
    EmployeeSignup, EmployeeLogin, AuthResponse, Employee, AskRequest, AskResponse,
    EmployeeProfile, UserStats, ProfileUpdateRequest, ProfileResponse,
    QuestionHistory, UserAnalytics, GlobalAnalytics, CategoryAnalytics, TimeBasedAnalytics,
    AnalyticsResponse, HistoryResponse, SearchRequest, SearchResponse
)
from app.session import get_session_data, set_session_data
from app.user_profiles import user_profiles
from app.question_analytics import question_analytics
from typing import Optional

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
    """Enhanced ask question with Redis Streams and Sorted Sets analytics"""
    
    # Check authentication
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Create employee object
    employee = Employee(
        employee_id=session_data["employee_id"],
        username=session_data["username"]
    )
    
    # Generate response
    answer = f"Hello {employee.username} (ID: {employee.employee_id}), you asked: '{ask_data.question}'. This is a simple response."
    
    # Log question event to Redis Stream
    stream_id = question_analytics.log_question_event(
        employee_id=session_data["employee_id"],
        question=ask_data.question,
        response=answer,
        category=ask_data.category,
        difficulty=ask_data.difficulty
    )
    
    # Increment questions asked counter in Redis Hash
    user_profiles.increment_questions_asked(session_data["employee_id"])
    
    # Get user stats for response
    user_stats_data = user_profiles.get_user_stats(session_data["employee_id"])
    user_stats = None
    if user_stats_data:
        user_stats = UserStats(**user_stats_data)
    
    # Get recent question history
    question_history_data = question_analytics.get_user_question_history(session_data["employee_id"], count=5)
    question_history = [QuestionHistory(**item) for item in question_history_data]
    
    return AskResponse(
        success=True,
        answer=answer,
        employee=employee,
        user_stats=user_stats,
        question_history=question_history
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


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_user_analytics(
    request: Request,
    start_time: Optional[int] = Query(None, description="Start timestamp"),
    end_time: Optional[int] = Query(None, description="End timestamp")
):
    """Get detailed user analytics from Redis Sorted Sets"""
    
    # Check authentication
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get user analytics from Redis Sorted Sets
    analytics_data = question_analytics.get_user_analytics(
        session_data["employee_id"], 
        start_time=start_time, 
        end_time=end_time
    )
    
    if not analytics_data:
        raise HTTPException(status_code=404, detail="User analytics not found")
    
    analytics = UserAnalytics(**analytics_data)
    
    return AnalyticsResponse(
        success=True,
        message="User analytics retrieved successfully",
        analytics=analytics
    )


@router.get("/history", response_model=HistoryResponse)
async def get_question_history(
    request: Request,
    count: int = Query(10, description="Number of questions to retrieve", ge=1, le=100)
):
    """Get question history from Redis Streams"""
    
    # Check authentication
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get question history from Redis Streams
    history_data = question_analytics.get_user_question_history(session_data["employee_id"], count=count)
    
    if not history_data:
        return HistoryResponse(
            success=True,
            message="No question history found",
            history=[]
        )
    
    history = [QuestionHistory(**item) for item in history_data]
    
    return HistoryResponse(
        success=True,
        message="Question history retrieved successfully",
        history=history
    )


@router.post("/search", response_model=SearchResponse)
async def search_questions(request: Request, search_request: SearchRequest):
    """Search questions in user's history"""
    
    # Check authentication
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Search questions in Redis Streams
    search_results = question_analytics.search_questions(
        session_data["employee_id"], 
        search_request.search_term
    )
    
    if not search_results:
        return SearchResponse(
            success=True,
            message="No matching questions found",
            results=[]
        )
    
    results = [QuestionHistory(**item) for item in search_results]
    
    return SearchResponse(
        success=True,
        message=f"Found {len(results)} matching questions",
        results=results
    )


@router.get("/analytics/time-based", response_model=AnalyticsResponse)
async def get_time_based_analytics(
    request: Request,
    hours: int = Query(24, description="Time period in hours", ge=1, le=168)
):
    """Get time-based analytics"""
    
    # Check authentication
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get time-based analytics
    time_analytics = question_analytics.get_time_based_analytics(session_data["employee_id"], hours=hours)
    
    if not time_analytics:
        raise HTTPException(status_code=404, detail="Time-based analytics not found")
    
    return AnalyticsResponse(
        success=True,
        message=f"Time-based analytics for last {hours} hours",
        analytics=UserAnalytics(**time_analytics)
    )


@router.get("/analytics/global", response_model=AnalyticsResponse)
async def get_global_analytics(
    start_time: Optional[int] = Query(None, description="Start timestamp"),
    end_time: Optional[int] = Query(None, description="End timestamp")
):
    """Get global analytics (admin endpoint)"""
    
    # Get global analytics
    global_analytics = question_analytics.get_global_analytics(start_time=start_time, end_time=end_time)
    
    if not global_analytics:
        raise HTTPException(status_code=404, detail="Global analytics not found")
    
    return AnalyticsResponse(
        success=True,
        message="Global analytics retrieved successfully",
        analytics=UserAnalytics(**global_analytics)
    )


@router.get("/analytics/category/{category}", response_model=AnalyticsResponse)
async def get_category_analytics(
    category: str,
    start_time: Optional[int] = Query(None, description="Start timestamp"),
    end_time: Optional[int] = Query(None, description="End timestamp")
):
    """Get analytics for specific category"""
    
    # Get category analytics
    category_analytics = question_analytics.get_category_analytics(
        category, 
        start_time=start_time, 
        end_time=end_time
    )
    
    if not category_analytics:
        raise HTTPException(status_code=404, detail=f"Category analytics for '{category}' not found")
    
    return AnalyticsResponse(
        success=True,
        message=f"Category analytics for '{category}' retrieved successfully",
        analytics=UserAnalytics(**category_analytics)
    )
