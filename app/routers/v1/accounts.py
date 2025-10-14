"""
Account endpoints - CRUD operations for user accounts.
"""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.response import ApiResponse
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse, AccountWithRole
from app.services import account_service, role_service
from app.utils.response import success_response, error_response, not_found_response, validation_error_response

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=ApiResponse, status_code=201)
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


@router.get("", response_model=ApiResponse)
def list_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all accounts."""
    accounts = account_service.get_accounts(db, skip=skip, limit=limit)
    return success_response(
        message="Accounts retrieved successfully",
        data=[AccountWithRole.model_validate(a).model_dump() for a in accounts],
        meta={"total": len(accounts)}
    )


@router.get("/{account_id}", response_model=ApiResponse)
def get_account(
    account_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific account by ID."""
    db_account = account_service.get_account(db, account_id)
    if not db_account:
        return not_found_response("Account")
    
    return success_response(
        message="Account retrieved successfully",
        data=AccountWithRole.model_validate(db_account).model_dump()
    )


@router.patch("/{account_id}", response_model=ApiResponse)
def update_account(
    account_id: UUID,
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
        
        # If updating email, check if it's already taken
        if account_update.email:
            existing = account_service.get_account_by_email(db, account_update.email)
            if existing and existing.id != account_id:
                return error_response(
                    message="Email already in use",
                    code=409
                )
        
        db_account = account_service.update_account(db, account_id, account_update)
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


@router.delete("/{account_id}", response_model=ApiResponse)
def delete_account(
    account_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an account."""
    success = account_service.delete_account(db, account_id)
    if not success:
        return not_found_response("Account")
    
    return success_response(
        message="Account deleted successfully",
        code=200
    )
