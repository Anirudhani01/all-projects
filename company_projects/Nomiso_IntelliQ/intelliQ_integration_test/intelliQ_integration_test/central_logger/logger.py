
# core/logger.py
import logging
import os
import sys
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    # Fix Unicode issues on Windows
    if sys.platform == 'win32':
        # Try to set console encoding to UTF-8
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            # If that fails, we'll use ASCII-safe logging
            pass
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'agent.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def get_logger(name):
    """Get logger instance"""
    return logging.getLogger(name)



def safe_log(logger, level, message):
    """Log message with safe emoji handling"""
    try:
        logger.log(level, message)
    except UnicodeEncodeError:
        # Remove emojis and try again
        safe_message = message.encode('ascii', 'ignore').decode('ascii')
        logger.log(level, safe_message)