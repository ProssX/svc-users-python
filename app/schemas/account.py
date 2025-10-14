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
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 characters)")
    role_id: UUID = Field(..., description="Role ID to assign to this account")


class AccountUpdate(BaseModel):
    """Schema for updating an account."""
    role_id: Optional[UUID] = Field(None, description="New role ID")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="New password")


class AccountResponse(AccountBase):
    """Schema for account response (without password)."""
    role_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountWithRole(AccountResponse):
    """Schema for account response with role details included."""
    role: RoleResponse

    class Config:
        from_attributes = True
