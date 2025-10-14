"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.routers.v1.router import api_v1_router

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
