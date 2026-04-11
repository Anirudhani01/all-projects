"""
File handling utilities
"""
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FileUtils:
    """Utility class for file operations"""
    
    @staticmethod
    def get_file_info(file_path: Path) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            stat = file_path.stat()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            return {
                "name": file_path.name,
                "size": stat.st_size,
                "extension": file_path.suffix.lower(),
                "mime_type": mime_type,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "is_file": file_path.is_file(),
                "is_readable": file_path.is_file() and file_path.stat().st_mode & 0o444
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return {}
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe folder creation"""
        # Remove or replace invalid characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        sanitized = "".join(c if c in safe_chars else "_" for c in filename)
        
        # Remove multiple underscores and trim
        sanitized = "_".join(part for part in sanitized.split("_") if part)
        
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        
        return sanitized or "unknown_file"
    
    @staticmethod
    def ensure_directory(path: Path) -> bool:
        """Ensure directory exists, create if not"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")
            return False
    
    @staticmethod
    def get_unique_filename(base_path: Path, filename: str) -> Path:
        """Get unique filename if file already exists"""
        counter = 1
        original_path = base_path / filename
        
        while original_path.exists():
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                new_filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
            else:
                new_filename = f"{filename}_{counter}"
            original_path = base_path / new_filename
            counter += 1
        
        return original_path
