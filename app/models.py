from pydantic import BaseModel, Field
from typing import Optional


class AskRequest(BaseModel):
    """Request model for the /ask endpoint"""
    question: str = Field(..., description="User's question", min_length=1, max_length=1000)


class AskResponse(BaseModel):
    """Response model for the /ask endpoint"""
    user_name: str = Field(..., description="Name of the user")
    employee_id: str = Field(..., description="Employee ID of the user")
    question: str = Field(..., description="Original question asked")
    response: str = Field(..., description="Response to the question")
    status: str = Field(default="success", description="Status of the request")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    status: str = Field(default="error", description="Status of the request")
