from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from app.common.types import TransactionType, TransactionStatus, Currency


class Transaction:
    """Transaction document model."""
    
    def __init__(
        self,
        type: TransactionType,
        user_id: ObjectId,
        amount: float,
        currency: Currency = Currency.INR,
        status: TransactionStatus = TransactionStatus.APPROVED,
        transaction_id: Optional[ObjectId] = None,
        merchant_id: Optional[ObjectId] = None,
        applied_fee_pct: Optional[float] = None,
        fee_amount: Optional[float] = None,
        total_amount: Optional[float] = None,
        merchant_payout_amount: Optional[float] = None,
        balance_before: Optional[float] = None,
        balance_after: Optional[float] = None,
        merchant_wallet_balance_before: Optional[float] = None,
        merchant_wallet_balance_after: Optional[float] = None,
        user_credit_before: Optional[float] = None,
        user_credit_after: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = transaction_id or ObjectId()
        self.type = type
        self.user_id = user_id
        self.merchant_id = merchant_id
        self.amount = amount
        self.currency = currency
        self.status = status
        self.applied_fee_pct = applied_fee_pct
        self.fee_amount = fee_amount
        self.total_amount = total_amount
        self.merchant_payout_amount = merchant_payout_amount
        self.balance_before = balance_before
        self.balance_after = balance_after
        self.merchant_wallet_balance_before = merchant_wallet_balance_before
        self.merchant_wallet_balance_after = merchant_wallet_balance_after
        self.user_credit_before = user_credit_before
        self.user_credit_after = user_credit_after
        self.idempotency_key = idempotency_key
        self.reason = reason
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "type": self.type,
            "user_id": self.user_id,
            "merchant_id": self.merchant_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "applied_fee_pct": self.applied_fee_pct,
            "fee_amount": self.fee_amount,
            "total_amount": self.total_amount,
            "merchant_payout_amount": self.merchant_payout_amount,
            "balance_before": self.balance_before,
            "balance_after": self.balance_after,
            "merchant_wallet_balance_before": self.merchant_wallet_balance_before,
            "merchant_wallet_balance_after": self.merchant_wallet_balance_after,
            "user_credit_before": self.user_credit_before,
            "user_credit_after": self.user_credit_after,
            "idempotency_key": self.idempotency_key,
            "reason": self.reason,
            "metadata": self.metadata,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create Transaction instance from dictionary."""
        return cls(
            transaction_id=data["_id"],
            type=TransactionType(data["type"]),
            user_id=data["user_id"],
            merchant_id=data.get("merchant_id"),
            amount=data["amount"],
            currency=Currency(data["currency"]),
            status=TransactionStatus(data["status"]),
            applied_fee_pct=data.get("applied_fee_pct"),
            fee_amount=data.get("fee_amount"),
            total_amount=data.get("total_amount"),
            merchant_payout_amount=data.get("merchant_payout_amount"),
            balance_before=data.get("balance_before"),
            balance_after=data.get("balance_after"),
            merchant_wallet_balance_before=data.get("merchant_wallet_balance_before"),
            merchant_wallet_balance_after=data.get("merchant_wallet_balance_after"),
            user_credit_before=data.get("user_credit_before"),
            user_credit_after=data.get("user_credit_after"),
            idempotency_key=data.get("idempotency_key"),
            reason=data.get("reason"),
            metadata=data.get("metadata", {}),
            created_at=data["created_at"]
        )
    
    def is_purchase(self) -> bool:
        """Check if transaction is a purchase."""
        return self.type == TransactionType.PURCHASE
    
    def is_payment(self) -> bool:
        """Check if transaction is a payment."""
        return self.type == TransactionType.PAYMENT
    
    def is_wallet_add(self) -> bool:
        """Check if transaction is a wallet add."""
        return self.type == TransactionType.WALLET_ADD
    
    def is_wallet_payment(self) -> bool:
        """Check if transaction is a wallet payment."""
        return self.type == TransactionType.WALLET_PAYMENT
    
    def is_approved(self) -> bool:
        """Check if transaction is approved."""
        return self.status == TransactionStatus.APPROVED
    
    def is_rejected(self) -> bool:
        """Check if transaction is rejected."""
        return self.status == TransactionStatus.REJECTED


class IdempotencyKey:
    """Idempotency key document model."""
    
    def __init__(
        self,
        scope: str,
        key: str,
        response_hash: Optional[str] = None,
        key_id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        ttl_expires_at: Optional[datetime] = None
    ):
        self._id = key_id or ObjectId()
        self.scope = scope
        self.key = key
        self.response_hash = response_hash
        self.created_at = created_at or datetime.utcnow()
        self.ttl_expires_at = ttl_expires_at
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "scope": self.scope,
            "key": self.key,
            "response_hash": self.response_hash,
            "created_at": self.created_at,
            "ttl_expires_at": self.ttl_expires_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "IdempotencyKey":
        """Create IdempotencyKey instance from dictionary."""
        return cls(
            key_id=data["_id"],
            scope=data["scope"],
            key=data["key"],
            response_hash=data.get("response_hash"),
            created_at=data["created_at"],
            ttl_expires_at=data.get("ttl_expires_at")
        )
