import os
import logging
from datetime import datetime
from pathlib import Path
import sys

def setup_centralized_logging():
    """
    Set up centralized logging configuration with date-wise log files.
    
    Creates log files in format: app_YYYY-MM-DD_HH-MM-SS.log
    Each application restart creates a new log file.
    
    Returns:
        logging.Logger: Configured root logger
    """
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Generate timestamp for unique log file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_dir / f"app_{timestamp}.log"
    
    # Get root logger and clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler - INFO level only with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Set UTF-8 encoding for console handler
    if hasattr(console_handler.stream, 'reconfigure'):
        console_handler.stream.reconfigure(encoding='utf-8')
    
    # File handler - DEBUG level (all logs) with detailed format
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers at console level
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('openai._base_client').setLevel(logging.WARNING)
    
    # Log the initialization
    logger = logging.getLogger(__name__)
    logger.info(f"Centralized logging initialized. Log file: {log_file}")
    
    return root_logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance that uses the centralized configuration.
    
    Args:
        name (str): Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name or __name__)

def cleanup_old_logs(days_to_keep: int = 7):
    """
    Clean up old log files older than specified days.
    
    Args:
        days_to_keep (int): Number of days to keep log files
    """
    log_dir = Path('logs')
    if not log_dir.exists():
        return
    
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    for log_file in log_dir.glob('app_*.log'):
        try:
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time < cutoff_date:
                log_file.unlink()
                print(f"Deleted old log file: {log_file}")
        except Exception as e:
            print(f"Error deleting log file {log_file}: {e}")