from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.common.types import TransactionType, TransactionStatus, Currency


class PurchaseRequest(BaseModel):
    """Request schema for purchase transaction."""
    user_id: int = Field(..., description="User ID (custom auto-increment)")
    merchant_id: int = Field(..., description="Merchant ID (custom auto-increment)")
    amount: float = Field(..., gt=0, description="Purchase amount")
    currency: Currency = Field(Currency.INR, description="Currency")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PaymentRequest(BaseModel):
    """Request schema for payment transaction."""
    user_id: int = Field(..., description="User ID (custom auto-increment)")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: Currency = Field(Currency.INR, description="Currency")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TransactionResponse(BaseModel):
    """Response schema for transaction data."""
    id: str = Field(..., description="Transaction ID")
    type: TransactionType = Field(..., description="Transaction type")
    user_id: Optional[int] = Field(None, description="User ID (custom auto-increment)")
    merchant_id: Optional[int] = Field(None, description="Merchant ID (custom auto-increment)")
    amount: float = Field(..., description="Transaction amount")
    currency: Currency = Field(..., description="Currency")
    status: TransactionStatus = Field(..., description="Transaction status")
    applied_fee_pct: Optional[float] = Field(None, description="Applied fee percentage")
    fee_amount: Optional[float] = Field(None, description="Fee amount")
    merchant_payout_amount: Optional[float] = Field(None, description="Merchant payout amount")
    balance_before: Optional[float] = Field(None, description="Balance before transaction")
    balance_after: Optional[float] = Field(None, description="Balance after transaction")
    reason: Optional[str] = Field(None, description="Reason for rejection/reversal")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Transaction creation timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            ObjectId: str
        }
    }


class PurchaseResponse(BaseModel):
    """Response schema for purchase transaction."""
    transaction: TransactionResponse = Field(..., description="Transaction details")
    message: str = Field(..., description="Response message")


class PaymentResponse(BaseModel):
    """Response schema for payment transaction."""
    transaction: TransactionResponse = Field(..., description="Transaction details")
    message: str = Field(..., description="Response message")


class TransactionListResponse(BaseModel):
    """Response schema for transaction list with pagination."""
    transactions: List[TransactionResponse] = Field(..., description="List of transactions")
    total: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether there are more pages")
    
    model_config = {
        "json_encoders": {
            ObjectId: str
        }
    }


class TransactionFilter(BaseModel):
    """Query parameters for filtering transactions."""
    user_id: Optional[int] = Field(None, description="Filter by user ID (custom auto-increment)")
    merchant_id: Optional[int] = Field(None, description="Filter by merchant ID (custom auto-increment)")
    type: Optional[TransactionType] = Field(None, description="Filter by transaction type")
    status: Optional[TransactionStatus] = Field(None, description="Filter by transaction status")
    from_date: Optional[datetime] = Field(None, description="Filter from date")
    to_date: Optional[datetime] = Field(None, description="Filter to date")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")


class TransactionSummary(BaseModel):
    """Summary statistics for transactions."""
    total_transactions: int = Field(..., description="Total number of transactions")
    total_amount: float = Field(..., description="Total transaction amount")
    total_fees: float = Field(..., description="Total fees collected")
    purchase_count: int = Field(..., description="Number of purchases")
    payment_count: int = Field(..., description="Number of payments")
    approved_count: int = Field(..., description="Number of approved transactions")
    rejected_count: int = Field(..., description="Number of rejected transactions")
    
    model_config = {
        "json_encoders": {
            ObjectId: str
        }
    }
