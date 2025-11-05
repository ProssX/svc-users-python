"""
Authorization dependencies for FastAPI routes.
"""
from typing import List, Callable
from fastapi import Depends, HTTPException, status

from app.schemas.auth import DecodedToken
from app.dependencies.auth import get_current_user


def require_permissions(required_permissions: List[str]) -> Callable:
    """
    Factory function that returns a FastAPI dependency for permission-based authorization.
    
    This function creates a dependency that validates the current user has all required
    permissions. It first authenticates the user using get_current_user, then checks
    if the user's permissions include all required permissions.
    
    Args:
        required_permissions: List of permission strings that the user must have
                            (e.g., ["accounts:read", "accounts:update"])
    
    Returns:
        FastAPI dependency function that returns the authenticated user if authorized
    
    Raises:
        HTTPException: 401 for authentication errors (from get_current_user)
        HTTPException: 403 for authorization errors (insufficient permissions)
    
    Example:
        @router.get("/accounts")
        def list_accounts(
            current_user: DecodedToken = Depends(require_permissions(["accounts:read"]))
        ):
            # current_user is available here with verified permissions
            pass
    """
    async def permission_dependency(
        current_user: DecodedToken = Depends(get_current_user)
    ) -> DecodedToken:
        """
        Dependency that checks if the authenticated user has required permissions.
        
        Args:
            current_user: Authenticated user from get_current_user dependency
        
        Returns:
            DecodedToken: The authenticated user if they have required permissions
        
        Raises:
            HTTPException: 403 if user lacks any required permissions
        """
        # Check if user has all required permissions
        user_permissions = set(current_user.permissions)
        missing_permissions = []
        
        for permission in required_permissions:
            if permission not in user_permissions:
                missing_permissions.append(permission)
        
        if missing_permissions:
            # User is missing some required permissions
            if len(missing_permissions) == 1:
                detail = f"Missing required permission: {missing_permissions[0]}"
            else:
                detail = f"Missing required permissions: {', '.join(missing_permissions)}"
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail
            )
        
        # User has all required permissions
        return current_user
    
    return permission_dependency


def check_permissions(required_permissions: List[str]) -> Callable:
    """
    Factory function that returns a permission checker that assumes user is already authenticated.
    
    This is designed to work with global authentication where get_current_user is already
    called at the router level, avoiding duplicate authentication prompts in OpenAPI.
    
    Args:
        required_permissions: List of permission strings that the user must have
    
    Returns:
        Function that checks permissions for an already authenticated user
    
    Raises:
        HTTPException: 403 for authorization errors (insufficient permissions)
    """
    def permission_checker(current_user: DecodedToken) -> DecodedToken:
        """
        Check if the authenticated user has required permissions.
        
        Args:
            current_user: Already authenticated user
        
        Returns:
            DecodedToken: The authenticated user if they have required permissions
        
        Raises:
            HTTPException: 403 if user lacks any required permissions
        """
        # Check if user has all required permissions
        user_permissions = set(current_user.permissions)
        missing_permissions = []
        
        for permission in required_permissions:
            if permission not in user_permissions:
                missing_permissions.append(permission)
        
        if missing_permissions:
            # User is missing some required permissions
            if len(missing_permissions) == 1:
                detail = f"Missing required permission: {missing_permissions[0]}"
            else:
                detail = f"Missing required permissions: {', '.join(missing_permissions)}"
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail
            )
        
        # User has all required permissions
        return current_user
    
    return permission_checker


def require_permissions(required_permissions: List[str]) -> Callable:
    """
    Same as require_permissions but hidden from OpenAPI documentation.
    
    Factory function that returns a FastAPI dependency for permission-based authorization
    that doesn't appear in the OpenAPI schema. The authentication and authorization logic
    remains exactly the same.
    
    Args:
        required_permissions: List of permission strings that the user must have
                            (e.g., ["accounts:read", "accounts:update"])
    
    Returns:
        FastAPI dependency function that returns the authenticated user if authorized
    
    Raises:
        HTTPException: 401 for authentication errors
        HTTPException: 403 for authorization errors (insufficient permissions)
    """
    async def permission_dependency(
        current_user: DecodedToken = Depends(get_current_user)
    ) -> DecodedToken:
        """
        Dependency that checks if the authenticated user has required permissions.
        
        Args:
            current_user: Authenticated user from get_current_user dependency
        
        Returns:
            DecodedToken: The authenticated user if they have required permissions
        
        Raises:
            HTTPException: 403 if user lacks any required permissions
        """
        # Check if user has all required permissions
        user_permissions = set(current_user.permissions)
        missing_permissions = []
        
        for permission in required_permissions:
            if permission not in user_permissions:
                missing_permissions.append(permission)
        
        if missing_permissions:
            # User is missing some required permissions
            if len(missing_permissions) == 1:
                detail = f"Missing required permission: {missing_permissions[0]}"
            else:
                detail = f"Missing required permissions: {', '.join(missing_permissions)}"
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail
            )
        
        # User has all required permissions
        return current_user
    
    return permission_dependency