"""
Role endpoints - CRUD operations for roles and permission assignments.
"""
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.response import ApiResponse, TypedApiResponse, PaginationMeta
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleWithPermissions, AssignPermissions
from app.schemas.auth import DecodedToken
from app.services import role_service
from app.dependencies.permissions import require_permissions
from app.utils.response import success_response, error_response, not_found_response

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("", 
    response_model=TypedApiResponse[RoleResponse]
)
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["roles:create"]))
):
    """Create a new role."""
    
    try:
        # Check if role already exists
        existing = role_service.get_role_by_name(db, role.name)
        if existing:
            response = error_response(
                message="Role with this name already exists",
                code=409
            )
            return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
        
        db_role = role_service.create_role(db, role)
        response = success_response(
            message="Role created successfully",
            data=RoleResponse.model_validate(db_role).model_dump(),
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


@router.get("", 
    response_model=TypedApiResponse[List[RoleWithPermissions]]
)
def list_roles(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["roles:read"]))
):
    """
    Get list of all roles with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (default: 10)
    """
    roles, total_items = role_service.get_roles(db, page=page, page_size=page_size)
    
    # Calculate total pages
    import math
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    
    response = success_response(
        message="Roles retrieved successfully",
        data=[RoleWithPermissions.model_validate(r).model_dump() for r in roles],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages
        ).model_dump()
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.get("/by-name/{role_name}", 
    response_model=TypedApiResponse[RoleWithPermissions]
)
def get_role_by_name(
    role_name: str,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["roles:read"]))
):
    """Get a specific role by name with its permissions."""
    db_role = role_service.get_role_by_name(db, role_name)
    if not db_role:
        response = not_found_response("Role")
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    
    response = success_response(
        message="Role retrieved successfully",
        data=RoleWithPermissions.model_validate(db_role).model_dump()
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.get("/{role_id}", 
    response_model=TypedApiResponse[RoleWithPermissions]
)
def get_role(
    role_id: UUID,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["roles:read"]))
):
    """Get a specific role by ID with its permissions."""
    db_role = role_service.get_role(db, role_id)
    if not db_role:
        response = not_found_response("Role")
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    
    response = success_response(
        message="Role retrieved successfully",
        data=RoleWithPermissions.model_validate(db_role).model_dump()
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.patch("/{role_id}", 
    response_model=TypedApiResponse[RoleResponse]
)
def update_role(
    role_id: UUID,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["roles:update"]))
):
    """Update a role."""
    try:
        db_role = role_service.update_role(db, role_id, role_update)
        if not db_role:
            response = not_found_response("Role")
            return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
        
        response = success_response(
            message="Role updated successfully",
            data=RoleResponse.model_validate(db_role).model_dump()
        )
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    except IntegrityError:
        db.rollback()
        response = error_response(
            message="Role with this name already exists",
            code=409
        )
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.delete("/{role_id}", 
    response_model=TypedApiResponse[None]
)
def delete_role(
    role_id: UUID,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["roles:delete"]))
):
    """Delete a role."""
    success = role_service.delete_role(db, role_id)
    if not success:
        response = not_found_response("Role")
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    
    response = success_response(
        message="Role deleted successfully",
        code=200
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.post("/{role_id}/permissions", 
    response_model=TypedApiResponse[RoleWithPermissions]
)
def assign_permissions(
    role_id: UUID,
    permissions: AssignPermissions,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["roles:update"]))
):
    """Add permissions to a role. Skips permissions that are already assigned."""
    db_role = role_service.assign_permissions_to_role(db, role_id, permissions.permission_ids)
    if not db_role:
        response = not_found_response("Role")
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    
    response = success_response(
        message="Permissions added successfully",
        data=RoleWithPermissions.model_validate(db_role).model_dump()
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.delete("/{role_id}/permissions", 
    response_model=TypedApiResponse[RoleWithPermissions]
)
def remove_permissions(
    role_id: UUID,
    permissions: AssignPermissions,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["roles:update"]))
):
    """Remove multiple permissions from a role."""
    db_role = role_service.remove_permissions_from_role(db, role_id, permissions.permission_ids)
    if not db_role:
        response = not_found_response("Role")
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    
    response = success_response(
        message="Permissions removed successfully",
        data=RoleWithPermissions.model_validate(db_role).model_dump()
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))