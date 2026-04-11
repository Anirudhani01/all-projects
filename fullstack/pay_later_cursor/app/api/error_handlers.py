from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.common.exceptions import (
    DomainException,
    UserNotFound,
    MerchantNotFound,
    DuplicateEntity,
    CreditLimitExceeded,
    InvalidAmount,
    InvalidFeePercentage,
    DuplicateRequest,
    InsufficientBalance,
    ConflictUpdate,
    InvalidUserStatus
)
import structlog

logger = structlog.get_logger(__name__)


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Handle domain exceptions and map them to appropriate HTTP status codes."""
    
    # Log the error
    logger.error("Domain exception occurred",
                exception_type=type(exc).__name__,
                message=exc.message,
                details=exc.details,
                path=request.url.path,
                method=request.method)
    
    # Map domain exceptions to HTTP status codes
    if isinstance(exc, (UserNotFound, MerchantNotFound)):
        status_code = 404
    elif isinstance(exc, (DuplicateEntity, DuplicateRequest, ConflictUpdate)):
        status_code = 409
    elif isinstance(exc, CreditLimitExceeded):
        status_code = 402  # Payment Required
    elif isinstance(exc, (InvalidAmount, InvalidFeePercentage, InsufficientBalance, InvalidUserStatus)):
        status_code = 400
    else:
        status_code = 500
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": type(exc).__name__,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle validation exceptions."""
    
    logger.error("Validation exception occurred",
                exception_type=type(exc).__name__,
                message=str(exc),
                path=request.url.path,
                method=request.method)
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": "ValidationError",
                "message": "Validation failed",
                "details": str(exc)
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    
    logger.error("Unexpected exception occurred",
                exception_type=type(exc).__name__,
                message=str(exc),
                path=request.url.path,
                method=request.method)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred"
            }
        }
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    
    # Register domain exception handler
    app.add_exception_handler(DomainException, domain_exception_handler)
    
    # Register specific domain exceptions
    app.add_exception_handler(UserNotFound, domain_exception_handler)
    app.add_exception_handler(MerchantNotFound, domain_exception_handler)
    app.add_exception_handler(DuplicateEntity, domain_exception_handler)
    app.add_exception_handler(CreditLimitExceeded, domain_exception_handler)
    app.add_exception_handler(InvalidAmount, domain_exception_handler)
    app.add_exception_handler(InvalidFeePercentage, domain_exception_handler)
    app.add_exception_handler(DuplicateRequest, domain_exception_handler)
    app.add_exception_handler(InsufficientBalance, domain_exception_handler)
    app.add_exception_handler(ConflictUpdate, domain_exception_handler)
    app.add_exception_handler(InvalidUserStatus, domain_exception_handler)
    
    # Register validation exception handler
    from pydantic import ValidationError
    app.add_exception_handler(ValidationError, validation_exception_handler)
    
    # Register general exception handler
    app.add_exception_handler(Exception, general_exception_handler)
