# Design Document

## Overview

This design implements a comprehensive authentication and authorization system for the FastAPI application using the existing JWT infrastructure. The system will protect all routes except designated public endpoints using permission-based access control, while providing global authentication setup in the OpenAPI documentation.

## Architecture

### Authentication Flow
1. **Token Validation**: Extract and validate JWT tokens from Authorization headers
2. **User Context**: Decode token claims to create user context with permissions
3. **Permission Check**: Verify user has required permissions for the endpoint
4. **Access Control**: Allow or deny access based on authentication and authorization results

### Components Overview
- **Authentication Dependency**: FastAPI dependency for token validation
- **Authorization Dependency**: FastAPI dependency for permission checking  
- **Public Route Configuration**: List of endpoints that bypass authentication
- **Global Security Scheme**: OpenAPI security configuration for Bearer tokens
- **Error Handling**: Consistent error responses for auth failures

## Components and Interfaces

### 1. Authentication Dependencies (`app/dependencies/auth.py`)

```python
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from app.schemas.auth import DecodedToken
from app.services.auth_service import verify_and_decode_token

async def get_current_user(authorization: str = Header(...)) -> DecodedToken:
    """Extract and validate JWT token, return user context."""
    
def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[DecodedToken]:
    """Optional authentication for endpoints that can work with or without auth."""
```

### 2. Authorization Dependencies (`app/dependencies/permissions.py`)

```python
from typing import List
from fastapi import Depends, HTTPException, status
from app.schemas.auth import DecodedToken
from app.dependencies.auth import get_current_user

def require_permissions(required_permissions: List[str]):
    """
    Factory function that returns a FastAPI dependency.
    Use this as a route dependency to enforce permission requirements.
    Raises HTTP 403 if user lacks required permissions.
    """
```

### 3. Public Route Configuration (`app/config.py`)

```python
# Add to existing settings
PUBLIC_ROUTES = [
    "/health",
    "/api/v1/health", 
    "/api/v1/auth/login",
    "/api/v1/auth/register", 
    "/api/v1/auth/jwks",
    "/docs",
    "/redoc",
    "/openapi.json"
]
```

### 4. Global Security Scheme (`app/main.py`)

```python
def custom_openapi():
    """Enhanced OpenAPI schema with global Bearer token authentication."""
    # Add security scheme definition
    # Configure global security requirements
    # Mark public endpoints as exempt
```

### 5. Route Protection Implementation

**Current Route Pattern:**
```python
@router.get("/accounts")
def list_accounts(db: Session = Depends(get_db)):
    pass
```

**Protected Route Pattern:**
```python
@router.get("/accounts")
def list_accounts(
    db: Session = Depends(get_db),
    current_user: DecodedToken = Depends(require_permissions(["accounts.read"]))
):
    # current_user is automatically available here
    # require_permissions() ensures user has "accounts.read" permission
    pass
```

## Data Models

### User Context Schema
```python
# Reuse existing DecodedToken from app/schemas/auth.py
class DecodedToken(BaseModel):
    sub: str  # User ID
    organizationId: str
    roles: List[str]
    permissions: List[str]
    # ... other JWT claims
```

### Permission Mapping
Based on existing seed data, the permission structure follows the pattern:
- `{resource}.{action}` (e.g., "accounts.read", "roles.create")
- Resources: accounts, roles, permissions
- Actions: create, read, update, delete

## Error Handling

### Authentication Errors (HTTP 401)
- Missing Authorization header
- Invalid token format
- Expired token
- Invalid signature
- Invalid issuer/audience

### Authorization Errors (HTTP 403)
- Valid token but insufficient permissions
- User lacks required permissions for endpoint

### Error Response Format
```python
# Use existing error_response utility
{
    "success": false,
    "message": "Authentication required",
    "data": null,
    "meta": null
}
```



## Implementation Plan

### Phase 1: Core Authentication
1. Create authentication dependencies
2. Configure public routes list
3. Add global security scheme to OpenAPI

### Phase 2: Route Protection
1. Update all protected routes to use authentication dependency
2. Add permission requirements to each endpoint
3. Test authentication on all routes

### Phase 3: Permission-Based Authorization
1. Implement permission checking dependency
2. Update routes with specific permission requirements
3. Test authorization with different user roles

### Phase 4: Documentation
1. Verify OpenAPI documentation shows global auth
2. Update route documentation with permission requirements