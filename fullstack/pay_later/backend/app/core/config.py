"""
Configuration settings for the Pay-Later application.
"""
from typing import List, Optional
from pydantic import BaseSettings, validator
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application Settings
    app_name: str = "Pay-Later API"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Database Settings
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "pay_later_db"
    mongodb_max_pool_size: int = 10
    mongodb_min_pool_size: int = 1
    
    # JWT Settings
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Security Settings
    secret_key: str = "your-super-secret-key-change-in-production"
    bcrypt_rounds: int = 12
    
    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Email Settings (for future use)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Frontend URL
    frontend_url: str = "http://localhost:3000"
    
    @validator("jwt_secret_key", "secret_key", pre=True)
    def validate_secret_keys(cls, v):
        """Validate that secret keys are not default values in production."""
        if cls.environment == "production" and v in [
            "your-super-secret-jwt-key-change-in-production",
            "your-super-secret-key-change-in-production"
        ]:
            raise ValueError("Secret keys must be changed in production")
        return v
    
    @validator("mongodb_url", pre=True)
    def validate_mongodb_url(cls, v):
        """Validate MongoDB URL format."""
        if not v.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("Invalid MongoDB URL format")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()


# Database configuration
DATABASE_CONFIG = {
    "url": settings.mongodb_url,
    "database": settings.mongodb_db_name,
    "max_pool_size": settings.mongodb_max_pool_size,
    "min_pool_size": settings.mongodb_min_pool_size,
}

# JWT configuration
JWT_CONFIG = {
    "secret_key": settings.jwt_secret_key,
    "algorithm": settings.jwt_algorithm,
    "access_token_expire_minutes": settings.jwt_access_token_expire_minutes,
    "refresh_token_expire_days": settings.jwt_refresh_token_expire_days,
}

# CORS configuration
CORS_CONFIG = {
    "origins": settings.cors_origins,
    "allow_credentials": settings.cors_allow_credentials,
    "allow_methods": settings.cors_allow_methods,
    "allow_headers": settings.cors_allow_headers,
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "per_minute": settings.rate_limit_per_minute,
    "per_hour": settings.rate_limit_per_hour,
}
