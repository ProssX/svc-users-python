"""
API v1 router - aggregates all v1 endpoints.
"""
from fastapi import APIRouter
from app.routers.v1 import health, permissions, roles, accounts, auth

# Create main v1 router
api_v1_router = APIRouter()

# Include all route modules
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(permissions.router)
api_v1_router.include_router(roles.router)
api_v1_router.include_router(accounts.router)
