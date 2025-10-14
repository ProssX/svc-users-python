# Authentication Microservice (svc-users-python)

A FastAPI-based authentication microservice for user management with role-based permissions.

## 📋 Overview

This microservice provides basic authentication functionality with:
- **Account Management** - User accounts with email/password authentication
- **Role-Based Access** - Hierarchical role system
- **Permission System** - Granular permissions attached to roles
- **Standard API Responses** - Consistent response format across all endpoints

### Architecture

```
Account (1) ──→ (1) Role (1) ──→ (M) Permission
```

- An account has exactly **one role**
- A role can have **many permissions**
- A permission can be attached to **many roles** (M:M relationship)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (via Docker)

### 1. Clone & Setup

```bash
# Clone the repository
cd svc-users-python

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (defaults should work for local development)
```

### 3. Start PostgreSQL

```bash
# Start PostgreSQL in Docker
docker-compose up -d

# Verify it's running
docker-compose ps
```

### 4. Initialize Database

```bash
# Run seed script (creates tables and initial data)
python seed.py
```

This will create:
- Database tables
- Default permissions (12 permissions)
- Default roles (Admin, Manager, User)
- Sample accounts:
  - `admin@example.com` / `admin123` (Admin role)
  - `user@example.com` / `user123` (User role)

### 5. Start the Application

```bash
# Run the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

The service will be available at:
- **API**: http://localhost:8001
- **Interactive Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 📚 API Documentation

### Base URL: `/api/v1`

All responses follow this standard format:

```json
{
  "status": "success | error",
  "code": 200,
  "message": "Human-readable message",
  "data": {...} | [...] | null,
  "errors": [...] | null,
  "meta": {...} | null
}
```

### Endpoints

#### Health Check
- `GET /api/v1/health` - Service health status

#### Accounts
- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts` - List all accounts
- `GET /api/v1/accounts/{id}` - Get account by ID
- `PATCH /api/v1/accounts/{id}` - Update account
- `DELETE /api/v1/accounts/{id}` - Delete account

#### Roles
- `POST /api/v1/roles` - Create role
- `GET /api/v1/roles` - List all roles
- `GET /api/v1/roles/{id}` - Get role by ID
- `PATCH /api/v1/roles/{id}` - Update role
- `DELETE /api/v1/roles/{id}` - Delete role
- `POST /api/v1/roles/{id}/permissions` - Assign permissions to role
- `DELETE /api/v1/roles/{id}/permissions/{permission_id}` - Remove permission from role

#### Permissions
- `POST /api/v1/permissions` - Create permission
- `GET /api/v1/permissions` - List all permissions
- `GET /api/v1/permissions/{id}` - Get permission by ID
- `PATCH /api/v1/permissions/{id}` - Update permission
- `DELETE /api/v1/permissions/{id}` - Delete permission

### Example Requests

#### Create an Account
```bash
curl -X POST "http://localhost:8001/api/v1/accounts" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepass123",
    "role_id": "your-role-uuid-here"
  }'
```

#### List All Roles
```bash
curl -X GET "http://localhost:8001/api/v1/roles"
```

#### Assign Permissions to Role
```bash
curl -X POST "http://localhost:8001/api/v1/roles/{role_id}/permissions" \
  -H "Content-Type: application/json" \
  -d '{
    "permission_ids": [
      "permission-uuid-1",
      "permission-uuid-2"
    ]
  }'
```

## 🗄️ Database Schema

### Accounts Table
```sql
id: UUID (PK)
email: VARCHAR(255) UNIQUE NOT NULL
password_hash: VARCHAR(255) NOT NULL
role_id: UUID (FK → roles.id)
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

### Roles Table
```sql
id: UUID (PK)
name: VARCHAR(100) UNIQUE NOT NULL
description: VARCHAR(255)
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

### Permissions Table
```sql
id: UUID (PK)
name: VARCHAR(100) UNIQUE NOT NULL
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

### Role_Permissions Table (Join)
```sql
role_id: UUID (PK, FK → roles.id)
permission_id: UUID (PK, FK → permissions.id)
```

## 🔐 Security

### Password Storage
- Passwords are hashed using **bcrypt** before storage
- Plain-text passwords are never stored in the database
- Password verification is done via bcrypt comparison

### Default Permissions

The seed script creates these permissions:
- `accounts.create`, `accounts.read`, `accounts.update`, `accounts.delete`
- `roles.create`, `roles.read`, `roles.update`, `roles.delete`
- `permissions.create`, `permissions.read`, `permissions.update`, `permissions.delete`

## 📁 Project Structure

```
svc-users-python/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── account.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   └── role_permission.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── response.py
│   │   ├── account.py
│   │   ├── role.py
│   │   └── permission.py
│   ├── routers/                # API route handlers
│   │   └── v1/
│   │       ├── health.py
│   │       ├── accounts.py
│   │       ├── roles.py
│   │       ├── permissions.py
│   │       └── router.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── account_service.py
│   │   ├── role_service.py
│   │   └── permission_service.py
│   └── utils/                  # Utility functions
│       └── response.py
├── .env                        # Environment variables
├── .env.example                # Environment template
├── docker-compose.yml          # PostgreSQL container
├── requirements.txt            # Python dependencies
├── seed.py                     # Database seeding script
├── Dockerfile                  # Docker image configuration
└── README.md                   # This file
```

## 🛠️ Development

### Running Tests
```bash
# TODO: Add pytest tests in future iterations
```

### Database Management

**Reset database:**
```bash
# Stop and remove containers
docker-compose down -v

# Start fresh
docker-compose up -d
python seed.py
```

**Access PostgreSQL:**
```bash
docker exec -it svc-users-db psql -U postgres -d svc_users
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Document functions with docstrings
- Keep functions focused and simple

## 🐳 Docker

### Build Image
```bash
docker build -t svc-users-python:latest .
```

### Run Container
```bash
docker run -p 8001:8001 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  svc-users-python:latest
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/svc_users` |
| `PORT` | Server port | `8001` |
| `HOST` | Server host | `0.0.0.0` |
| `ENVIRONMENT` | Environment (development/production) | `development` |
| `SECRET_KEY` | Secret key for security | `change-me-in-production` |

## 🔄 Future Enhancements

- [ ] JWT token generation & validation
- [ ] Login/logout endpoints
- [ ] Refresh token mechanism
- [ ] Email verification
- [ ] Password reset flow
- [ ] API authentication middleware
- [ ] Rate limiting
- [ ] Unit & integration tests
- [ ] CI/CD pipeline

## 📖 API Response Examples

### Success Response
```json
{
  "status": "success",
  "code": 200,
  "message": "Account created successfully",
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "user@example.com",
    "role_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "created_at": "2025-10-14T10:30:00Z",
    "updated_at": "2025-10-14T10:30:00Z"
  },
  "errors": null,
  "meta": null
}
```

### Error Response
```json
{
  "status": "error",
  "code": 404,
  "message": "Account not found",
  "data": null,
  "errors": null,
  "meta": null
}
```

### Validation Error Response
```json
{
  "status": "error",
  "code": 422,
  "message": "Validation error",
  "data": null,
  "errors": [
    {"field": "email", "error": "Invalid email format"},
    {"field": "password", "error": "Password must be at least 8 characters"}
  ],
  "meta": null
}
```

## 📞 Support

For questions or issues, please contact the development team.

## 📄 License

[Add your license here]
