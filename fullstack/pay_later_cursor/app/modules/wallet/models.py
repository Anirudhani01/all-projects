from datetime import datetime, timezone
from typing import Optional, Dict
from bson import ObjectId


class MerchantWallet:
    """Merchant wallet document model."""
    
    def __init__(
        self,
        merchant_id: ObjectId,
        balance: float = 0.0,
        total_received: float = 0.0,
        total_fees_earned: float = 0.0,
        last_transaction_at: Optional[datetime] = None,
        wallet_id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = wallet_id or ObjectId()
        self.merchant_id = merchant_id
        self.balance = balance
        self.total_received = total_received
        self.total_fees_earned = total_fees_earned
        self.last_transaction_at = last_transaction_at
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "merchant_id": self.merchant_id,
            "balance": self.balance,
            "total_received": self.total_received,
            "total_fees_earned": self.total_fees_earned,
            "last_transaction_at": self.last_transaction_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MerchantWallet":
        """Create MerchantWallet instance from dictionary."""
        return cls(
            wallet_id=data["_id"],
            merchant_id=data["merchant_id"],
            balance=data["balance"],
            total_received=data["total_received"],
            total_fees_earned=data["total_fees_earned"],
            last_transaction_at=data.get("last_transaction_at"),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
    
    def add_amount(self, amount: float, fee_amount: float = 0.0):
        """Add amount to wallet balance."""
        self.balance += amount
        self.total_received += amount
        self.total_fees_earned += fee_amount
        self.last_transaction_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def get_balance(self) -> float:
        """Get current wallet balance."""
        return self.balance


class CreditLimit:
    """Credit limit document model."""
    
    def __init__(
        self,
        user_id: ObjectId,
        credit_limit: float = 0.0,
        available_credit: float = 0.0,
        used_credit: float = 0.0,
        merchant_usage: Optional[Dict[str, float]] = None,
        credit_id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = credit_id or ObjectId()
        self.user_id = user_id
        self.credit_limit = credit_limit
        self.available_credit = available_credit
        self.used_credit = used_credit
        self.merchant_usage = merchant_usage or {}
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "credit_limit": self.credit_limit,
            "available_credit": self.available_credit,
            "used_credit": self.used_credit,
            "merchant_usage": self.merchant_usage,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CreditLimit":
        """Create CreditLimit instance from dictionary."""
        return cls(
            credit_id=data["_id"],
            user_id=data["user_id"],
            credit_limit=data["credit_limit"],
            available_credit=data["available_credit"],
            used_credit=data["used_credit"],
            merchant_usage=data.get("merchant_usage", {}),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
    
    def set_credit_limit(self, credit_limit: float):
        """Set credit limit and recalculate available credit."""
        self.credit_limit = credit_limit
        self.available_credit = self.credit_limit - self.used_credit
        self.updated_at = datetime.now(timezone.utc)
    
    def add_merchant_usage(self, merchant_id: str, amount: float):
        """Add usage for a specific merchant."""
        current_usage = self.merchant_usage.get(merchant_id, 0.0)
        self.merchant_usage[merchant_id] = current_usage + amount
        self.used_credit += amount
        self.available_credit = self.credit_limit - self.used_credit
        self.updated_at = datetime.now(timezone.utc)
    
    def add_payment(self, amount: float):
        """Add payment to reduce used credit."""
        self.used_credit -= amount
        self.available_credit = self.credit_limit - self.used_credit
        self.updated_at = datetime.now(timezone.utc)
    
    def get_merchant_usage(self, merchant_id: str) -> float:
        """Get usage for a specific merchant."""
        return self.merchant_usage.get(merchant_id, 0.0)
    
    def has_sufficient_credit(self, amount: float) -> bool:
        """Check if user has sufficient credit for the amount."""
        return self.available_credit >= amount
