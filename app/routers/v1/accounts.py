"""
Account endpoints - CRUD operations for user accounts.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.response import ApiResponse, TypedApiResponse
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse, AccountWithRole
from app.services import account_service, role_service
from app.utils.response import success_response, error_response, not_found_response, validation_error_response

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", 
    response_model=TypedApiResponse[AccountResponse], 
    status_code=201,

)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db)
):
    """Create a new account with email and password."""
    try:
        # Check if email already exists
        existing = account_service.get_account_by_email(db, account.email)
        if existing:
            return error_response(
                message="Account with this email already exists",
                code=409
            )
        
        # Check if role exists
        role = role_service.get_role(db, account.role_id)
        if not role:
            return validation_error_response(
                errors=[{"field": "role_id", "error": "Role not found"}]
            )
        
        db_account = account_service.create_account(db, account)
        return success_response(
            message="Account created successfully",
            data=AccountResponse.model_validate(db_account).model_dump(),
            code=201
        )
    except IntegrityError:
        db.rollback()
        return error_response(
            message="Database integrity error",
            code=500
        )


@router.get("", response_model=TypedApiResponse[List[AccountWithRole]])
def list_accounts(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get list of all accounts with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (default: 10)
    """
    accounts, total_items = account_service.get_accounts(db, page=page, page_size=page_size)
    
    # Calculate total pages
    import math
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    
    return success_response(
        message="Accounts retrieved successfully",
        data=[AccountWithRole.model_validate(a).model_dump() for a in accounts],
        meta={
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages
        }
    )


@router.get("/{email}", response_model=TypedApiResponse[AccountWithRole])
def get_account(
    email: str,
    db: Session = Depends(get_db)
):
    """Get a specific account by email."""
    db_account = account_service.get_account_by_email(db, email)
    if not db_account:
        return not_found_response("Account")
    
    return success_response(
        message="Account retrieved successfully",
        data=AccountWithRole.model_validate(db_account).model_dump()
    )


@router.patch("/{email}", response_model=TypedApiResponse[AccountResponse])
def update_account(
    email: str,
    account_update: AccountUpdate,
    db: Session = Depends(get_db)
):
    """Update an account."""
    try:
        # If updating role, check if it exists
        if account_update.role_id:
            role = role_service.get_role(db, account_update.role_id)
            if not role:
                return validation_error_response(
                    errors=[{"field": "role_id", "error": "Role not found"}]
                )
        
        db_account = account_service.update_account(db, email, account_update)
        if not db_account:
            return not_found_response("Account")
        
        return success_response(
            message="Account updated successfully",
            data=AccountResponse.model_validate(db_account).model_dump()
        )
    except IntegrityError:
        db.rollback()
        return error_response(
            message="Database integrity error",
            code=500
        )


@router.delete("/{email}", 
    response_model=TypedApiResponse[AccountResponse]
)
def delete_account(
    email: str,
    db: Session = Depends(get_db)
):
    """Delete an account."""
    success = account_service.delete_account(db, email)
    if not success:
        return not_found_response("Account")
    
    return success_response(
        message="Account deleted successfully",
        code=200
    )
