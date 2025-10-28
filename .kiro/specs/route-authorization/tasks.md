# Implementation Plan

- [x] 1. Create authentication dependencies
  - Create `app/dependencies/__init__.py` file
  - Create `app/dependencies/auth.py` with `get_current_user` function that validates JWT tokens
  - Add error handling for missing, invalid, and expired tokens
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Create authorization dependencies  
  - Create `app/dependencies/permissions.py` with `require_permissions` factory function
  - Implement permission checking logic that validates user permissions from JWT claims
  - Add HTTP 403 error handling for insufficient permissions
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 3. Configure public routes and global security
  - Add `PUBLIC_ROUTES` list to `app/config.py` with health and auth endpoints
  - Update `app/main.py` to add global Bearer token security scheme to OpenAPI
  - Configure security requirements to exclude public routes from authentication
  - _Requirements: 2.1, 2.2, 2.3, 4.1, 4.2, 4.3_

- [ ] 4. Update auth routes with proper protection
  - Update `/auth/me` endpoint to use authentication dependency
  - Ensure `/auth/login`, `/auth/register`, `/auth/jwks` remain public
  - Verify auth routes work correctly with new dependencies
  - _Requirements: 2.3_

- [ ] 5. Protect all routes with appropriate permissions
  - Update `app/routers/v1/accounts.py` to use `require_permissions` dependency:
    - POST `/accounts` requires `accounts:create` permission
    - GET `/accounts` requires `accounts:read` permission
    - GET `/accounts/{email}` requires `accounts:read` permission
    - PATCH `/accounts/{email}` requires `accounts:update` permission
    - DELETE `/accounts/{email}` requires `accounts:delete` permission
  - Update `app/routers/v1/roles.py` to use `require_permissions` dependency:
    - POST `/roles` requires `roles:create` permission
    - GET `/roles` requires `roles:read` permission
    - GET `/roles/{id}` requires `roles:read` permission
    - PATCH `/roles/{id}` requires `roles:update` permission
    - DELETE `/roles/{id}` requires `roles:delete` permission
  - Update `app/routers/v1/permissions.py` to use `require_permissions` dependency:
    - POST `/permissions` requires `permissions:create` permission
    - GET `/permissions` requires `permissions:read` permission
    - GET `/permissions/{id}` requires `permissions:read` permission
    - PATCH `/permissions/{id}` requires `permissions:update` permission
    - DELETE `/permissions/{id}` requires `permissions:delete` permission
  - _Requirements: 1.1, 1.2, 3.1, 3.2_

- [ ] 6. Verify OpenAPI documentation
  - Test that Swagger UI shows global "Authorize" button
  - Verify protected endpoints show lock icons
  - Verify public endpoints remain unmarked
  - Test that setting token once applies to all protected endpoints
  - _Requirements: 4.1, 4.2, 4.3, 4.4_