"""
Permission service - business logic for permission operations.
"""
from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    """Create a new permission."""
    db_permission = Permission(name=permission.name)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def get_permission(db: Session, permission_id: UUID) -> Optional[Permission]:
    """Get permission by ID."""
    return db.query(Permission).filter(Permission.id == permission_id).first()


def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
    """Get permission by name."""
    return db.query(Permission).filter(Permission.name == name).first()


def get_permissions(db: Session, page: int = 1, page_size: int = 10) -> tuple[List[Permission], int]:
    """
    Get list of permissions with page-based pagination.
    
    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Tuple of (list of permissions, total count)
    """
    query = db.query(Permission)
    total = query.count()
    
    # Calculate offset from page number
    offset = (page - 1) * page_size
    permissions = query.offset(offset).limit(page_size).all()
    
    return permissions, total


def update_permission(db: Session, permission_id: UUID, permission_update: PermissionUpdate) -> Optional[Permission]:
    """Update a permission."""
    db_permission = get_permission(db, permission_id)
    if not db_permission:
        return None
    
    db_permission.name = permission_update.name
    db.commit()
    db.refresh(db_permission)
    return db_permission


def delete_permission(db: Session, permission_id: UUID) -> bool:
    """Delete a permission."""
    db_permission = get_permission(db, permission_id)
    if not db_permission:
        return False
    
    db.delete(db_permission)
    db.commit()
    return True
