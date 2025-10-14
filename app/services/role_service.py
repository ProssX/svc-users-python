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


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """Get list of roles with pagination."""
    return db.query(Role).offset(skip).limit(limit).all()


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
    Assign multiple permissions to a role.
    Replaces existing permissions with the new list.
    """
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    # Get all permissions by IDs
    permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
    
    # Replace role's permissions
    db_role.permissions = permissions
    db.commit()
    db.refresh(db_role)
    return db_role


def remove_permission_from_role(db: Session, role_id: UUID, permission_id: UUID) -> Optional[Role]:
    """Remove a specific permission from a role."""
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    # Find and remove the permission
    permission = next((p for p in db_role.permissions if p.id == permission_id), None)
    if permission:
        db_role.permissions.remove(permission)
        db.commit()
        db.refresh(db_role)
    
    return db_role
