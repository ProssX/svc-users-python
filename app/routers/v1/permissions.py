"""
Permission endpoints - CRUD operations for permissions.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.response import TypedApiResponse, PaginationMeta
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionResponse
from app.services import permission_service
from app.utils.response import success_response, error_response, not_found_response

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post("", 
    response_model=TypedApiResponse[PermissionResponse], 
    status_code=201
)
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db)
):
    """Create a new permission."""
    try:
        # Check if permission already exists
        existing = permission_service.get_permission_by_name(db, permission.name)
        if existing:
            return error_response(
                message="Permission with this name already exists",
                code=409
            )
        
        db_permission = permission_service.create_permission(db, permission)
        return success_response(
            message="Permission created successfully",
            data=PermissionResponse.model_validate(db_permission).model_dump(),
            code=201
        )
    except IntegrityError:
        db.rollback()
        return error_response(
            message="Database integrity error",
            code=500
        )


@router.get("", 
    response_model=TypedApiResponse[List[PermissionResponse]]
)
def list_permissions(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get list of all permissions with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (default: 10)
    """
    permissions, total_items = permission_service.get_permissions(db, page=page, page_size=page_size)
    
    # Calculate total pages
    import math
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    
    # Create pagination metadata
    pagination_meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )
    
    return success_response(
        message="Permissions retrieved successfully",
        data=[PermissionResponse.model_validate(p).model_dump() for p in permissions],
        meta=pagination_meta.model_dump()
    )


@router.get("/{permission_id}", 
    response_model=TypedApiResponse[PermissionResponse]
)
def get_permission(
    permission_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific permission by ID."""
    db_permission = permission_service.get_permission(db, permission_id)
    if not db_permission:
        return not_found_response("Permission")
    
    return success_response(
        message="Permission retrieved successfully",
        data=PermissionResponse.model_validate(db_permission).model_dump()
    )


@router.patch("/{permission_id}", 
    response_model=TypedApiResponse[PermissionResponse]
)
def update_permission(
    permission_id: UUID,
    permission_update: PermissionUpdate,
    db: Session = Depends(get_db)
):
    """Update a permission."""
    try:
        db_permission = permission_service.update_permission(db, permission_id, permission_update)
        if not db_permission:
            return not_found_response("Permission")
        
        return success_response(
            message="Permission updated successfully",
            data=PermissionResponse.model_validate(db_permission).model_dump()
        )
    except IntegrityError:
        db.rollback()
        return error_response(
            message="Permission with this name already exists",
            code=409
        )


@router.delete("/{permission_id}", 
    response_model=TypedApiResponse[None]
)
def delete_permission(
    permission_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a permission."""
    success = permission_service.delete_permission(db, permission_id)
    if not success:
        return not_found_response("Permission")
    
    return success_response(
        message="Permission deleted successfully",
        code=200
    )