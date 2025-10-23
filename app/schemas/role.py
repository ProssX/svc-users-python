"""
Role schemas for request/response validation.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
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
    """Schema for role response with realistic examples."""
    id: UUID = Field(..., description="Unique role identifier")
    created_at: datetime = Field(..., description="Role creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Admin",
                "description": "Administrator role with full permissions",
                "id": "d2938640-8cd4-4fe1-a3f4-8b9d4972eb2a",
                "created_at": "2025-10-22T00:58:32.178170",
                "updated_at": "2025-10-22T00:58:32.178172"
            }
        }
    )


class RoleWithPermissions(RoleResponse):
    """Schema for role response with permissions included and realistic examples."""
    permissions: List[PermissionResponse] = Field(default=[], description="List of permissions assigned to this role")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Admin",
                "description": "Administrator role with full permissions",
                "id": "d2938640-8cd4-4fe1-a3f4-8b9d4972eb2a",
                "created_at": "2025-10-22T00:58:32.178170",
                "updated_at": "2025-10-22T00:58:32.178172",
                "permissions": [
                    {
                        "name": "users:create",
                        "id": "18e6d529-e8b1-4b48-aebc-d19b4e627e15",
                        "created_at": "2025-10-22T00:58:32.178170",
                        "updated_at": "2025-10-22T00:58:32.178172"
                    },
                    {
                        "name": "users:read",
                        "id": "28f7e639-f9c2-5c59-bfcd-e2ac5f738f26",
                        "created_at": "2025-10-22T00:58:32.178170",
                        "updated_at": "2025-10-22T00:58:32.178172"
                    }
                ]
            }
        }
    )


class AssignPermissions(BaseModel):
    """Schema for assigning permissions to a role."""
    permission_ids: List[UUID] = Field(..., min_length=1, description="List of permission IDs to assign")
