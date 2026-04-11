import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    db_username: str = "anirudh"
    db_password: str = "password 123"
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "employee_db"
    
    # Application Configuration
    app_name: str = "Employee Management System"
    app_version: str = "1.0.0"
    debug: bool = True
    
    @property
    def database_url(self) -> str:
        """Generate database URL for SQLAlchemy"""
        return f"mysql+pymysql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"


# Create settings instance
settings = Settings()
