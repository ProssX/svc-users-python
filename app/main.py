"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.config import get_settings, PUBLIC_ROUTES
from app.routers.v1.router import api_v1_router
from app.exceptions import register_exception_handlers


# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Authentication Microservice",
    description="User authentication service with Account, Role, and Permission management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Parse CORS origins (supports comma-separated list or "*")
allowed_origins = ["*"] if settings.cors_origins == "*" else [
    origin.strip() for origin in settings.cors_origins.split(",")
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_v1_router, prefix="/api/v1")

# Register exception handlers
register_exception_handlers(app)


def custom_openapi():
    """
    Custom OpenAPI schema generation with global Bearer token authentication.
    Removes 422 validation error responses and configures security requirements.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }
    
    # Configure security requirements for all endpoints except public routes
    for path, path_data in openapi_schema["paths"].items():
        for method, method_data in path_data.items():
            if isinstance(method_data, dict):
                # Remove 422 responses from all endpoints
                if "responses" in method_data and "422" in method_data["responses"]:
                    del method_data["responses"]["422"]
                
                # Add security requirement if not a public route
                if path not in PUBLIC_ROUTES:
                    method_data["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set custom OpenAPI schema generator
app.openapi = custom_openapi


@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    # Database schema is managed by Alembic migrations
    # Run migrations before starting: alembic upgrade head
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    pass


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Authentication Microservice",
        "version": "1.0.0",
        "docs": "/docs"
    }
