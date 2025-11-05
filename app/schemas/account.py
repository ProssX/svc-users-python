"""
Account schemas for request/response validation.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.schemas.role import RoleResponse


class AccountBase(BaseModel):
    """Base account schema with shared fields."""
    email: EmailStr = Field(..., description="User email address")


class AccountCreate(AccountBase):
    """Schema for creating a new account."""
    password: str = Field(..., min_length=8, max_length=72, description="User password (min 8, max 72 characters - bcrypt limit)")
    entity_id: UUID = Field(..., description="Unique entity identifier for this account")
    role_id: UUID = Field(..., description="Role ID to assign to this account")
    organization_id: UUID = Field(..., description="Organization ID to link this account")


class AccountUpdate(BaseModel):
    """Schema for updating an account."""
    role_id: Optional[UUID] = Field(None, description="New role ID")
    password: Optional[str] = Field(None, min_length=8, max_length=72, description="New password (min 8, max 72 characters - bcrypt limit)")


class AccountResponse(AccountBase):
    """Schema for account response (without password) with realistic examples."""
    # Entity identifier (UUID) - present in responses
    entity_id: UUID = Field(..., description="Unique entity identifier for this account")
    organization_id: UUID = Field(..., description="Organization this account belongs to")
    role_id: UUID = Field(..., description="Role assigned to this account")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "entity_id": "550e8400-e29b-41d4-a716-446655440000",
                "organization_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "role_id": "d2938640-8cd4-4fe1-a3f4-8b9d4972eb2a",
                "created_at": "2025-10-22T00:58:32.178170",
                "updated_at": "2025-10-22T00:58:32.178172"
            }
        }
    )


class AccountWithRole(AccountResponse):
    """Schema for account response with role details included and realistic examples."""
    role: RoleResponse = Field(..., description="Role details for this account")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "admin@example.com",
                "entity_id": "550e8400-e29b-41d4-a716-446655440000",
                "organization_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "role_id": "d2938640-8cd4-4fe1-a3f4-8b9d4972eb2a",
                "created_at": "2025-10-22T00:58:32.178170",
                "updated_at": "2025-10-22T00:58:32.178172",
                "role": {
                    "name": "Admin",
                    "description": "Administrator role with full permissions",
                    "id": "d2938640-8cd4-4fe1-a3f4-8b9d4972eb2a",
                    "created_at": "2025-10-22T00:58:32.178170",
                    "updated_at": "2025-10-22T00:58:32.178172"
                }
            }
        }
    )
