"""
Authentication schemas for JWT login and JWKS.
"""
from typing import List
from pydantic import BaseModel, EmailStr, Field


class TokenRequest(BaseModel):
    """
    Login request with email and password.
    Used for POST /auth/login endpoint.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="User password (min 8 characters)"
    )


class TokenResult(BaseModel):
    """
    JWT token response - minimal format.
    Only returns token and expiration; all claims are inside the JWT.
    """
    tokenType: str = Field(
        default="Bearer", 
        description="Token type (always 'Bearer')"
    )
    token: str = Field(
        ..., 
        description="RS256-signed JWT with all user claims"
    )
    expiresAt: str = Field(
        ..., 
        description="Token expiration timestamp in ISO 8601 format"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tokenType": "Bearer",
                "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImF1dGgtMjAyNS0xMC0xNSJ9...",
                "expiresAt": "2025-10-22T12:00:00Z"
            }
        }


class JWK(BaseModel):
    """
    JSON Web Key - represents a single public key.
    Used in JWKS for JWT signature verification.
    """
    kty: str = Field(default="RSA", description="Key type")
    kid: str = Field(..., description="Key ID for key rotation")
    use: str = Field(default="sig", description="Key usage (signature)")
    alg: str = Field(default="RS256", description="Algorithm")
    n: str = Field(..., description="RSA modulus (base64url-encoded)")
    e: str = Field(..., description="RSA exponent (base64url-encoded)")

    class Config:
        json_schema_extra = {
            "example": {
                "kty": "RSA",
                "kid": "auth-2025-10-15",
                "use": "sig",
                "alg": "RS256",
                "n": "sXQ0V3eZb0i2F8lYt7zj3V7p9jYj6Jm0JmR2Y3x...",
                "e": "AQAB"
            }
        }


class JWKS(BaseModel):
    """
    JSON Web Key Set - collection of public keys.
    Used for GET /auth/jwks endpoint.
    """
    keys: List[JWK] = Field(..., description="Array of JSON Web Keys")

    class Config:
        json_schema_extra = {
            "example": {
                "keys": [
                    {
                        "kty": "RSA",
                        "kid": "auth-2025-10-15",
                        "use": "sig",
                        "alg": "RS256",
                        "n": "sXQ0V3eZb0i2F8lYt7zj3V7p9jYj6Jm0JmR2Y3x...",
                        "e": "AQAB"
                    }
                ]
            }
        }
