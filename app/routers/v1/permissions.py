"""
Permission endpoints - CRUD operations for permissions.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.response import TypedApiResponse, PaginationMeta
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionResponse
from app.schemas.auth import DecodedToken
from app.services import permission_service
from app.dependencies.permissions import require_permissions
from app.utils.response import success_response, error_response, not_found_response

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post("", 
    response_model=TypedApiResponse[PermissionResponse]
)
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["permissions:read"]))
):
    """Create a new permission."""
    try:
        # Check if permission already exists
        existing = permission_service.get_permission_by_name(db, permission.name)
        if existing:
            response = error_response(
                message="Permission with this name already exists",
                code=409
            )
            return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
        
        db_permission = permission_service.create_permission(db, permission)
        response = success_response(
            message="Permission created successfully",
            data=PermissionResponse.model_validate(db_permission).model_dump(),
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
    response_model=TypedApiResponse[List[PermissionResponse]]
)
def list_permissions(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["permissions:read"]))
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
    
    response = success_response(
        message="Permissions retrieved successfully",
        data=[PermissionResponse.model_validate(p).model_dump() for p in permissions],
        meta=pagination_meta.model_dump()
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.get("/{permission_id}", 
    response_model=TypedApiResponse[PermissionResponse]
)
def get_permission(
    permission_id: UUID,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["permissions:read"]))
):
    """Get a specific permission by ID."""
    db_permission = permission_service.get_permission(db, permission_id)
    if not db_permission:
        response = not_found_response("Permission")
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    
    response = success_response(
        message="Permission retrieved successfully",
        data=PermissionResponse.model_validate(db_permission).model_dump()
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.patch("/{permission_id}", 
    response_model=TypedApiResponse[PermissionResponse]
)
def update_permission(
    permission_id: UUID,
    permission_update: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["permissions:update"]))
):
    """Update a permission."""
    try:
        db_permission = permission_service.update_permission(db, permission_id, permission_update)
        if not db_permission:
            response = not_found_response("Permission")
            return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
        
        response = success_response(
            message="Permission updated successfully",
            data=PermissionResponse.model_validate(db_permission).model_dump()
        )
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    except IntegrityError:
        db.rollback()
        response = error_response(
            message="Permission with this name already exists",
            code=409
        )
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.delete("/{permission_id}", 
    response_model=TypedApiResponse[None]
)
def delete_permission(
    permission_id: UUID,
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["permissions:delete"]))
):
    """Delete a permission."""
    success = permission_service.delete_permission(db, permission_id)
    if not success:
        response = not_found_response("Permission")
        return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
    
    response = success_response(
        message="Permission deleted successfully",
        code=200
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))