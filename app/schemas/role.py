"""
Role schemas for request/response validation.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.permission import PermissionResponse


class RoleBase(BaseModel):
    """Base role schema with shared fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Role name")
    description: Optional[str] = Field(None, max_length=255, description="Role description")


class RoleCreate(RoleBase):
    """Schema for creating a new role."""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class RoleResponse(RoleBase):
    """Schema for role response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleWithPermissions(RoleResponse):
    """Schema for role response with permissions included."""
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class AssignPermissions(BaseModel):
    """Schema for assigning permissions to a role."""
    permission_ids: List[UUID] = Field(..., min_length=1, description="List of permission IDs to assign")
