import re
from typing import Optional
from app.common.exceptions import InvalidAmount, InvalidFeePercentage
from app.common.types import MIN_AMOUNT, MAX_AMOUNT, MIN_FEE_PERCENTAGE, MAX_FEE_PERCENTAGE


def validate_amount(amount: float, field_name: str = "amount") -> float:
    """Validate and return amount."""
    if not isinstance(amount, (int, float)) or amount < MIN_AMOUNT:
        raise InvalidAmount(amount, f"{field_name} must be a positive number >= {MIN_AMOUNT}")
    
    if amount > MAX_AMOUNT:
        raise InvalidAmount(amount, f"{field_name} cannot exceed {MAX_AMOUNT}")
    
    return float(amount)


def validate_fee_percentage(fee_pct: float) -> float:
    """Validate fee percentage."""
    if not isinstance(fee_pct, (int, float)):
        raise InvalidFeePercentage(fee_pct)
    
    if fee_pct < MIN_FEE_PERCENTAGE or fee_pct > MAX_FEE_PERCENTAGE:
        raise InvalidFeePercentage(fee_pct)
    
    return float(fee_pct)


def validate_credit_limit(credit_limit: float) -> float:
    """Validate credit limit."""
    if not isinstance(credit_limit, (int, float)) or credit_limit < 0:
        raise InvalidAmount(credit_limit, "Credit limit must be a non-negative number")
    
    return float(credit_limit)


def normalize_email(email: str) -> str:
    """Normalize email address."""
    if not email:
        raise ValueError("Email cannot be empty")
    
    email = email.strip().lower()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    return email


def normalize_string(value: str, field_name: str = "string") -> str:
    """Normalize string value."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")
    
    return normalized


def validate_currency(currency: str) -> str:
    """Validate currency code."""
    if not isinstance(currency, str):
        raise ValueError("Currency must be a string")
    
    currency = currency.strip().upper()
    valid_currencies = ["INR", "USD", "EUR"]
    
    if currency not in valid_currencies:
        raise ValueError(f"Currency must be one of: {', '.join(valid_currencies)}")
    
    return currency


def calculate_fee_amount(amount: float, fee_percentage: float) -> float:
    """Calculate fee amount from percentage."""
    return round(amount * (fee_percentage / 100), 2)


def calculate_merchant_payout(amount: float, fee_amount: float) -> float:
    """Calculate merchant payout amount."""
    return round(amount - fee_amount, 2)
