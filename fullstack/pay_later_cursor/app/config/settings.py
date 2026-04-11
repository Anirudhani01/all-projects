try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "lazypay"
    
    # Application Configuration
    app_env: str = "local"
    port: int = 8000
    debug: bool = False
    
    # Logging Configuration
    log_level: str = "INFO"
    
    # Idempotency Configuration
    idempotency_ttl_hours: int = 24
    
    # JWT Configuration
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 3
    refresh_token_expire_minutes: int = 5
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()
