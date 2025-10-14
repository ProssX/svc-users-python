"""
Standard response schemas following Confluence standard.
All API responses use this format for consistency.
"""
from typing import Optional, Any, List, Dict
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """
    Standard API response format.
    
    Fields:
        status: 'success' or 'error'
        code: HTTP status code or internal error code
        message: Human-readable message
        data: Response payload (can be object, list, or null)
        errors: List of error details (for validation errors)
        meta: Additional metadata (pagination, context, etc.)
    """
    status: str  # "success" | "error"
    code: int
    message: str
    data: Optional[Any] = None
    errors: Optional[List[Dict[str, str]]] = None
    meta: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "message": "Operation completed successfully",
                "data": {"id": "123", "name": "example"},
                "errors": None,
                "meta": None
            }
        }
