"""
Authentication schemas for JWT login and JWKS.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tokenType": "Bearer",
                "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImF1dGgtMjAyNS0xMC0yMiJ9.eyJzdWIiOiIwMTkzMmU1Zi04YjJhLTdhMWMtOWY4ZS0zYzRiNWQ2ZTdmOGEiLCJvcmdhbml6YXRpb25JZCI6IjAxOTMyZTVmLThiMmEtN2ExYy05ZjhlLTNjNGI1ZDZlN2Y4YiIsImlzcyI6Imh0dHBzOi8vYXBpLmV4YW1wbGUuY29tIiwiYXVkIjoiaHR0cHM6Ly9hcGkuZXhhbXBsZS5jb20iLCJpYXQiOjE3Mjk1OTM2MDAsImV4cCI6MTczMDE5ODQwMCwianRpIjoiMDE5MzJlNWYtOGIyYS03YTFjLTlmOGUtM2M0YjVkNmU3ZjhjIiwicm9sZXMiOlsiQWRtaW4iXSwicGVybWlzc2lvbnMiOlsidXNlcnM6Y3JlYXRlIiwidXNlcnM6cmVhZCIsInVzZXJzOnVwZGF0ZSIsInVzZXJzOmRlbGV0ZSJdfQ.signature",
                "expiresAt": "2025-10-29T12:00:00Z"
            }
        }
    )


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
    publicKey: str = Field(..., description="Public key in base64-encoded PEM format")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "kty": "RSA",
                "kid": "auth-2025-10-22",
                "use": "sig",
                "alg": "RS256",
                "n": "sXQ0V3eZb0i2F8lYt7zj3V7p9jYj6Jm0JmR2Y3xKvLmNoPqRsTuVwXyZ1AbCdEfGhIjKlMnOpQrStUvWxYz",
                "e": "AQAB",
                "publicKey": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF3TXlWY0dQYzlyMGdheEQ0MXBSSQo0QWlBZ2lRczVpOFI2bDNFWDBvRGhiSDZsUzJpYndRRDBQZzNOMWpxNGViOTRGam1hZG0zNXQyUFM4UlU4cUZrCng5RVphdm5XaHFpa2tJd1lZdVFPZGRlTGxTNVFuY1d3RDBScmxVWE1wVk92Z2MvbHNJL05PQk9OaGllTlNYZXkKVDNlTjhxWkF5cEF6WkpWckNOWDlZZVVEQzUrdHIvdUc1djgxaXlLcmNFUjI3cXU2amVqNnFzTkJxaUNqMDFzZwp6VFpxa3BFUk5Oc2dBZTVjbVNUWE1kQzhRL3p0TEgxeEx6R3Bzbng2R0ZuNTNDRk85OTk3N1VldjRxbVFXR3pFCmhna21yb016OHpMa0xNYURaV2JiUGg5ZWtpSHdSNlArSDVLQVN5d3djTHpxMExiZzJEaDlaQjBmUmNXaWFSTzUKUFFJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=="
            }
        }
    )


class JWKS(BaseModel):
    """
    JSON Web Key Set - collection of public keys.
    Used for GET /auth/jwks endpoint.
    """
    keys: List[JWK] = Field(..., description="Array of JSON Web Keys")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keys": [
                    {
                        "kty": "RSA",
                        "kid": "auth-2025-10-22",
                        "use": "sig",
                        "alg": "RS256",
                        "n": "sXQ0V3eZb0i2F8lYt7zj3V7p9jYj6Jm0JmR2Y3xKvLmNoPqRsTuVwXyZ1AbCdEfGhIjKlMnOpQrStUvWxYz",
                        "e": "AQAB",
                        "publicKey": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF3TXlWY0dQYzlyMGdheEQ0MXBSSQo0QWlBZ2lRczVpOFI2bDNFWDBvRGhiSDZsUzJpYndRRDBQZzNOMWpxNGViOTRGam1hZG0zNXQyUFM4UlU4cUZrCng5RVphdm5XaHFpa2tJd1lZdVFPZGRlTGxTNVFuY1d3RDBScmxVWE1wVk92Z2MvbHNJL05PQk9OaGllTlNYZXkKVDNlTjhxWkF5cEF6WkpWckNOWDlZZVVEQzUrdHIvdUc1djgxaXlLcmNFUjI3cXU2amVqNnFzTkJxaUNqMDFzZwp6VFpxa3BFUk5Oc2dBZTVjbVNUWE1kQzhRL3p0TEgxeEx6R3Bzbng2R0ZuNTNDRk85OTk3N1VldjRxbVFXR3pFCmhna21yb016OHpMa0xNYURaV2JiUGg5ZWtpSHdSNlArSDVLQVN5d3djTHpxMExiZzJEaDlaQjBmUmNXaWFSTzUKUFFJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=="
                    }
                ]
            }
        }
    )


class DecodedToken(BaseModel):
    """
    Decoded JWT token payload.
    Used for GET /auth/me endpoint response.
    """
    sub: str = Field(..., description="Subject (User ID)")
    organizationId: str = Field(..., description="Organization ID")
    iss: str = Field(..., description="Issuer")
    aud: str = Field(..., description="Audience")
    iat: int = Field(..., description="Issued at timestamp (epoch)")
    exp: int = Field(..., description="Expiration timestamp (epoch)")
    jti: str = Field(..., description="JWT ID (UUID v7)")
    roles: List[str] = Field(default_factory=list, description="User roles")
    permissions: List[str] = Field(default_factory=list, description="User permissions")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sub": "01932e5f-8b2a-7a1c-9f8e-3c4b5d6e7f8a",
                "organizationId": "01932e5f-8b2a-7a1c-9f8e-3c4b5d6e7f8b",
                "iss": "https://api.example.com",
                "aud": "https://api.example.com",
                "iat": 1729593600,
                "exp": 1730198400,
                "jti": "01932e5f-8b2a-7a1c-9f8e-3c4b5d6e7f8c",
                "roles": ["Admin"],
                "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "permissions:read"]
            }
        }
    )
