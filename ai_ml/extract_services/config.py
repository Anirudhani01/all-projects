"""
Configuration settings for the Document Processing System
"""
import os
from pathlib import Path
from typing import Optional

class Settings:
    """Application settings and configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    RESULTS_DIR = BASE_DIR / "results"
    UPLOAD_DIR = BASE_DIR / "uploads"
    
    # FastAPI settings
    APP_NAME = "Document Processing System"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # File processing settings
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    
    # OCR settings
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")
    PADDLE_OCR_LANG = "en"
    
    # Image processing settings
    PDF_DPI = 300
    IMAGE_QUALITY = 95
    
    # Results storage settings
    RESULT_FOLDER_PREFIX = "result"
    KEEP_INTERMEDIATE_FILES = True
    CLEANUP_AFTER_DAYS = 30
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / "logs" / "app.log"
    
    # Processing timeouts
    PROCESSING_TIMEOUT = 300  # 5 minutes
    
    def __init__(self):
        """Initialize settings and create necessary directories"""
        self.RESULTS_DIR.mkdir(exist_ok=True)
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        (self.BASE_DIR / "logs").mkdir(exist_ok=True)

# Global settings instance
settings = Settings()
