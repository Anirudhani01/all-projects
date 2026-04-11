from typing import Optional, Any


class DomainException(Exception):
    """Base domain exception."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class UserNotFound(DomainException):
    """Raised when a user is not found."""
    pass


class MerchantNotFound(DomainException):
    """Raised when a merchant is not found."""
    pass


class DuplicateEntity(DomainException):
    """Raised when trying to create a duplicate entity."""
    
    def __init__(self, entity_type: str, field: str, value: Any):
        message = f"{entity_type} with {field} '{value}' already exists"
        super().__init__(message, {"entity_type": entity_type, "field": field, "value": value})


class CreditLimitExceeded(DomainException):
    """Raised when a purchase would exceed user's credit limit."""
    
    def __init__(self, user_id: str, requested_amount: float, available_credit: float):
        message = f"Credit limit exceeded. Requested: {requested_amount}, Available: {available_credit}"
        super().__init__(message, {
            "user_id": user_id,
            "requested_amount": requested_amount,
            "available_credit": available_credit
        })


class InvalidAmount(DomainException):
    """Raised when an invalid amount is provided."""
    
    def __init__(self, amount: float, reason: str):
        message = f"Invalid amount {amount}: {reason}"
        super().__init__(message, {"amount": amount, "reason": reason})


class InvalidFeePercentage(DomainException):
    """Raised when an invalid fee percentage is provided."""
    
    def __init__(self, fee_pct: float):
        message = f"Invalid fee percentage {fee_pct}. Must be between 0 and 100."
        super().__init__(message, {"fee_pct": fee_pct})


class DuplicateRequest(DomainException):
    """Raised when a duplicate request is detected (idempotency)."""
    
    def __init__(self, idempotency_key: str):
        message = f"Duplicate request detected with idempotency key: {idempotency_key}"
        super().__init__(message, {"idempotency_key": idempotency_key})


class InsufficientBalance(DomainException):
    """Raised when payment amount exceeds outstanding balance."""
    
    def __init__(self, user_id: str, payment_amount: float, outstanding_amount: float):
        message = f"Payment amount {payment_amount} exceeds outstanding balance {outstanding_amount}"
        super().__init__(message, {
            "user_id": user_id,
            "payment_amount": payment_amount,
            "outstanding_amount": outstanding_amount
        })


class ConflictUpdate(DomainException):
    """Raised when optimistic locking fails."""
    
    def __init__(self, entity_type: str, entity_id: str):
        message = f"Concurrent update detected for {entity_type} {entity_id}"
        super().__init__(message, {"entity_type": entity_type, "entity_id": entity_id})


class InvalidUserStatus(DomainException):
    """Raised when user status is invalid for the operation."""
    
    def __init__(self, user_id: str, current_status: str, required_status: str):
        message = f"User {user_id} has status {current_status}, but {required_status} is required"
        super().__init__(message, {
            "user_id": user_id,
            "current_status": current_status,
            "required_status": required_status
        })


class NotFoundError(DomainException):
    """Raised when a resource is not found."""
    pass


class ValidationError(DomainException):
    """Raised when validation fails."""
    pass
