# Design Document

## Overview

The `/auth/register` endpoint will be added to the existing authentication system to issue temporary tokens with specific permissions for initial setup operations. The endpoint will follow the existing FastAPI patterns and integrate with the current JWT token generation system.

## Architecture

The registration endpoint will be implemented as a new route in the existing `app/routers/v1/auth.py` file, leveraging the current authentication service architecture:

- **Router Layer**: New POST `/auth/register` endpoint in `auth.py`
- **Service Layer**: New function in `auth_service.py` for temporary token generation
- **Schema Layer**: New request/response schemas in `auth.py`

## Components and Interfaces

### 1. Request Schema
**Reuse existing `TokenRequest`** from `app/schemas/auth.py`:
```python
# Already exists - no new schema needed
class TokenRequest(BaseModel):
    email: EmailStr
    password: str
```

### 2. Response Schema
**Reuse existing `TokenResult`** from `app/schemas/auth.py`:
```python
# Already exists - no new schema needed
class TokenResult(BaseModel):
    tokenType: str = "Bearer"
    token: str
    expiresAt: str
```

### 3. Service Function
**New function in `auth_service.py`**:
```python
def generate_temporary_registration_token(email: str) -> TokenResult:
    # Reuse existing JWT generation logic from generate_jwt_token()
    # Override expiration to 15 minutes
    # Override permissions to: create_user, create_employee, create_organization, read_business_types
    # Use email as subject instead of account ID
```

### 4. Router Endpoint
**New endpoint in `app/routers/v1/auth.py`**:
```python
@router.post("/register", 
    response_model=TypedApiResponse[TokenResult], 
    status_code=status.HTTP_201_CREATED,
    summary="Register and get temporary token",
    description="Issues a temporary token with limited permissions for initial setup"
)
def register(credentials: TokenRequest, db: Session = Depends(get_db)):
    # Validate email/password format (no database lookup)
    # Call generate_temporary_registration_token(credentials.email)
    # Return TokenResult using existing success_response pattern
```

### 5. OpenAPI Documentation
Following existing patterns in the auth router:
- **Summary**: "Register and get temporary token"
- **Description**: Detailed explanation of temporary token purpose and permissions
- **Request Body**: Reuse `TokenRequest` schema documentation
- **Response**: Reuse `TypedApiResponse[TokenResult]` with 201 status
- **Tags**: ["Auth"] (same as other auth endpoints)
- **Security**: Public endpoint (no authentication required)

## Data Models

**Reuse existing JWT token structure** from `generate_jwt_token()` with modifications:
- **Expiration**: 15 minutes instead of 7 days (`timedelta(minutes=15)`)
- **Permissions**: Fixed array `["create_user", "create_employee", "create_organization", "read_business_types"]`
- **Subject**: Email address instead of account entity_id
- **Organization ID**: Empty string or null (no organization context)
- **Roles**: Empty array (no role context)
- **Claims**: Reuse all standard JWT claims (iss, aud, iat, exp, jti)

## Error Handling

Following existing patterns:
- **400 Bad Request**: Invalid request data
- **500 Internal Server Error**: Token generation failures
- **201 Created**: Successful registration with token