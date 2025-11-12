# Implementation Plan

- [x] 1. Add temporary token generation service function
  - Create `generate_temporary_registration_token()` function in `app/services/auth_service.py`
  - Reuse existing JWT generation logic from `generate_jwt_token()`
  - Set 15-minute expiration using `timedelta(minutes=15)`
  - Include fixed permissions: create_user, create_employee, create_organization, read_business_types
  - Use email as subject instead of account entity_id
  - Set empty organization_id and roles array
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Implement registration endpoint
  - Add POST `/auth/register` endpoint to `app/routers/v1/auth.py`
  - Reuse existing `TokenRequest` schema for request body
  - Reuse existing `TokenResult` schema for response
  - Call `generate_temporary_registration_token()` service function
  - Return 201 status code on success
  - Use existing `success_response` pattern for response formatting
  - _Requirements: 1.1, 1.4, 1.5_

- [x] 3. Add OpenAPI documentation
  - Add comprehensive endpoint documentation with summary and description
  - Include response model `TypedApiResponse[TokenResult]`
  - Set status code to `HTTP_201_CREATED`
  - Add detailed description explaining temporary token purpose and permissions
  - Include endpoint in "Auth" tag group
  - _Requirements: 1.6_