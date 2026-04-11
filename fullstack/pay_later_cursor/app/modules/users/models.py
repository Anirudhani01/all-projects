from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class User(BaseModel):
    """User model for the application."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: int = Field(..., description="Custom auto-increment user ID")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number")
    is_active: bool = Field(True, description="Whether the user is active")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create model from dictionary."""
        # Create a copy to avoid modifying the original data
        user_data = data.copy()
        if "_id" in user_data:
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]  # Remove _id to avoid Pydantic validation error
        return cls(**user_data)


class UserBank(BaseModel):
    """User Bank Account model for storing user's bank balance."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: int = Field(..., description="Custom auto-increment user ID")
    balance: float = Field(2000.0, description="Current bank balance (default 2000)")
    total_deposited: float = Field(0.0, description="Total amount deposited")
    total_withdrawn: float = Field(0.0, description="Total amount withdrawn")
    last_transaction_at: Optional[datetime] = Field(None, description="Last transaction timestamp")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserBank":
        """Create model from dictionary."""
        # Create a copy to avoid modifying the original data
        bank_data = data.copy()
        if "_id" in bank_data:
            bank_data["id"] = str(bank_data["_id"])
            del bank_data["_id"]  # Remove _id to avoid Pydantic validation error
        return cls(**bank_data)

    def add_deposit(self, amount: float) -> None:
        """Add deposit to bank account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.total_deposited += amount
        self.last_transaction_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def withdraw(self, amount: float) -> bool:
        """Withdraw from bank account. Returns True if successful."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self.balance < amount:
            return False  # Insufficient funds
        self.balance -= amount
        self.total_withdrawn += amount
        self.last_transaction_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        return True

    def get_balance(self) -> float:
        """Get current bank balance."""
        return self.balance

    def has_sufficient_funds(self, amount: float) -> bool:
        """Check if user has sufficient funds for withdrawal."""
        return self.balance >= amount


class UserBalance(BaseModel):
    """User balance model for tracking credit and outstanding amounts."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: int = Field(..., description="Custom auto-increment user ID")
    credit_limit: float = Field(2000.0, description="Total credit limit (fixed at 2000)")
    outstanding_amount: float = Field(0.0, description="Amount owed to PayLater")
    available_credit: float = Field(2000.0, description="Available credit (credit_limit - outstanding_amount)")
    total_merchant_usage: float = Field(0.0, description="Total used across all merchants")
    total_purchases: float = Field(0.0, description="Total purchases made")
    total_payments: float = Field(0.0, description="Total payments made")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserBalance":
        """Create model from dictionary."""
        # Create a copy to avoid modifying the original data
        balance_data = data.copy()
        if "_id" in balance_data:
            balance_data["id"] = str(balance_data["_id"])
            del balance_data["_id"]  # Remove _id to avoid Pydantic validation error
        return cls(**balance_data)

    def update_balance(self, purchase_amount: float, fee_amount: float) -> None:
        """Update balance after a purchase."""
        self.outstanding_amount += purchase_amount + fee_amount
        self.total_merchant_usage += purchase_amount
        self.total_purchases += purchase_amount
        self.available_credit = self.credit_limit - self.outstanding_amount
        self.updated_at = datetime.now(timezone.utc)

    def add_payment(self, payment_amount: float) -> None:
        """Add payment to reduce outstanding amount."""
        if payment_amount <= 0:
            raise ValueError("Payment amount must be positive")
        if payment_amount > self.outstanding_amount:
            raise ValueError("Payment amount cannot exceed outstanding amount")
        
        self.outstanding_amount -= payment_amount
        self.total_payments += payment_amount
        self.available_credit = self.credit_limit - self.outstanding_amount
        self.updated_at = datetime.now(timezone.utc)

    def add_merchant_usage(self, amount: float) -> None:
        """Add merchant usage amount."""
        self.total_merchant_usage += amount
        self.updated_at = datetime.now(timezone.utc)

    def set_credit_limit(self, limit: float) -> None:
        """Set credit limit (should always be 2000)."""
        if limit != 2000.0:
            raise ValueError("Credit limit must always be 2000")
        self.credit_limit = limit
        self.available_credit = self.credit_limit - self.outstanding_amount
        self.updated_at = datetime.now(timezone.utc)
    
    @property
    def reached_limit(self) -> bool:
        """Check if user has reached their credit limit."""
        return self.available_credit <= 0

    @property
    def credit_utilization_percentage(self) -> float:
        """Calculate credit utilization percentage."""
        if self.credit_limit == 0:
            return 0.0
        return (self.outstanding_amount / self.credit_limit) * 100
