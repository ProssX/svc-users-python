"""
Standard response schemas following Confluence standard.
All API responses use this format for consistency.
"""
from typing import Optional, Any, List, Dict, Generic, TypeVar, Union, Literal
from pydantic import BaseModel, Field, ConfigDict


# Generic type variable for typed responses
T = TypeVar('T')


class PaginationMeta(BaseModel):
    """
    Pagination metadata for list responses.
    
    Contains information about the current page, page size, and total counts
    to help clients navigate through paginated results.
    """
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total_items: int = Field(..., ge=0, description="Total number of items available")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "page_size": 10,
                "total_items": 17,
                "total_pages": 2
            }
        }
    )


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
    status: Literal["success", "error"] = Field(..., description="Response status indicating success or error")
    code: int = Field(..., description="HTTP status code or internal error code")
    message: str = Field(..., description="Human-readable message describing the operation result")
    data: Optional[Any] = Field(None, description="Response payload containing the actual data")
    errors: Optional[List[Dict[str, str]]] = Field(None, description="List of error details for validation failures")
    meta: Optional[Union[PaginationMeta, Dict[str, Any]]] = Field(None, description="Additional metadata such as pagination info")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "code": 200,
                "message": "Operation completed successfully",
                "data": {"id": "123", "name": "example"},
                "errors": None,
                "meta": None
            }
        }
    )


class ValidationErrorDetail(BaseModel):
    """
    Detailed validation error information.
    
    Contains specific information about which field failed validation
    and what the validation error was.
    """
    field: str = Field(..., description="Field name that failed validation")
    error: str = Field(..., description="Validation error message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field": "email",
                "error": "Invalid email format"
            }
        }
    )





class TypedApiResponse(BaseModel, Generic[T]):
    """
    Typed API response format for OpenAPI documentation.
    Use this when you want to specify the exact data type in responses.
    
    Provides better type safety and more accurate OpenAPI documentation
    by specifying the exact structure of the data field.
    
    Fields:
        status: 'success' or 'error'
        code: HTTP status code
        message: Human-readable message
        data: Typed response payload
        errors: List of error details (for validation errors)
        meta: Additional metadata (pagination, context, etc.)
    """
    status: Literal["success", "error"] = Field(..., description="Response status indicating success or error")
    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Human-readable message describing the operation result")
    data: Optional[T] = Field(None, description="Typed response payload containing the actual data")
    errors: Optional[List[ValidationErrorDetail]] = Field(None, description="List of detailed validation error information")
    meta: Optional[Union[PaginationMeta, Dict[str, Any]]] = Field(None, description="Additional metadata such as pagination info")

    model_config = ConfigDict(
        from_attributes=True
    )
