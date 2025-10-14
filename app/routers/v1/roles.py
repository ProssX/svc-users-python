"""
Role endpoints - CRUD operations for roles and permission assignments.
"""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.response import ApiResponse
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleWithPermissions, AssignPermissions
from app.services import role_service
from app.utils.response import success_response, error_response, not_found_response

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("", response_model=ApiResponse, status_code=201)
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db)
):
    """Create a new role."""
    try:
        # Check if role already exists
        existing = role_service.get_role_by_name(db, role.name)
        if existing:
            return error_response(
                message="Role with this name already exists",
                code=409
            )
        
        db_role = role_service.create_role(db, role)
        return success_response(
            message="Role created successfully",
            data=RoleResponse.model_validate(db_role).model_dump(),
            code=201
        )
    except IntegrityError:
        db.rollback()
        return error_response(
            message="Database integrity error",
            code=500
        )


@router.get("", response_model=ApiResponse)
def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all roles."""
    roles = role_service.get_roles(db, skip=skip, limit=limit)
    return success_response(
        message="Roles retrieved successfully",
        data=[RoleWithPermissions.model_validate(r).model_dump() for r in roles],
        meta={"total": len(roles)}
    )


@router.get("/{role_id}", response_model=ApiResponse)
def get_role(
    role_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific role by ID with its permissions."""
    db_role = role_service.get_role(db, role_id)
    if not db_role:
        return not_found_response("Role")
    
    return success_response(
        message="Role retrieved successfully",
        data=RoleWithPermissions.model_validate(db_role).model_dump()
    )


@router.patch("/{role_id}", response_model=ApiResponse)
def update_role(
    role_id: UUID,
    role_update: RoleUpdate,
    db: Session = Depends(get_db)
):
    """Update a role."""
    try:
        db_role = role_service.update_role(db, role_id, role_update)
        if not db_role:
            return not_found_response("Role")
        
        return success_response(
            message="Role updated successfully",
            data=RoleResponse.model_validate(db_role).model_dump()
        )
    except IntegrityError:
        db.rollback()
        return error_response(
            message="Role with this name already exists",
            code=409
        )


@router.delete("/{role_id}", response_model=ApiResponse)
def delete_role(
    role_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a role."""
    success = role_service.delete_role(db, role_id)
    if not success:
        return not_found_response("Role")
    
    return success_response(
        message="Role deleted successfully",
        code=200
    )


@router.post("/{role_id}/permissions", response_model=ApiResponse)
def assign_permissions(
    role_id: UUID,
    permissions: AssignPermissions,
    db: Session = Depends(get_db)
):
    """Assign permissions to a role. Replaces existing permissions."""
    db_role = role_service.assign_permissions_to_role(db, role_id, permissions.permission_ids)
    if not db_role:
        return not_found_response("Role")
    
    return success_response(
        message="Permissions assigned successfully",
        data=RoleWithPermissions.model_validate(db_role).model_dump()
    )


@router.delete("/{role_id}/permissions/{permission_id}", response_model=ApiResponse)
def remove_permission(
    role_id: UUID,
    permission_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove a specific permission from a role."""
    db_role = role_service.remove_permission_from_role(db, role_id, permission_id)
    if not db_role:
        return not_found_response("Role")
    
    return success_response(
        message="Permission removed successfully",
        data=RoleWithPermissions.model_validate(db_role).model_dump()
    )
