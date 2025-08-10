from fastapi import APIRouter, Request, Response, HTTPException
from app.models.auth import (
    EmployeeSignup, EmployeeLogin, AuthResponse, Employee, AskRequest, AskResponse,
    UserStats, QuestionHistory
)
from app.core.session import set_session_data
from app.api.users.routes import RedisUserProfiles
from app.api.analytics.routes import RedisQuestionAnalytics

# Initialize instances
user_profiles = RedisUserProfiles()
question_analytics = RedisQuestionAnalytics()
from app.utils.helpers import (
    require_authentication, get_authenticated_employee
)
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _create_employee_from_session(session_data: dict) -> Employee:
    """Create Employee object from session data"""
    return Employee(
        employee_id=session_data["employee_id"],
        username=session_data["username"]
    )


def _create_session_data(employee: Employee, password: str) -> dict:
    """Create session data from employee and password"""
    return {
        "employee_id": employee.employee_id,
        "username": employee.username,
        "password": password,
        "authenticated": True
    }


@router.post("/signup", response_model=AuthResponse)
async def signup(request: Request, response: Response, signup_data: EmployeeSignup):
    """Employee signup endpoint with Redis Hash profiles"""
    
    # Check if username already exists
    if user_profiles.username_exists(signup_data.username):
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
    session_data = _create_session_data(employee, signup_data.password)
    set_session_data(request, response, session_data)
    
    return AuthResponse(
        success=True,
        message="Signup successful",
        employee=employee,
        profile=None
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: Request, response: Response, login_data: EmployeeLogin):
    """Employee login endpoint with Redis Hash profiles"""
    
    # Check if employee exists and password is correct
    user_data = user_profiles.get_user_by_username(login_data.username)
    if not user_data or user_data["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update login activity
    user_profiles.update_login_activity(user_data["employee_id"])
    
    # Create employee object for session
    employee = Employee(
        employee_id=user_data["employee_id"],
        username=user_data["username"]
    )
    
    # Store employee in session
    session_data = _create_session_data(employee, user_data["password"])
    set_session_data(request, response, session_data)
    
    return AuthResponse(
        success=True,
        message="Login successful",
        employee=employee,
        profile=None
    )


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: Request, ask_data: AskRequest):
    """Enhanced ask question with Redis Streams and Sorted Sets analytics"""
    
    # Get authenticated employee
    session_data = require_authentication(request)
    employee = _create_employee_from_session(session_data)
    
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
    
    # Increment questions asked counter
    user_profiles.increment_questions_asked(session_data["employee_id"])
    
    # Get user stats for response
    user_stats_data = user_profiles.get_user_stats(session_data["employee_id"])
    user_stats = UserStats(**user_stats_data) if user_stats_data else None
    
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
