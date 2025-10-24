"""
Global exception handlers for the FastAPI application.
"""
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.schemas.response import ValidationErrorDetail


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors and return them in our standard format.
    """
    errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body' or 'query'
        errors.append(ValidationErrorDetail(
            field=field_path,
            error=error["msg"]
        ).model_dump())
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "code": 422,
            "message": "Validation error",
            "data": None,
            "errors": errors,
            "meta": None
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions and return them in our standard format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
            "errors": None,
            "meta": None
        }
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app.
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)