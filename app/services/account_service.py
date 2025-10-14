"""
Account service - business logic for account operations.
"""
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
        password_hash=hashed_password,
        role_id=account.role_id
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def get_account(db: Session, account_id: UUID) -> Optional[Account]:
    """Get account by ID."""
    return db.query(Account).filter(Account.id == account_id).first()


def get_account_by_email(db: Session, email: str) -> Optional[Account]:
    """Get account by email."""
    return db.query(Account).filter(Account.email == email).first()


def get_accounts(db: Session, skip: int = 0, limit: int = 100) -> List[Account]:
    """Get list of accounts with pagination."""
    return db.query(Account).offset(skip).limit(limit).all()


def update_account(db: Session, account_id: UUID, account_update: AccountUpdate) -> Optional[Account]:
    """Update an account."""
    db_account = get_account(db, account_id)
    if not db_account:
        return None
    
    # Update fields if provided
    if account_update.email is not None:
        db_account.email = account_update.email
    if account_update.role_id is not None:
        db_account.role_id = account_update.role_id
    if account_update.password is not None:
        db_account.password_hash = hash_password(account_update.password)
    
    db.commit()
    db.refresh(db_account)
    return db_account


def delete_account(db: Session, account_id: UUID) -> bool:
    """Delete an account."""
    db_account = get_account(db, account_id)
    if not db_account:
        return False
    
    db.delete(db_account)
    db.commit()
    return True
