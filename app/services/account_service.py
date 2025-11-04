"""
Account service - business logic for account operations.
"""
import uuid
from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate
from app.services.auth_service import hash_password


def create_account(db: Session, account: AccountCreate) -> Account:
    """Create a new account with hashed password."""
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
    return db_account


def get_account_by_email(db: Session, email: str, organization_id: UUID) -> Optional[Account]:
    """Get account by email (primary key) filtered by organization."""
    return db.query(Account).filter(
        Account.email == email,
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


def delete_account(db: Session, email: str, organization_id: UUID) -> bool:
    """Delete an account filtered by organization."""
    db_account = get_account_by_email(db, email, organization_id)
    if not db_account:
        return False
    
    db.delete(db_account)
    db.commit()
    return True
