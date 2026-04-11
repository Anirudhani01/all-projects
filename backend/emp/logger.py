import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    """Custom logger for the Employee Management System"""
    
    def __init__(self, name: str = "employee_management"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler for all logs
        file_handler = logging.FileHandler(f"logs/employee_management.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Console handler for important logs
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add handlers if they don't exist
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_operation(self, operation: str, details: str, user: Optional[str] = None):
        """Log an operation with details"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_info = f" by {user}" if user else ""
        message = f"[{operation}]{user_info}: {details}"
        self.logger.info(message)
    
    def log_error(self, error: str, details: str = ""):
        """Log an error"""
        message = f"ERROR: {error}"
        if details:
            message += f" - Details: {details}"
        self.logger.error(message)
    
    def log_database_operation(self, operation: str, table: str, record_id: Optional[int] = None):
        """Log database operations"""
        record_info = f" (ID: {record_id})" if record_id else ""
        self.log_operation(f"DB_{operation}", f"Table: {table}{record_info}")
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, user: Optional[str] = None):
        """Log API requests"""
        self.log_operation(
            "API_REQUEST", 
            f"{method} {endpoint} - Status: {status_code}",
            user
        )


# Create global logger instance
logger = Logger()
