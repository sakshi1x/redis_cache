from fastapi import APIRouter, Request, HTTPException, Query
from typing import Optional
from app.api.analytics.routes import RedisQuestionAnalytics
from app.utils.helpers import require_authentication, get_authenticated_employee

router = APIRouter(prefix="/analytics", tags=["Analytics"])
question_analytics = RedisQuestionAnalytics()

@router.get("/history")
async def get_question_history(
    request: Request,
    count: int = Query(10, ge=1, le=100, description="Number of questions to retrieve")
):
    """Get current user's question history"""
    employee = get_authenticated_employee(request)
    history = question_analytics.get_user_question_history(employee.employee_id, count)
    return {"success": True, "history": history}

@router.get("/user-stats")
async def get_user_analytics(
    request: Request,
    start_time: Optional[int] = Query(None, description="Start timestamp"),
    end_time: Optional[int] = Query(None, description="End timestamp")
):
    """Get current user's analytics"""
    employee = get_authenticated_employee(request)
    analytics = question_analytics.get_user_analytics(employee.employee_id, start_time, end_time)
    return {"success": True, "analytics": analytics}

@router.get("/global")
async def get_global_analytics(
    request: Request,
    start_time: Optional[int] = Query(None, description="Start timestamp"),
    end_time: Optional[int] = Query(None, description="End timestamp")
):
    """Get global analytics (admin only)"""
    require_authentication(request)
    analytics = question_analytics.get_global_analytics(start_time, end_time)
    return {"success": True, "analytics": analytics}

@router.get("/category/{category}")
async def get_category_analytics(
    request: Request,
    category: str,
    start_time: Optional[int] = Query(None, description="Start timestamp"),
    end_time: Optional[int] = Query(None, description="End timestamp")
):
    """Get analytics for a specific category"""
    require_authentication(request)
    analytics = question_analytics.get_category_analytics(category, start_time, end_time)
    return {"success": True, "analytics": analytics}

@router.get("/search")
async def search_questions(
    request: Request,
    search_term: str = Query(..., description="Search term")
):
    """Search questions for current user"""
    employee = get_authenticated_employee(request)
    results = question_analytics.search_questions(employee.employee_id, search_term)
    return {"success": True, "results": results}
