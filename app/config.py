"""
Configuration management for the authentication microservice.
Loads environment variables and provides application settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str
    
    # Server
    port: int = 8001
    host: str = "0.0.0.0"
    environment: str = "development"
    
    # Security
    # IMPORTANT: Must be set in environment variables for production
    secret_key: str
    
    # JWT Configuration
    jwt_algorithm: str = "RS256"
    jwt_issuer: str = "https://api.example.com"
    jwt_audience: str = "https://api.example.com"
    jwt_expiration_days: int = 7
    jwt_kid: str = "auth-2025-10-15"
    
    # RSA Keys (base64-encoded PEM format stored in environment variables)
    jwt_private_key: str
    jwt_public_key: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Public routes that don't require authentication
PUBLIC_ROUTES = [
    "/",
    "/health",
    "/api/v1/health", 
    "/api/v1/auth/login",
    "/api/v1/auth/register", 
    "/api/v1/auth/jwks",
    "/docs",
    "/redoc",
    "/openapi.json"
]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are loaded only once.
    """
    return Settings()
