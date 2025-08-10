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


class QuestionHistory(BaseModel):
    """Question history model"""
    event_id: str
    question: str
    response: str
    category: str
    difficulty: str
    timestamp: int


class UserAnalytics(BaseModel):
    """User analytics model"""
    total_questions: int
    categories: Dict[str, int]
    difficulties: Dict[str, int]
    recent_questions: List[Dict[str, Any]]


class GlobalAnalytics(BaseModel):
    """Global analytics model"""
    total_questions: int
    category_distribution: Dict[str, int]
    time_range: Optional[Dict[str, Optional[int]]] = None


class CategoryAnalytics(BaseModel):
    """Category analytics model"""
    category: str
    total_questions: int
    questions: List[Dict[str, Any]]
    time_range: Optional[Dict[str, Optional[int]]] = None


class TimeBasedAnalytics(BaseModel):
    """Time-based analytics model"""
    time_period_hours: int
    total_questions: int
    hourly_distribution: Dict[int, int]
    start_time: int
    end_time: int


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
    profile: Optional[EmployeeProfile] = None


class ProfileUpdateRequest(BaseModel):
    """Profile update request model"""
    department: Optional[str] = None
    role: Optional[str] = None


class ProfileResponse(BaseModel):
    """Profile response model"""
    success: bool
    message: str
    profile: Optional[EmployeeProfile] = None


class AnalyticsResponse(BaseModel):
    """Analytics response model"""
    success: bool
    message: str
    analytics: Optional[UserAnalytics] = None


class HistoryResponse(BaseModel):
    """Question history response model"""
    success: bool
    message: str
    history: Optional[List[QuestionHistory]] = None


class SearchRequest(BaseModel):
    """Search request model"""
    search_term: str


class SearchResponse(BaseModel):
    """Search response model"""
    success: bool
    message: str
    results: Optional[List[QuestionHistory]] = None
