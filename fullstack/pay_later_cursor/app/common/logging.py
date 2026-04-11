import sys
import structlog
from typing import Any, Dict
from app.config.settings import settings


def setup_logging():
    """Setup structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    import logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_request(logger: structlog.BoundLogger, method: str, path: str, **kwargs):
    """Log incoming request."""
    logger.info(
        "Incoming request",
        method=method,
        path=path,
        **kwargs
    )


def log_response(logger: structlog.BoundLogger, status_code: int, **kwargs):
    """Log response."""
    logger.info(
        "Response sent",
        status_code=status_code,
        **kwargs
    )


def log_error(logger: structlog.BoundLogger, error: Exception, **kwargs):
    """Log error with context."""
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        **kwargs
    )


def log_transaction(
    logger: structlog.BoundLogger,
    transaction_type: str,
    user_id: str,
    amount: float,
    status: str,
    **kwargs
):
    """Log transaction events."""
    logger.info(
        "Transaction processed",
        transaction_type=transaction_type,
        user_id=user_id,
        amount=amount,
        status=status,
        **kwargs
    )


def log_fee_change(
    logger: structlog.BoundLogger,
    merchant_id: str,
    old_fee: float,
    new_fee: float,
    **kwargs
):
    """Log fee change events."""
    logger.info(
        "Fee changed",
        merchant_id=merchant_id,
        old_fee=old_fee,
        new_fee=new_fee,
        **kwargs
    )
