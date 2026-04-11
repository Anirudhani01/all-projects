import os
import logging
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    blue = "\x1b[34;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: blue + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class AppLogger:
    def __init__(self, logger_name=__name__):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.addFilter(lambda record: "[TASK STATUS]" in record.getMessage())
            formatter = ColoredFormatter()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            log_path = os.path.join(os.getcwd(), 'logs')
            if not os.path.exists(log_path):
                os.makedirs(log_path)
            log_filename = f"app_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
            log_file_path = os.path.join(log_path, log_filename)
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def log_status(self, message):
        self.logger.info(f"[TASK STATUS] {message}")
    def get_logger(self):
        return self.logger
    
