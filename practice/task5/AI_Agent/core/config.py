"""
Configuration file for the AI-Powered Unit Test Case Generation System.
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for the system."""
    
    # System configuration
    SYSTEM_NAME = "AI-Powered Unit Test Case Generation System"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # API configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    
    # Test generation configuration
    DEFAULT_TEST_FRAMEWORK = os.getenv("DEFAULT_TEST_FRAMEWORK", "pytest")
    DEFAULT_INCLUDE_MOCKS = os.getenv("DEFAULT_INCLUDE_MOCKS", "true").lower() == "true"
    DEFAULT_INCLUDE_COVERAGE = os.getenv("DEFAULT_INCLUDE_COVERAGE", "true").lower() == "true"
    
    # Code analysis configuration
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "1048576"))  # 1MB
    SUPPORTED_EXTENSIONS = [".py", ".js", ".java", ".cs"]  # Future support
    IGNORE_PATTERNS = [
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "build",
        "dist"
    ]
    
    # Template configuration
    TEMPLATE_CACHE_SIZE = int(os.getenv("TEMPLATE_CACHE_SIZE", "100"))
    TEMPLATE_SELECTION_THRESHOLD = float(os.getenv("TEMPLATE_SELECTION_THRESHOLD", "0.7"))
    
    # Output configuration
    DEFAULT_OUTPUT_FORMAT = os.getenv("DEFAULT_OUTPUT_FORMAT", "python")
    SUPPORTED_OUTPUT_FORMATS = ["python", "json", "markdown"]
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance configuration
    MAX_GENERATION_TIME = int(os.getenv("MAX_GENERATION_TIME", "300"))  # 5 minutes
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all configuration values as a dictionary."""
        return {
            "system_name": cls.SYSTEM_NAME,
            "version": cls.VERSION,
            "debug": cls.DEBUG,
            "openai_api_key_configured": bool(cls.OPENAI_API_KEY),
            "openai_model": cls.OPENAI_MODEL,
            "openai_temperature": cls.OPENAI_TEMPERATURE,
            "default_test_framework": cls.DEFAULT_TEST_FRAMEWORK,
            "default_include_mocks": cls.DEFAULT_INCLUDE_MOCKS,
            "default_include_coverage": cls.DEFAULT_INCLUDE_COVERAGE,
            "max_file_size": cls.MAX_FILE_SIZE,
            "supported_extensions": cls.SUPPORTED_EXTENSIONS,
            "ignore_patterns": cls.IGNORE_PATTERNS,
            "template_cache_size": cls.TEMPLATE_CACHE_SIZE,
            "template_selection_threshold": cls.TEMPLATE_SELECTION_THRESHOLD,
            "default_output_format": cls.DEFAULT_OUTPUT_FORMAT,
            "supported_output_formats": cls.SUPPORTED_OUTPUT_FORMATS,
            "log_level": cls.LOG_LEVEL,
            "max_generation_time": cls.MAX_GENERATION_TIME,
            "batch_size": cls.BATCH_SIZE
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate the current configuration and return validation results."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check required configurations
        if not cls.OPENAI_API_KEY:
            validation_results["warnings"].append("No OpenAI API key configured. AI features will be limited.")
        
        # Check file size limits
        if cls.MAX_FILE_SIZE > 10 * 1024 * 1024:  # 10MB
            validation_results["warnings"].append("Maximum file size is quite large. Consider reducing for better performance.")
        
        # Check template selection threshold
        if cls.TEMPLATE_SELECTION_THRESHOLD < 0.5:
            validation_results["warnings"].append("Template selection threshold is low. This may result in suboptimal template selection.")
        
        # Check batch size
        if cls.BATCH_SIZE > 50:
            validation_results["warnings"].append("Batch size is large. This may impact memory usage.")
        
        return validation_results


# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    MAX_GENERATION_TIME = 600  # 10 minutes for development


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    MAX_GENERATION_TIME = 120  # 2 minutes for production


class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    MAX_GENERATION_TIME = 60  # 1 minute for testing


# Configuration factory
def get_config(environment: str = None) -> Config:
    """Get configuration based on environment."""
    if not environment:
        environment = os.getenv("ENVIRONMENT", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    return config_map.get(environment.lower(), DevelopmentConfig)


# Default configuration instance
config = get_config()
