"""
Account endpoints - CRUD operations for user accounts.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.response import ApiResponse, TypedApiResponse
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse, AccountWithRole
from app.schemas.auth import DecodedToken
from app.services import account_service, role_service
from app.dependencies.permissions import require_permissions
from app.utils.response import success_response, error_response, not_found_response, validation_error_response

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", 
    response_model=TypedApiResponse[AccountResponse]
)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["accounts:create"]))
):
    """Create a new account with email and password."""
    
    try:
        # Determine organization ID source: JWT token or request body (for register tokens)
        if current_user.organizationId and current_user.organizationId.strip():
            # Normal flow: Use organization from JWT token
            organization_id = UUID(current_user.organizationId)
        else:
            # Register token flow: Use organization from request body
            organization_id = account.organization_id
            
            # Validation: Register tokens can only create the first account
            # Check if any accounts already exist for this organization
            existing_accounts, total = account_service.get_accounts(db, organization_id, page=1, page_size=1)
            if total > 0:
                response = error_response(
                    message="Register token can only be used to create the first account. Organization already has accounts.",
                    code=403
                )
                return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
        
        # Check if email already exists within the organization
        existing = account_service.get_account_by_email(db, account.email, organization_id)
        if existing:
            response = error_response(
                message="Account with this email already exists",
                code=409
            )
            return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
        
        # Check if role exists
        role = role_service.get_role(db, account.role_id)
        if not role:
            response = validation_error_response(
                errors=[{"field": "role_id", "error": "Role not found"}]
            )
            return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
        
        db_account = account_service.create_account(db, account)
        response = success_response(
            message="Account created successfully",
            data=AccountResponse.model_validate(db_account).model_dump(),
            code=201
        )
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    except IntegrityError:
        db.rollback()
        response = error_response(
            message="Database integrity error",
            code=500
        )
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.get("", response_model=TypedApiResponse[List[AccountWithRole]])
def list_accounts(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["accounts:read"]))
):
    """
    Get list of accounts filtered by organization with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (default: 10)
    """
    from uuid import UUID
    
    # Extract organization ID from JWT token
    organization_id = UUID(current_user.organizationId)
    
    accounts, total_items = account_service.get_accounts(db, organization_id, page=page, page_size=page_size)
    
    # Calculate total pages
    import math
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    
    response = success_response(
        message="Accounts retrieved successfully",
        data=[AccountWithRole.model_validate(a).model_dump() for a in accounts],
        meta={
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages
        }
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.get("/{email}", response_model=TypedApiResponse[AccountWithRole])
def get_account(
    email: str,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["accounts:read"]))
):
    """Get a specific account by email within the user's organization."""
    from uuid import UUID
    
    # Extract organization ID from JWT token
    organization_id = UUID(current_user.organizationId)
    
    db_account = account_service.get_account_by_email(db, email, organization_id)
    if not db_account:
        response = not_found_response("Account")
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    
    response = success_response(
        message="Account retrieved successfully",
        data=AccountWithRole.model_validate(db_account).model_dump()
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.patch("/{email}", response_model=TypedApiResponse[AccountResponse])
def update_account(
    email: str,
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["accounts:update"]))
):
    """Update an account within the user's organization."""
    from uuid import UUID
    
    try:
        # Extract organization ID from JWT token
        organization_id = UUID(current_user.organizationId)
        
        # If updating role, check if it exists
        if account_update.role_id:
            role = role_service.get_role(db, account_update.role_id)
            if not role:
                response = validation_error_response(
                    errors=[{"field": "role_id", "error": "Role not found"}]
                )
                return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
        
        db_account = account_service.update_account(db, email, account_update, organization_id)
        if not db_account:
            response = not_found_response("Account")
            return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
        
        response = success_response(
            message="Account updated successfully",
            data=AccountResponse.model_validate(db_account).model_dump()
        )
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    except IntegrityError:
        db.rollback()
        response = error_response(
            message="Database integrity error",
            code=500
        )
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.delete("/{email}", 
    response_model=TypedApiResponse[AccountResponse]
)
def delete_account(
    email: str,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["accounts:delete"]))
):
    """Delete an account within the user's organization."""
    from uuid import UUID
    
    # Extract organization ID from JWT token
    organization_id = UUID(current_user.organizationId)
    
    success = account_service.delete_account(db, email, organization_id)
    if not success:
        response = not_found_response("Account")
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    
    response = success_response(
        message="Account deleted successfully",
        code=200
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
