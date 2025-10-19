"""
Authentication endpoints - login and JWKS.
"""
from fastapi import APIRouter, Depends, status, HTTPException, Header
from sqlalchemy.orm import Session
import jwt

from app.database import get_db
from app.schemas.response import ApiResponse
from app.schemas.auth import TokenRequest, TokenResult, JWKS, DecodedToken
from app.services.auth_service import authenticate_user, generate_jwt_token, get_jwks, verify_and_decode_token
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


@router.get("/me", response_model=ApiResponse, status_code=status.HTTP_200_OK)
def verify_token(authorization: str = Header(...)):
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
    # Check if Authorization header is present and starts with "Bearer "
    if not authorization or not authorization.startswith("Bearer "):
        return error_response(
            message="Missing or malformed Authorization header. Expected format: 'Bearer <token>'",
            code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Extract token from "Bearer <token>"
    token = authorization.split(" ")[1]
    
    try:
        # Verify signature and decode token
        decoded_token = verify_and_decode_token(token)
        
        # Return success response with decoded token
        return success_response(
            message="Token verified successfully.",
            data=decoded_token.model_dump(),
            code=status.HTTP_200_OK
        )
    
    except jwt.ExpiredSignatureError:
        return error_response(
            message="Token has expired.",
            code=status.HTTP_401_UNAUTHORIZED
        )
    
    except jwt.InvalidIssuerError:
        return error_response(
            message="Invalid token issuer.",
            code=status.HTTP_401_UNAUTHORIZED
        )
    
    except jwt.InvalidAudienceError:
        return error_response(
            message="Invalid token audience.",
            code=status.HTTP_401_UNAUTHORIZED
        )
    
    except jwt.InvalidTokenError as e:
        return error_response(
            message=f"Invalid token: {str(e)}",
            code=status.HTTP_401_UNAUTHORIZED
        )
    
    except Exception as e:
        return error_response(
            message=f"Token verification failed: {str(e)}",
            code=status.HTTP_401_UNAUTHORIZED
        )
