from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional

from app.models import AskRequest, AskResponse, ErrorResponse
from app.services import QuestionService

# Create router instance
router = APIRouter()


@router.post(
    "/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question",
    description="Submit a question and receive a response. Requires user-name and employee-id headers.",
    responses={
        200: {"description": "Successful response", "model": AskResponse},
        400: {"description": "Bad request - missing or invalid headers", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse}
    }
)
async def ask_question(
    request: AskRequest,
    user_name: Optional[str] = Header(None, alias="user-name", description="User's name"),
    employee_id: Optional[str] = Header(None, alias="employee-id", description="Employee ID")
):
    """
    Ask a question and receive a response.
    
    This endpoint requires:
    - user-name header: The name of the user
    - employee-id header: The employee ID of the user
    - question in request body: The question to be answered
    
    Returns a structured response with the user's information and the answer.
    """
    # Validate headers
    is_valid, error_message = QuestionService.validate_headers(user_name, employee_id)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Process the question
    response = QuestionService.process_question(
        question=request.question,
        user_name=user_name,
        employee_id=employee_id
    )
    
    # Return structured response
    return AskResponse(
        user_name=user_name,
        employee_id=employee_id,
        question=request.question,
        response=response,
        status="success"
    )


@router.get(
    "/health",
    summary="Health check",
    description="Simple health check endpoint to verify the API is running"
)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy", "message": "API is running successfully"}
