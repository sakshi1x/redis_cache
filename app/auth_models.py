from pydantic import BaseModel
from typing import Optional


class EmployeeSignup(BaseModel):
    """Employee signup model"""
    employee_id: str
    username: str
    password: str


class EmployeeLogin(BaseModel):
    """Employee login model"""
    username: str
    password: str


class Employee(BaseModel):
    """Employee model"""
    employee_id: str
    username: str


class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool
    message: str
    employee: Optional[Employee] = None


class AskRequest(BaseModel):
    """Ask question request model"""
    question: str


class AskResponse(BaseModel):
    """Ask question response model"""
    success: bool
    answer: str
    employee: Employee
