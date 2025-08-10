from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class EmployeeSignup(BaseModel):
    """Employee signup model"""
    employee_id: str
    username: str
    password: str
    department: Optional[str] = "General"
    role: Optional[str] = "Employee"


class EmployeeLogin(BaseModel):
    """Employee login model"""
    username: str
    password: str


class Employee(BaseModel):
    """Employee model"""
    employee_id: str
    username: str


class UserStats(BaseModel):
    """User statistics model"""
    questions_asked: int
    login_count: int
    last_login: int
    created_at: int


class QuestionHistory(BaseModel):
    """Question history model"""
    event_id: str
    question: str
    response: str
    category: str
    difficulty: str
    timestamp: int


class AskRequest(BaseModel):
    """Enhanced ask question request model"""
    question: str
    category: Optional[str] = "general"
    difficulty: Optional[str] = "beginner"


class AskResponse(BaseModel):
    """Enhanced ask question response model"""
    success: bool
    answer: str
    employee: Employee
    user_stats: Optional[UserStats] = None
    question_history: Optional[List[QuestionHistory]] = None


class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool
    message: str
    employee: Optional[Employee] = None
    profile: Optional[Any] = None
