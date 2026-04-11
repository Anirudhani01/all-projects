# import logging
# from logging.handlers import RotatingFileHandler

# LOG_FILE = "paylater_app.log"

# # Create logger
# logger = logging.getLogger("paylater_app")
# logger.setLevel(logging.INFO)

# # Rotating file handler: 1 MB per file, keep 5 backups
# handler = RotatingFileHandler(LOG_FILE, maxBytes=1024, backupCount=5)  # 1 KB for testing
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# # Console handler (optional)
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(formatter)
# logger.addHandler(console_handler)
