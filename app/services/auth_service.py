"""
Authentication service for password hashing, verification, and JWT token generation.
"""
import base64
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from uuid_utils import uuid7
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.account import Account
from app.schemas.auth import TokenResult, JWK, JWKS

# Cache for loaded keys (avoid reloading from env on every request)
_private_key_cache = None
_public_key_cache = None


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    Bcrypt has a maximum password length of 72 bytes. If the password
    is longer, it will be truncated to 72 bytes before hashing.
    
    Args:
        password: Plain-text password
    
    Returns:
        Hashed password string
    """
    # Bcrypt can only handle passwords up to 72 bytes
    # Truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a hashed password.
    
    Args:
        plain_password: Plain-text password to verify
        hashed_password: Hashed password from database
    
    Returns:
        True if password matches, False otherwise
    """
    # Truncate password if longer than 72 bytes (bcrypt limit)
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Compare with hashed password
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))


def generate_uuid7() -> str:
    """
    Generate a UUID v7 (time-ordered UUID).
    
    UUID v7 is sortable and includes timestamp information,
    making it better for database indexing and debugging.
    
    Returns:
        String representation of UUID v7
    """
    return str(uuid7())


def load_private_key():
    """
    Load RSA private key from environment variable (base64-encoded PEM).
    
    The key is cached in memory to avoid repeated decoding.
    
    Returns:
        RSA private key object
    """
    global _private_key_cache
    
    if _private_key_cache is None:
        settings = get_settings()
        # Decode base64-encoded PEM from environment variable
        pem_bytes = base64.b64decode(settings.jwt_private_key)
        # Load the private key
        _private_key_cache = serialization.load_pem_private_key(
            pem_bytes,
            password=None,
            backend=default_backend()
        )
    
    return _private_key_cache


def load_public_key():
    """
    Load RSA public key from environment variable (base64-encoded PEM).
    
    The key is cached in memory to avoid repeated decoding.
    
    Returns:
        RSA public key object
    """
    global _public_key_cache
    
    if _public_key_cache is None:
        settings = get_settings()
        # Decode base64-encoded PEM from environment variable
        pem_bytes = base64.b64decode(settings.jwt_public_key)
        # Load the public key
        _public_key_cache = serialization.load_pem_public_key(
            pem_bytes,
            backend=default_backend()
        )
    
    return _public_key_cache


def authenticate_user(db: Session, email: str, password: str) -> Optional[Account]:
    """
    Authenticate a user with email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain-text password
    
    Returns:
        Account object if authentication succeeds, None otherwise
    """
    # Query account by email
    account = db.query(Account).filter(Account.email == email).first()
    
    # Return None if account doesn't exist
    if not account:
        return None
    
    # Verify password
    if not verify_password(password, account.password_hash):
        return None
    
    return account


def generate_jwt_token(account: Account, db: Session) -> TokenResult:
    """
    Generate a JWT token for an authenticated user.
    
    The token includes standard JWT claims (sub, iss, aud, iat, exp, jti)
    and custom claims (organizationId, roles, permissions).
    
    Args:
        account: Authenticated user account
        db: Database session (for loading role and permissions)
    
    Returns:
        TokenResult with token string and expiration timestamp
    """
    settings = get_settings()
    
    # Calculate timestamps
    now = datetime.utcnow()
    expiration = now + timedelta(days=settings.jwt_expiration_days)
    iat = int(now.timestamp())
    exp = int(expiration.timestamp())
    
    # Extract roles and permissions from account
    # Note: Account has a relationship to Role, and Role has a relationship to Permissions
    roles = [account.role.name] if account.role else []
    permissions = [p.name for p in account.role.permissions] if account.role else []
    
    # Build JWT payload
    payload = {
        "sub": str(account.entity_id),  # User ID
        "organizationId": str(account.organization_id),  # Organization ID
        "iss": settings.jwt_issuer,  # Issuer
        "aud": settings.jwt_audience,  # Audience
        "iat": iat,  # Issued at (epoch seconds)
        "exp": exp,  # Expires at (epoch seconds)
        "jti": generate_uuid7(),  # JWT ID (UUID v7)
        "roles": roles,  # User roles
        "permissions": permissions  # User permissions
    }
    
    # Load private key for signing
    private_key = load_private_key()
    
    # Generate JWT token with RS256 algorithm
    token = jwt.encode(
        payload,
        private_key,
        algorithm=settings.jwt_algorithm,
        headers={"kid": settings.jwt_kid}  # Key ID in header for rotation
    )
    
    # Return token result
    return TokenResult(
        tokenType="Bearer",
        token=token,
        expiresAt=expiration.isoformat() + "Z"  # ISO 8601 format with Z suffix
    )


def get_jwks() -> JWKS:
    """
    Generate JSON Web Key Set (JWKS) with current public key.
    
    This endpoint allows clients to retrieve the public key
    for verifying JWT signatures.
    
    Returns:
        JWKS object with current public key
    """
    settings = get_settings()
    public_key = load_public_key()
    
    # Extract RSA public numbers
    public_numbers = public_key.public_numbers()
    
    # Convert modulus (n) and exponent (e) to base64url format
    # This is the format required by JWKS specification
    def int_to_base64url(num: int) -> str:
        """Convert integer to base64url-encoded string."""
        # Convert to bytes with big-endian byte order
        num_bytes = num.to_bytes((num.bit_length() + 7) // 8, byteorder='big')
        # Encode to base64url (no padding)
        return base64.urlsafe_b64encode(num_bytes).decode('utf-8').rstrip('=')
    
    n = int_to_base64url(public_numbers.n)
    e = int_to_base64url(public_numbers.e)
    
    # Create JWK
    jwk = JWK(
        kty="RSA",
        kid=settings.jwt_kid,
        use="sig",
        alg=settings.jwt_algorithm,
        n=n,
        e=e
    )
    
    # Return JWKS with single key
    return JWKS(keys=[jwk])
