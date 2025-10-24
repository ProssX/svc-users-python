"""
Authentication dependencies for FastAPI routes.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
import jwt

from app.schemas.auth import DecodedToken
from app.services.auth_service import verify_and_decode_token


async def get_current_user(authorization: str = Header(..., include_in_schema=False)) -> DecodedToken:
    """
    Extract and validate JWT token from Authorization header.
    
    This dependency validates the JWT token and returns the decoded user context.
    It handles missing, invalid, and expired tokens with appropriate HTTP errors.
    
    Args:
        authorization: Authorization header value (expected format: "Bearer <token>")
    
    Returns:
        DecodedToken: User context with permissions and claims
    
    Raises:
        HTTPException: 401 for authentication errors
    """
    # Check if Authorization header is present
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required"
        )
    
    # Check if header starts with "Bearer "
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )
    
    # Extract token from header
    token = authorization[7:]  # Remove "Bearer " prefix
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required"
        )
    
    try:
        # Verify and decode the JWT token
        decoded_token = verify_and_decode_token(token)
        return decoded_token
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer"
        )
    
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token audience"
        )
    
    except Exception as e:
        # Catch any other JWT-related errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[DecodedToken]:
    """
    Optional authentication dependency for endpoints that can work with or without auth.
    
    This dependency attempts to validate a JWT token if present, but doesn't raise
    an error if the token is missing. It only raises errors for invalid tokens.
    
    Args:
        authorization: Optional Authorization header value
    
    Returns:
        DecodedToken if valid token is provided, None if no token provided
    
    Raises:
        HTTPException: 401 for invalid tokens (but not for missing tokens)
    """
    if not authorization:
        return None
    
    # If authorization header is present, validate it using the same logic
    # as get_current_user, but don't require it
    try:
        return await get_current_user(authorization)
    except HTTPException:
        # Re-raise the exception for invalid tokens
        raise