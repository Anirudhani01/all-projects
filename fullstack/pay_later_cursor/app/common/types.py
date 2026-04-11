from enum import Enum
try:
    from typing import Literal
except ImportError:
    # For Python 3.7 compatibility
    from typing_extensions import Literal
from datetime import datetime
from bson import ObjectId


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class UserRole(str, Enum):
    """User roles."""
    USER = "user"
    MERCHANT = "merchant"
    ADMIN = "admin"


class TransactionType(str, Enum):
    """Transaction types."""
    PURCHASE = "PURCHASE"
    PAYMENT = "PAYMENT"
    REFUND = "REFUND"
    # NEW: Wallet system transaction types
    WALLET_ADD = "wallet_add"
    WALLET_PAYMENT = "wallet_payment"


class TransactionStatus(str, Enum):
    """Transaction status."""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVERSED = "REVERSED"


class Currency(str, Enum):
    """Supported currencies."""
    INR = "INR"
    USD = "USD"
    EUR = "EUR"


# Type aliases
UserId = ObjectId
MerchantId = ObjectId
TransactionId = ObjectId
BalanceId = ObjectId

# Default currency
DEFAULT_CURRENCY = Currency.INR

# Validation constants
MIN_CREDIT_LIMIT = 0
MAX_CREDIT_LIMIT = 1_000_000  # 1M
MIN_FEE_PERCENTAGE = 0.0
MAX_FEE_PERCENTAGE = 100.0
MIN_AMOUNT = 0.01
MAX_AMOUNT = 1_000_000  # 1M
