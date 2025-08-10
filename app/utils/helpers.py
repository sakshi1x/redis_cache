from typing import Optional, Dict, Any, List
from fastapi import Request, HTTPException
from app.core.session import get_session_data
from app.models.auth import Employee


def require_authentication(request: Request) -> Dict[str, Any]:
    """Require authentication and return session data"""
    session_data = get_session_data(request)
    if not session_data or not session_data.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    return session_data


def get_authenticated_employee(request: Request) -> Employee:
    """Get authenticated employee from session"""
    session_data = require_authentication(request)
    return Employee(
        employee_id=session_data["employee_id"],
        username=session_data["username"]
    )


def build_success_response(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build a standardized success response"""
    response = {"success": True, "message": message}
    if data:
        response.update(data)
    return response


def build_error_response(message: str, error_code: int = 400) -> Dict[str, Any]:
    """Build a standardized error response"""
    return {"success": False, "message": message, "error_code": error_code}


def validate_time_range(start_time: Optional[int], end_time: Optional[int]) -> bool:
    """Validate time range parameters"""
    if start_time is not None and end_time is not None:
        return start_time <= end_time
    return True


def sanitize_search_term(search_term: str) -> str:
    """Sanitize search term for safe processing"""
    return search_term.strip().lower() if search_term else ""


def format_redis_key(pattern: str, **kwargs) -> str:
    """Format Redis key using pattern and parameters"""
    return pattern.format(**kwargs)


def convert_numeric_fields(data: Dict[str, Any], 
                          numeric_fields: List[str]) -> Dict[str, Any]:
    """Convert string fields to integers where appropriate"""
    result = data.copy()
    for field in numeric_fields:
        if field in result and result[field]:
            try:
                result[field] = int(result[field])
            except (ValueError, TypeError):
                result[field] = 0
    return result


def get_pagination_params(skip: int = 0, limit: int = 10, max_limit: int = 100) -> tuple[int, int]:
    """Get validated pagination parameters"""
    skip = max(0, skip)
    limit = min(max(1, limit), max_limit)
    return skip, limit


def validate_category(category: str, allowed_categories: List[str]) -> str:
    """Validate and return category, defaulting to first allowed category if invalid"""
    return category if category in allowed_categories else allowed_categories[0]


def validate_difficulty(difficulty: str, allowed_difficulties: List[str]) -> str:
    """Validate and return difficulty, defaulting to first allowed difficulty if invalid"""
    return difficulty if difficulty in allowed_difficulties else allowed_difficulties[0]


def group_by_field(items: List[Dict[str, Any]], field: str) -> Dict[str, List[Dict[str, Any]]]:
    """Group items by a specific field"""
    grouped = {}
    for item in items:
        key = item.get(field, "unknown")
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    return grouped


def count_by_field(items: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    """Count items by a specific field"""
    counts = {}
    for item in items:
        key = item.get(field, "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def filter_by_time_range(items: List[Dict[str, Any]], 
                        timestamp_field: str,
                        start_time: Optional[int] = None,
                        end_time: Optional[int] = None) -> List[Dict[str, Any]]:
    """Filter items by time range"""
    if start_time is None and end_time is None:
        return items
    
    filtered = []
    for item in items:
        timestamp = item.get(timestamp_field, 0)
        if start_time is not None and timestamp < start_time:
            continue
        if end_time is not None and timestamp > end_time:
            continue
        filtered.append(item)
    
    return filtered


def sort_by_timestamp(items: List[Dict[str, Any]], 
                     timestamp_field: str = "timestamp",
                     reverse: bool = True) -> List[Dict[str, Any]]:
    """Sort items by timestamp"""
    return sorted(items, key=lambda x: x.get(timestamp_field, 0), reverse=reverse)


def limit_results(items: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    """Limit the number of results"""
    return items[:limit] if limit > 0 else items
