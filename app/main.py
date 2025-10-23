"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.config import get_settings
from app.database import init_db
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
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
    Custom OpenAPI schema generation that removes 422 validation error responses.
    This keeps the documentation clean while still handling validation errors at runtime.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Remove 422 responses from all endpoints
    for path_data in openapi_schema["paths"].values():
        for method_data in path_data.values():
            if isinstance(method_data, dict) and "responses" in method_data:
                if "422" in method_data["responses"]:
                    del method_data["responses"]["422"]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set custom OpenAPI schema generator
app.openapi = custom_openapi


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    init_db()


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
