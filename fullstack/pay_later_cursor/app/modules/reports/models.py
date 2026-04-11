"""
Report models for LazyPay application.
"""

from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class FeeCollectionReport(BaseModel):
    """Model for fee collection report."""
    merchant_name: str
    fee_collected: float = Field(..., description="Total fee collected for the merchant")
    total_transactions: int = Field(..., description="Total number of transactions")
    period_start: Optional[datetime] = Field(None, description="Report period start date")
    period_end: Optional[datetime] = Field(None, description="Report period end date")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserDuesReport(BaseModel):
    """Model for user dues report."""
    user_name: str
    dues: float = Field(..., description="Total outstanding dues for the user")
    total_purchases: float = Field(..., description="Total purchases made by user")
    total_payments: float = Field(..., description="Total payments made by user")
    credit_limit: float = Field(..., description="User's credit limit")
    available_credit: float = Field(..., description="Available credit remaining")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UsersAtCreditLimitReport(BaseModel):
    """Model for users at credit limit report."""
    users: List[str] = Field(..., description="List of usernames at credit limit")
    total_count: int = Field(..., description="Total number of users at credit limit")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TotalDuesReport(BaseModel):
    """Model for total dues report."""
    total: float = Field(..., description="Total outstanding dues across all users")
    details: Dict[str, float] = Field(..., description="Dues breakdown by username")
    total_users_with_dues: int = Field(..., description="Number of users with outstanding dues")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReportFilter(BaseModel):
    """Model for report filtering options."""
    start_date: Optional[datetime] = Field(None, description="Report start date")
    end_date: Optional[datetime] = Field(None, description="Report end date")
    limit: Optional[int] = Field(100, description="Maximum number of records to return")
    offset: Optional[int] = Field(0, description="Number of records to skip")
