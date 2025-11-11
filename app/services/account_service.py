"""
Account service - business logic for account operations.
"""
import uuid
import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate
from app.services.auth_service import hash_password
from app.utils.organizations_client import update_employee_has_account

# Configure logging
logger = logging.getLogger(__name__)


async def create_account(db: Session, account: AccountCreate, auth_token: str) -> Account:
    """
    Create a new account with hashed password.
    
    First updates the employee's hasAccount attribute in Organizations Service,
    then creates the account in the database. This order ensures data consistency.
    
    Args:
        db: Database session
        account: Account creation data
        auth_token: JWT token for authenticating with Organizations Service
        
    Returns:
        Account: Created account object
        
    Raises:
        Exception: If Organizations Service update fails (prevents account creation)
    """
    # STEP 1: Update employee hasAccount in Organizations Service FIRST
    # If this fails, we don't create the account (ensures consistency)
    try:
        await update_employee_has_account(
            organization_id=account.organization_id,
            employee_id=account.entity_id,
            has_account=True,
            auth_token=auth_token
        )
    except Exception as e:
        logger.error(f"Failed to update employee {account.entity_id} in Organizations Service: {str(e)}")
        raise Exception("Unable to update employee in Organizations Service. Account creation aborted.")
    
    # STEP 2: Create account in database (only if Organizations Service update succeeded)
    # Hash the password before storing
    hashed_password = hash_password(account.password)
    
    db_account = Account(
        email=account.email,
        entity_id=account.entity_id,  # Use entity_id from request
        password_hash=hashed_password,
        role_id=account.role_id,
        organization_id=account.organization_id
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    logger.info(f"Successfully created account for employee {account.entity_id}")
    return db_account


def get_account_by_email(db: Session, email: str, organization_id: UUID) -> Optional[Account]:
    """Get account by email (primary key) filtered by organization."""
    return db.query(Account).filter(
        Account.email == email,
        Account.organization_id == organization_id
    ).first()


def get_account_by_entity_id(db: Session, entity_id: UUID, organization_id: UUID) -> Optional[Account]:
    """Get account by entity_id filtered by organization."""
    return db.query(Account).filter(
        Account.entity_id == entity_id,
        Account.organization_id == organization_id
    ).first()


def get_accounts(db: Session, organization_id: UUID, page: int = 1, page_size: int = 10) -> tuple[List[Account], int]:
    """
    Get list of accounts filtered by organization with page-based pagination.
    
    Args:
        db: Database session
        organization_id: Organization UUID to filter accounts
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Tuple of (list of accounts, total count)
    """
    query = db.query(Account).filter(Account.organization_id == organization_id)
    total = query.count()
    
    # Calculate offset from page number
    offset = (page - 1) * page_size
    accounts = query.offset(offset).limit(page_size).all()
    
    return accounts, total


def update_account(db: Session, email: str, account_update: AccountUpdate, organization_id: UUID) -> Optional[Account]:
    """Update an account filtered by organization."""
    db_account = get_account_by_email(db, email, organization_id)
    if not db_account:
        return None
    
    # Update fields if provided
    if account_update.role_id is not None:
        db_account.role_id = account_update.role_id
    if account_update.password is not None:
        db_account.password_hash = hash_password(account_update.password)
    
    db.commit()
    db.refresh(db_account)
    return db_account


async def delete_account(db: Session, email: str, organization_id: UUID, auth_token: str) -> bool:
    """
    Delete an account filtered by organization.
    
    First deletes the account from the database, then updates the employee's
    hasAccount attribute in Organizations Service. If the Organizations Service
    update fails, the account is still deleted (logged as warning for reconciliation).
    
    Args:
        db: Database session
        email: Email of the account to delete
        organization_id: Organization UUID
        auth_token: JWT token for authenticating with Organizations Service
        
    Returns:
        bool: True if account was deleted, False if account not found
    """
    db_account = get_account_by_email(db, email, organization_id)
    if not db_account:
        return False
    
    # Store entity_id before deletion
    entity_id = db_account.entity_id
    
    # STEP 1: Delete account from database first
    db.delete(db_account)
    db.commit()
    logger.info(f"Successfully deleted account {email} for employee {entity_id}")
    
    # STEP 2: Update employee hasAccount in Organizations Service
    # If this fails, we log but don't rollback (account is already deleted)
    try:
        await update_employee_has_account(
            organization_id=organization_id,
            employee_id=entity_id,
            has_account=False,
            auth_token=auth_token
        )
    except Exception as e:
        logger.warning(
            f"Failed to update employee {entity_id} in Organizations Service after account deletion: {str(e)}. "
            f"Account was deleted but employee hasAccount attribute may be out of sync."
        )
        # Don't raise - account is already deleted, this can be reconciled later
    
    return True
