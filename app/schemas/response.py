"""
Standard response schemas following Confluence standard.
All API responses use this format for consistency.
"""
from typing import Optional, Any, List, Dict, Generic, TypeVar
from pydantic import BaseModel


# Generic type variable for typed responses
T = TypeVar('T')


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


class TypedApiResponse(BaseModel, Generic[T]):
    """
    Typed API response format for OpenAPI documentation.
    Use this when you want to specify the exact data type in responses.
    
    Fields:
        status: 'success' or 'error'
        code: HTTP status code
        message: Human-readable message
        data: Typed response payload
        errors: List of error details (for validation errors)
        meta: Additional metadata (pagination, context, etc.)
    """
    status: str
    code: int
    message: str
    data: Optional[T] = None
    errors: Optional[List[Dict[str, str]]] = None
    meta: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
