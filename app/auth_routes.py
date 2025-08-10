from fastapi import APIRouter, Request, Response, HTTPException
from app.auth_models import EmployeeSignup, EmployeeLogin, AuthResponse, Employee, AskRequest, AskResponse
from app.session import get_session_data, set_session_data

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Simple in-memory employee database for demo purposes
EMPLOYEES = {}


@router.post("/signup", response_model=AuthResponse)
async def signup(request: Request, response: Response, signup_data: EmployeeSignup):
    """Employee signup endpoint"""
    
    # Check if username already exists
    if signup_data.username in EMPLOYEES:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Store employee data
    EMPLOYEES[signup_data.username] = {
        "employee_id": signup_data.employee_id,
        "username": signup_data.username,
        "password": signup_data.password
    }
    
    # Create employee object for session
    employee = Employee(
        employee_id=signup_data.employee_id,
        username=signup_data.username
    )
    
    # Store employee in session (including password)
    session_data = {
        "employee_id": employee.employee_id,
        "username": employee.username,
        "password": signup_data.password,  # Store password in session
        "authenticated": True
    }
    
    set_session_data(request, response, session_data)
    
    return AuthResponse(
        success=True,
        message="Signup successful",
        employee=employee
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: Request, response: Response, login_data: EmployeeLogin):
    """Employee login endpoint"""
    
    # Check if employee exists and password is correct
    employee_data = EMPLOYEES.get(login_data.username)
    if not employee_data or employee_data["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create employee object for session
    employee = Employee(
        employee_id=employee_data["employee_id"],
        username=employee_data["username"]
    )
    
    # Store employee in session (including password)
    session_data = {
        "employee_id": employee.employee_id,
        "username": employee.username,
        "password": employee_data["password"],  # Store password in session
        "authenticated": True
    }
    
    set_session_data(request, response, session_data)
    
    return AuthResponse(
        success=True,
        message="Login successful",
        employee=employee
    )


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: Request, ask_data: AskRequest):
    """Ask a question - requires authentication"""
    
    # Check authentication
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Create employee object
    employee = Employee(
        employee_id=session_data["employee_id"],
        username=session_data["username"]
    )
    
    # Simple answer logic (you can replace this with your actual logic)
    answer = f"Hello {employee.username} (ID: {employee.employee_id}), you asked: '{ask_data.question}'. This is a simple response."
    
    return AskResponse(
        success=True,
        answer=answer,
        employee=employee
    )
