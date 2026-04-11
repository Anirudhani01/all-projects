try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database Configuration
    mongodb_url: str = "mongodb://localhost:27017/ecommerce_dev"
    database_name: str = "ecommerce_dev"
    
    # Server Configuration
    port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = True
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
