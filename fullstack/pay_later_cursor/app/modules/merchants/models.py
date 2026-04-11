from datetime import datetime
from typing import Optional
from bson import ObjectId


class Merchant:
    """Merchant document model."""
    
    def __init__(
        self,
        name: str,
        current_fee_pct: float,
        email: Optional[str] = None,
        wallet_balance: float = 0.0,
        total_received: float = 0.0,
        merchant_id: Optional[ObjectId] = None,
        custom_merchant_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = merchant_id or ObjectId()
        self.name = name
        self.email = email
        self.current_fee_pct = current_fee_pct
        self.wallet_balance = wallet_balance
        self.total_received = total_received
        self.custom_merchant_id = custom_merchant_id  # Auto-increment ID (1, 2, 3, ...)
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "name": self.name,
            "email": self.email,
            "current_fee_pct": self.current_fee_pct,
            "wallet_balance": self.wallet_balance,
            "total_received": self.total_received,
            "custom_merchant_id": self.custom_merchant_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Merchant":
        """Create Merchant instance from dictionary."""
        return cls(
            merchant_id=data["_id"],
            name=data["name"],
            email=data.get("email"),
            current_fee_pct=data["current_fee_pct"],
            wallet_balance=data.get("wallet_balance", 0.0),
            total_received=data.get("total_received", 0.0),
            custom_merchant_id=data.get("custom_merchant_id"),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
    
    def update_fee(self, new_fee_pct: float):
        """Update merchant fee percentage."""
        self.current_fee_pct = new_fee_pct
        self.updated_at = datetime.utcnow()
    
    def add_to_wallet(self, amount: float):
        """Add amount to merchant wallet."""
        self.wallet_balance += amount
        self.total_received += amount
        self.updated_at = datetime.utcnow()
    
    def get_wallet_balance(self) -> float:
        """Get current wallet balance."""
        return self.wallet_balance


class MerchantFeeHistory:
    """Merchant fee history document model."""
    
    def __init__(
        self,
        merchant_id: ObjectId,
        fee_pct: float,
        effective_from: datetime,
        changed_by: str = "system",
        history_id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = history_id or ObjectId()
        self.merchant_id = merchant_id
        self.fee_pct = fee_pct
        self.effective_from = effective_from
        self.changed_by = changed_by
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "merchant_id": self.merchant_id,
            "fee_pct": self.fee_pct,
            "effective_from": self.effective_from,
            "changed_by": self.changed_by,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MerchantFeeHistory":
        """Create MerchantFeeHistory instance from dictionary."""
        return cls(
            history_id=data["_id"],
            merchant_id=data["merchant_id"],
            fee_pct=data["fee_pct"],
            effective_from=data["effective_from"],
            changed_by=data["changed_by"],
            created_at=data["created_at"]
        )
