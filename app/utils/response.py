"""
Response utility functions.
Helper functions to create standardized API responses.
"""
from typing import Any, Optional, List, Dict
from app.schemas.response import ApiResponse


def success_response(
    message: str,
    data: Any = None,
    code: int = 200,
    meta: Optional[Dict[str, Any]] = None
) -> ApiResponse:
    """
    Create a success response.
    
    Args:
        message: Human-readable success message
        data: Response data (object, list, or None)
        code: HTTP status code (default: 200)
        meta: Additional metadata (optional)
    
    Returns:
        ApiResponse with status='success'
    """
    return ApiResponse(
        status="success",
        code=code,
        message=message,
        data=data,
        errors=None,
        meta=meta
    )


def error_response(
    message: str,
    code: int = 500,
    errors: Optional[List[Dict[str, str]]] = None
) -> ApiResponse:
    """
    Create an error response.
    
    Args:
        message: Human-readable error message
        code: HTTP status code (default: 500)
        errors: List of detailed errors (for validation errors)
    
    Returns:
        ApiResponse with status='error'
    """
    return ApiResponse(
        status="error",
        code=code,
        message=message,
        data=None,
        errors=errors,
        meta=None
    )


def validation_error_response(
    errors: List[Dict[str, str]],
    message: str = "Validation error"
) -> ApiResponse:
    """
    Create a validation error response.
    
    Args:
        errors: List of validation errors with field and error details
        message: Human-readable error message
    
    Returns:
        ApiResponse with status='error' and code=422
    """
    return error_response(
        message=message,
        code=422,
        errors=errors
    )


def not_found_response(
    resource: str = "Resource"
) -> ApiResponse:
    """
    Create a not found error response.
    
    Args:
        resource: Name of the resource that was not found
    
    Returns:
        ApiResponse with status='error' and code=404
    """
    return error_response(
        message=f"{resource} not found",
        code=404
    )
