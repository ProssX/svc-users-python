"""
Account schemas for request/response validation.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
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
    """Schema for account response (without password)."""
    # Entity identifier (UUID) - present in responses
    entity_id: UUID = Field(..., description="Unique entity identifier for this account")
    organization_id: UUID = Field(..., description="Organization this account belongs to")
    role_id: UUID = Field(..., description="Role assigned to this account")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class AccountWithRole(AccountResponse):
    """Schema for account response with role details included."""
    role: RoleResponse

    class Config:
        from_attributes = True
