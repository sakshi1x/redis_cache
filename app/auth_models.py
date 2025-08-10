from pydantic import BaseModel
from typing import Optional


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


class EmployeeProfile(BaseModel):
    """Extended employee profile model"""
    employee_id: str
    username: str
    department: str
    role: str
    questions_asked: int
    login_count: int
    last_login: int
    created_at: int
    status: str


class UserStats(BaseModel):
    """User statistics model"""
    questions_asked: int
    login_count: int
    last_login: int
    created_at: int


class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool
    message: str
    employee: Optional[Employee] = None
    profile: Optional[EmployeeProfile] = None


class AskRequest(BaseModel):
    """Ask question request model"""
    question: str


class AskResponse(BaseModel):
    """Ask question response model"""
    success: bool
    answer: str
    employee: Employee
    user_stats: Optional[UserStats] = None


class ProfileUpdateRequest(BaseModel):
    """Profile update request model"""
    department: Optional[str] = None
    role: Optional[str] = None


class ProfileResponse(BaseModel):
    """Profile response model"""
    success: bool
    message: str
    profile: Optional[EmployeeProfile] = None
