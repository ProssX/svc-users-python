"""
Role service - business logic for role operations.
"""
from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.permission import Permission
from app.schemas.role import RoleCreate, RoleUpdate


def create_role(db: Session, role: RoleCreate) -> Role:
    """Create a new role."""
    db_role = Role(name=role.name, description=role.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_role(db: Session, role_id: UUID) -> Optional[Role]:
    """Get role by ID."""
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Get role by name."""
    return db.query(Role).filter(Role.name == name).first()


def get_roles(db: Session, page: int = 1, page_size: int = 10) -> tuple[List[Role], int]:
    """
    Get list of roles with page-based pagination.
    
    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Tuple of (list of roles, total count)
    """
    query = db.query(Role)
    total = query.count()
    
    # Calculate offset from page number
    offset = (page - 1) * page_size
    roles = query.offset(offset).limit(page_size).all()
    
    return roles, total


def update_role(db: Session, role_id: UUID, role_update: RoleUpdate) -> Optional[Role]:
    """Update a role."""
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    if role_update.name is not None:
        db_role.name = role_update.name
    if role_update.description is not None:
        db_role.description = role_update.description
    
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: UUID) -> bool:
    """Delete a role."""
    db_role = get_role(db, role_id)
    if not db_role:
        return False
    
    db.delete(db_role)
    db.commit()
    return True


def assign_permissions_to_role(db: Session, role_id: UUID, permission_ids: List[UUID]) -> Optional[Role]:
    """
    Add multiple permissions to a role.
    Skips permissions that are already assigned.
    """
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    # Get current permission IDs
    current_permission_ids = {p.id for p in db_role.permissions}
    
    # Filter out permissions that are already assigned
    new_permission_ids = [pid for pid in permission_ids if pid not in current_permission_ids]
    
    if new_permission_ids:
        # Get new permissions by IDs
        new_permissions = db.query(Permission).filter(Permission.id.in_(new_permission_ids)).all()
        
        # Add new permissions to existing ones
        db_role.permissions.extend(new_permissions)
        db.commit()
        db.refresh(db_role)
    
    return db_role


def remove_permissions_from_role(db: Session, role_id: UUID, permission_ids: List[UUID]) -> Optional[Role]:
    """Remove multiple permissions from a role."""
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    # Convert permission_ids to set for faster lookup
    permission_ids_set = set(permission_ids)
    
    # Filter out permissions to be removed
    db_role.permissions = [p for p in db_role.permissions if p.id not in permission_ids_set]
    
    db.commit()
    db.refresh(db_role)
    return db_role
