"""
Configuration settings for the Hospital Management System
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    DATABASE_URL: str = "mysql+pymysql://anirudh:password123@localhost:3306/hospital_management"
    
    # Application Configuration
    APP_NAME: str = "Hospital Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".gif"]
    UPLOAD_DIR: str = "static/uploads"
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
