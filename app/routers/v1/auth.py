"""
Authentication endpoints - login and JWKS.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.response import ApiResponse
from app.schemas.auth import TokenRequest, TokenResult, JWKS
from app.services.auth_service import authenticate_user, generate_jwt_token, get_jwks
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=ApiResponse, status_code=status.HTTP_200_OK)
def login(
    credentials: TokenRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and issue JWT token.
    
    **Authentication Flow:**
    1. Validates email and password credentials
    2. Generates RS256-signed JWT with 7-day TTL
    3. Includes user roles and permissions in token claims
    
    **Token Claims:**
    - Standard: `sub`, `iss`, `aud`, `iat`, `exp`, `jti` (UUID v7)
    - Custom: `organizationId`, `roles`, `permissions`
    
    **Response:**
    - Returns token string, type, and expiration timestamp
    - All user information is encoded in the JWT (decode to access)
    
    **Security:**
    - This is a public endpoint (no authentication required)
    - Rate limiting should be implemented in production
    - Password minimum length: 12 characters
    """
    # Authenticate user with email and password
    account = authenticate_user(db, credentials.email, credentials.password)
    
    # Return 401 Unauthorized if credentials are invalid
    if not account:
        return error_response(
            message="Invalid credentials.",
            code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT token with all user claims
    token_result = generate_jwt_token(account, db)
    
    # Return success response with token
    return success_response(
        message="Token issued.",
        data=token_result.model_dump(),
        code=status.HTTP_200_OK
    )


@router.get("/jwks", response_model=JWKS, status_code=status.HTTP_200_OK)
def get_jwks_endpoint():
    """
    Get JSON Web Key Set (JWKS).
    
    Returns the public keys used to verify JWT signatures.
    
    **Usage:**
    - Clients should cache keys by `kid` (Key ID)
    - Refresh keys when encountering an unknown `kid`
    - Use these keys to verify JWT signatures (RS256 algorithm)
    
    **Key Information:**
    - Algorithm: RS256 (RSA with SHA-256)
    - Key Type: RSA
    - Usage: Signature verification
    - Format: Base64url-encoded modulus (n) and exponent (e)
    
    **Security:**
    - This is a public endpoint (no authentication required)
    - Public keys can be safely shared and distributed
    - Private key is never exposed
    """
    return get_jwks()
