# Authentication Microservice (svc-users-python)

A FastAPI-based authentication microservice for user management with JWT authentication and role-based permissions.

## 📋 Overview

This microservice provides:

- **JWT Authentication** - Login with RS256-signed tokens
- **Account Management** - User accounts with email/password
- **Role-Based Access** - Hierarchical role system
- **Permission System** - Granular permissions attached to roles

### Architecture

```
Account (1) ──→ (1) Role (1) ──→ (M) Permission
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (if running locally)

### Option 1: Run with Docker Compose (Recommended)

```bash
# 1. Generate JWT keys (first time only)
python -m app.scripts.generate_keys

# 2. Copy .env.example to .env and add your generated keys
cp .env.example .env
# Edit .env and paste JWT_PRIVATE_KEY, JWT_PUBLIC_KEY, and SECRET_KEY

# 3. Start everything (database + app)
docker-compose up -d

# 4. Run database migrations
docker exec -it svc-users-app alembic upgrade head

# 5. Seed test accounts (optional)
docker exec -it svc-users-app python -m app.scripts.seed
```

The service will be available at:

- **API**: http://localhost:8001
- **Docs**: http://localhost:8001/docs

### Option 2: Run Locally (Development)

```bash
# 1. Generate JWT keys (first time only)
python -m app.scripts.generate_keys

# 2. Setup environment
cp .env.example .env
# Edit .env and paste your generated keys and SECRET_KEY

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start PostgreSQL only
docker-compose up -d postgres

# 5. Run database migrations
alembic upgrade head

# 6. Seed test accounts (optional)
python -m app.scripts.seed

# 7. Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Default Test Accounts

After running `python -m app.scripts.seed`, you can use:

- **Admin**: `admin@example.com` / `admin123`
- **User**: `user@example.com` / `user123`

## 🗄️ Database Migrations

This project uses **Alembic** for database schema management.

### Run Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current migration version
alembic current

# View migration history
alembic history
```

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration (for data-only changes)
alembic revision -m "description of changes"
```

### Deployment (Coolify, etc.)

When deploying to production platforms like Coolify:

1. **Build Command**: Use default Dockerfile
2. **Post-Deployment Command**: `alembic upgrade head`
3. **Environment Variables**: Configure all required variables (see `.env.example`)

⚠️ **Important**: Always run migrations before starting the application!

### Migration Structure

- `alembic/versions/001_initial_*.py` - Creates database schema (tables, indexes)
- `alembic/versions/002_permissions_*.py` - Seeds default permissions
- `alembic/versions/003_roles_*.py` - Seeds default roles and assigns permissions

**Seed Scripts** (for test data only):

- `python -m app.scripts.seed` - Creates test accounts (admin, user)
- `python -m app.scripts.generate_keys` - Generates RSA key pairs for JWT

## 🔐 JWT Configuration

This service uses **RS256 asymmetric encryption** for JWT tokens. You must generate RSA key pairs before running the application.

### Generate Keys

```bash
python -m app.scripts.generate_keys
```

This script generates:

- **JWT_PRIVATE_KEY** - Used to sign tokens (keep secret!)
- **JWT_PUBLIC_KEY** - Used to verify tokens (can be shared)

Copy the output and paste into your `.env` file. The keys are base64-encoded PEM format.

⚠️ **Security**: Never commit `JWT_PRIVATE_KEY` to version control!

## 📝 Environment Variables

Create a `.env` file with these variables:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/svc_users

# Server
PORT=8001
HOST=0.0.0.0
ENVIRONMENT=development

# Security (REQUIRED - generate with: openssl rand -base64 32)
SECRET_KEY=<your-secret-key-here>

# JWT Configuration
JWT_ALGORITHM=RS256
JWT_ISSUER=https://api.example.com
JWT_AUDIENCE=https://api.example.com
JWT_EXPIRATION_DAYS=7
JWT_KID=auth-2025-10-15

