"""
Authentication endpoints - login and JWKS.
"""
from fastapi import APIRouter, Depends, status, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import jwt

from app.database import get_db
from app.schemas.response import ApiResponse, TypedApiResponse
from app.schemas.auth import TokenRequest, TokenResult, JWKS, DecodedToken
from app.services.auth_service import authenticate_user, generate_jwt_token, get_jwks, verify_and_decode_token, generate_temporary_registration_token
from app.utils.response import success_response, error_response
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", 
    response_model=TypedApiResponse[TokenResult]
)
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
    - Password minimum length: 8 characters
    """
    # Authenticate user with email and password
    account = authenticate_user(db, credentials.email, credentials.password)
    
    # Raise 401 Unauthorized if credentials are invalid
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )
    
    # Generate JWT token with all user claims
    token_result = generate_jwt_token(account, db)
    
    # Return success response with token
    response = success_response(
        message="Token issued.",
        data=token_result.model_dump(),
        code=status.HTTP_200_OK
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.post("/register", 
    response_model=TypedApiResponse[TokenResult],
    summary="Register and get temporary token",
    description="Issues a temporary token with limited permissions for initial setup"
)
def register(credentials: TokenRequest):
    """
    Register and issue temporary JWT token.
    
    **Registration Flow:**
    1. Validates email and password format (no database lookup)
    2. Generates RS256-signed JWT with 15-minute TTL
    3. Includes fixed permissions for initial setup operations
    
    **Token Claims:**
    - Standard: `sub`, `iss`, `aud`, `iat`, `exp`, `jti` (UUID v7)
    - Custom: `organizationId` (empty), `roles` (empty), `permissions` (fixed)
    
    **Fixed Permissions:**
    - create_user: Create new user accounts
    - create_employee: Create employee records
    - create_organization: Create organization records
    - read_business_types: Read business type data
    
    **Response:**
    - Returns token string, type, and expiration timestamp
    - Token expires in 15 minutes
    
    **Security:**
    - This is a public endpoint (no authentication required)
    - Token has limited permissions and short expiration
    - No database validation - format validation only
    """
    # Generate temporary registration token with fixed permissions
    token_result = generate_temporary_registration_token(credentials.email)
    
    # Return success response with token
    response = success_response(
        message="Registration token issued.",
        data=token_result.model_dump(),
        code=status.HTTP_201_CREATED
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.get("/jwks", response_model=TypedApiResponse[JWKS])
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
    jwks_data = get_jwks()
    response = success_response(
        message="JWKS retrieved successfully.",
        data=jwks_data.model_dump(),
        code=status.HTTP_200_OK
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))


@router.get("/me", response_model=TypedApiResponse[DecodedToken])
async def verify_token(current_user: DecodedToken = Depends(get_current_user)):
    """
    Verify JWT token and return decoded payload.
    
    This endpoint validates the JWT signature and returns all claims
    contained in the token if validation is successful.
    
    **Authentication:**
    - Requires `Authorization` header with format: `Bearer <token>`
    - Token signature is verified using the public key
    - Token expiration is checked
    - Issuer and audience are validated
    
    **Response:**
    - Returns decoded token payload with all claims
    - Includes user ID, organization ID, roles, and permissions
    
    **Error Responses:**
    - 401: Missing or malformed Authorization header
    - 401: Invalid token signature
    - 401: Token has expired
    - 401: Invalid issuer or audience
    """
    # The authentication dependency handles all token validation
    # and provides the decoded token as current_user
    response = success_response(
        message="Token verified successfully.",
        data=current_user.model_dump(),
        code=status.HTTP_200_OK
    )
    return JSONResponse(status_code=response.code, content=response.model_dump(mode='json'))
