"""
Permission schemas for request/response validation.
"""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


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
    """Schema for permission response with realistic examples."""
    id: UUID = Field(..., description="Unique permission identifier")
    created_at: datetime = Field(..., description="Permission creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "users:create",
                "id": "18e6d529-e8b1-4b48-aebc-d19b4e627e15",
                "created_at": "2025-10-22T00:58:32.178170",
                "updated_at": "2025-10-22T00:58:32.178172"
            }
        }
    )
