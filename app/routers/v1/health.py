"""
Health check endpoint.
"""
from fastapi import APIRouter
from app.utils.response import success_response
from app.schemas.response import ApiResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=ApiResponse)
async def health_check():
    """
    Health check endpoint.
    Returns the service status and basic information.
    """
    return success_response(
        message="Service is healthy",
        data={
            "service": "Authentication Microservice",
            "status": "operational",
            "version": "1.0.0"
        }
    )
