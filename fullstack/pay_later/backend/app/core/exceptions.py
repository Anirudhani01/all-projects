"""
Custom exceptions for the Pay-Later application.
"""
from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class PayLaterException(Exception):
    """Base exception for Pay-Later application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationException(PayLaterException):
    """Authentication related exceptions."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(PayLaterException):
    """Authorization related exceptions."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ValidationException(PayLaterException):
    """Data validation exceptions."""
    
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class NotFoundException(PayLaterException):
    """Resource not found exceptions."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictException(PayLaterException):
    """Resource conflict exceptions."""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class DatabaseException(PayLaterException):
    """Database related exceptions."""
    
    def __init__(self, message: str = "Database error"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreditLimitException(PayLaterException):
    """Credit limit related exceptions."""
    
    def __init__(self, message: str = "Credit limit error"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class TransactionException(PayLaterException):
    """Transaction related exceptions."""
    
    def __init__(self, message: str = "Transaction error"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class RateLimitException(PayLaterException):
    """Rate limiting exceptions."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


# Exception handlers
def handle_pay_later_exception(exc: PayLaterException) -> HTTPException:
    """Convert PayLaterException to HTTPException."""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details
        }
    )


def handle_validation_exception(exc: ValidationException) -> HTTPException:
    """Handle validation exceptions with detailed error information."""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details,
            "type": "validation_error"
        }
    )


def handle_authentication_exception(exc: AuthenticationException) -> HTTPException:
    """Handle authentication exceptions."""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "type": "authentication_error"
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


def handle_authorization_exception(exc: AuthorizationException) -> HTTPException:
    """Handle authorization exceptions."""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "type": "authorization_error"
        }
    )