# RSA Keys (generate with: python -m app.scripts.generate_keys)
JWT_PRIVATE_KEY=<your-base64-encoded-private-key>
JWT_PUBLIC_KEY=<your-base64-encoded-public-key>
```

**Key Variables:**

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - **REQUIRED** - Secret for application security (generate with: `openssl rand -base64 32`)
- `JWT_PRIVATE_KEY` - Base64-encoded RSA private key for signing tokens
- `JWT_PUBLIC_KEY` - Base64-encoded RSA public key for verification
- `JWT_EXPIRATION_DAYS` - Token lifetime (default: 7 days)
- `PORT` - Server port (default: 8001)
- `HOST` - Server host (default: 0.0.0.0)

See `.env.example` for complete configuration.

## 📚 API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Login and receive JWT token
- `GET /api/v1/auth/jwks` - Get public keys for JWT verification

### Accounts

- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts` - List accounts
- `GET /api/v1/accounts/{id}` - Get account
- `PATCH /api/v1/accounts/{id}` - Update account
- `DELETE /api/v1/accounts/{id}` - Delete account

### Roles

- `POST /api/v1/roles` - Create role
- `GET /api/v1/roles` - List roles
- `GET /api/v1/roles/{id}` - Get role
- `PATCH /api/v1/roles/{id}` - Update role
- `DELETE /api/v1/roles/{id}` - Delete role
- `POST /api/v1/roles/{id}/permissions` - Assign permissions
- `DELETE /api/v1/roles/{id}/permissions/{permission_id}` - Remove permission

### Permissions

- `POST /api/v1/permissions` - Create permission
- `GET /api/v1/permissions` - List permissions
- `GET /api/v1/permissions/{id}` - Get permission
- `PATCH /api/v1/permissions/{id}` - Update permission
- `DELETE /api/v1/permissions/{id}` - Delete permission

### Health

- `GET /api/v1/health` - Service health status

**Full API documentation**: http://localhost:8001/docs

## 🧪 Example Usage

### Login

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

**Response:**

```json
{
  "status": "success",
  "code": 200,
  "message": "Token issued.",
  "data": {
    "tokenType": "Bearer",
    "token": "eyJhbGciOiJSUzI1NiIs...",
    "expiresAt": "2025-10-22T12:00:00Z"
  }
}
```

### Create Account

```bash
curl -X POST http://localhost:8001/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepass123",
    "role_id": "your-role-uuid-here"
  }'
```

## 🛠️ Development

### Database Management

**Run migrations:**

```bash
# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current version
alembic current
```

**Seed test data:**

```bash
# Create test accounts (admin, user)
python -m app.scripts.seed

# Or in Docker:
docker exec -it svc-users-app python -m app.scripts.seed
```

**Reset database (careful!):**

```bash
docker-compose down -v
docker-compose up -d
alembic upgrade head
python -m app.scripts.seed
```

**Access PostgreSQL:**

```bash
docker exec -it svc-users-db psql -U postgres -d svc_users
```

### View Logs

```bash
# All services
docker-compose logs -f

# App only
docker-compose logs -f app

# Database only
docker-compose logs -f postgres
```

## � Project Structure

```
svc-users-python/
├── alembic/                 # Database migrations
│   ├── env.py              # Alembic environment config
│   └── versions/           # Migration files
│       ├── 001_initial_*.py       # Create tables
│       ├── 002_permissions_*.py   # Seed permissions
│       └── 003_roles_*.py         # Seed roles
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API route handlers
│   │   └── v1/
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── accounts.py
│   │       ├── roles.py
│   │       └── permissions.py
│   ├── services/            # Business logic
│   ├── utils/               # Utility functions
│   └── scripts/             # Utility scripts
│       ├── generate_keys.py # RSA key generation
│       └── seed.py          # Test data seeding
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # Docker services definition
├── Dockerfile               # App container image
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (create from .env.example)
```

## 🔒 Security

- **Passwords**: Hashed with bcrypt before storage
- **JWT Tokens**: Signed with RS256 (asymmetric encryption)
- **Key Management**: Private keys via environment variables
- **Token Expiration**: Configurable TTL (default: 7 days)

## 📖 Standard Response Format

All endpoints return:

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
