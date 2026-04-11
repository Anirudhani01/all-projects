from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from bson import ObjectId


# Request Schemas
class AddToWalletRequest(BaseModel):
    """Request schema for adding money to merchant wallet."""
    merchant_id: str = Field(..., description="Merchant ID")
    amount: float = Field(..., gt=0, description="Amount to add to wallet")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key for duplicate prevention")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 1000000:  # 1M limit
            raise ValueError('Amount cannot exceed 1,000,000')
        return round(v, 2)


class WalletPaymentRequest(BaseModel):
    """Request schema for wallet payment to PayLater."""
    amount: float = Field(..., gt=0, description="Payment amount")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key for duplicate prevention")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 1000000:  # 1M limit
            raise ValueError('Amount cannot exceed 1,000,000')
        return round(v, 2)


class WalletTransactionFilter(BaseModel):
    """Filter schema for wallet transactions."""
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    merchant_id: Optional[str] = Field(None, description="Filter by merchant ID")
    limit: int = Field(50, ge=1, le=1000, description="Number of transactions to return")


# Response Schemas
class WalletAddResponse(BaseModel):
    """Response schema for wallet add operation."""
    transaction_id: str
    amount: float
    fee_amount: float
    total_amount: float
    merchant_name: str
    merchant_balance_before: float
    merchant_balance_after: float
    user_credit_before: float
    user_credit_after: float
    success: bool = True
    message: str = "Successfully added to merchant wallet"


class WalletPaymentResponse(BaseModel):
    """Response schema for wallet payment operation."""
    transaction_id: str
    amount: float
    outstanding_before: float
    outstanding_after: float
    available_credit_before: float
    available_credit_after: float
    success: bool = True
    message: str = "Payment processed successfully"


class UserCreditInfoResponse(BaseModel):
    """Response schema for user credit information."""
    user_id: str
    credit_limit: float
    outstanding_amount: float
    available_credit: float
    total_merchant_usage: float
    reached_limit: bool
    
    @field_validator('reached_limit', mode='before')
    @classmethod
    def calculate_reached_limit(cls, v, info):
        if info.data:
            return info.data.get('available_credit', 0) <= 0
        return v


class MerchantWalletBalanceResponse(BaseModel):
    """Response schema for merchant wallet balance."""
    merchant_id: str
    merchant_name: str
    wallet_balance: float
    total_received: float
    fee_percentage: float


class WalletTransactionResponse(BaseModel):
    """Response schema for wallet transaction."""
    transaction_id: str
    type: str
    user_id: str
    merchant_id: Optional[str]
    amount: float
    fee_amount: float
    total_amount: float
    currency: str
    status: str
    merchant_wallet_balance_before: Optional[float]
    merchant_wallet_balance_after: Optional[float]
    user_credit_before: Optional[float]
    user_credit_after: Optional[float]
    reason: Optional[str]
    created_at: datetime


class UserMerchantUsageResponse(BaseModel):
    """Response schema for user merchant usage."""
    user_id: str
    total_usage: float
    merchant_breakdown: Dict[str, float]
    credit_limit: float
    available_credit: float
    outstanding_amount: float
    merchant_count: int
    
    @field_validator('merchant_count', mode='before')
    @classmethod
    def calculate_merchant_count(cls, v, info):
        if info.data:
            return len(info.data.get('merchant_breakdown', {}))
        return v


class MerchantWalletSummaryResponse(BaseModel):
    """Response schema for merchant wallet summary."""
    merchant_id: str
    merchant_name: str
    current_balance: float
    total_received: float
    total_fees: float
    transaction_count: int
    fee_percentage: float


class WalletTransactionsResponse(BaseModel):
    """Response schema for wallet transactions list."""
    transactions: List[WalletTransactionResponse]
    total_count: int
    limit: int
    has_more: bool


# Error Response Schemas
class WalletErrorResponse(BaseModel):
    """Error response schema for wallet operations."""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# Summary Schemas
class WalletSummaryResponse(BaseModel):
    """Summary response for wallet operations."""
    total_users: int
    total_merchants: int
    total_transactions: int
    total_outstanding: float
    total_fees_collected: float
    active_wallets: int


# Utility Schemas
class IdempotencyKeyResponse(BaseModel):
    """Response schema for idempotency key validation."""
    key: str
    exists: bool
    transaction_id: Optional[str] = None


class WalletHealthResponse(BaseModel):
    """Health check response for wallet system."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    database_connected: bool
    services_healthy: bool
