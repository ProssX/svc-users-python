"""
Permission schemas for request/response validation.
"""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """Base permission schema with shared fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Permission name (e.g., 'users.create')")


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating a permission."""
    name: str = Field(..., min_length=1, max_length=100)


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
