"""
Report schemas for LazyPay application API.
"""

from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


# Request Schemas
class FeeReportRequest(BaseModel):
    """Request schema for fee collection report."""
    start_date: Optional[datetime] = Field(None, description="Report start date")
    end_date: Optional[datetime] = Field(None, description="Report end date")


class DuesReportRequest(BaseModel):
    """Request schema for user dues report."""
    include_details: Optional[bool] = Field(False, description="Include detailed breakdown")


class TotalDuesReportRequest(BaseModel):
    """Request schema for total dues report."""
    include_inactive_users: Optional[bool] = Field(False, description="Include inactive users")


# Response Schemas
class FeeCollectionResponse(BaseModel):
    """Response schema for fee collection report."""
    fee_collected: float = Field(..., description="Total fee collected for the merchant")
    total_transactions: int = Field(..., description="Total number of transactions")
    period_start: Optional[datetime] = Field(None, description="Report period start date")
    period_end: Optional[datetime] = Field(None, description="Report period end date")


class UserDuesResponse(BaseModel):
    """Response schema for user dues report."""
    dues: float = Field(..., description="Total outstanding dues for the user")
    total_purchases: Optional[float] = Field(None, description="Total purchases made by user")
    total_payments: Optional[float] = Field(None, description="Total payments made by user")
    credit_limit: Optional[float] = Field(None, description="User's credit limit")
    available_credit: Optional[float] = Field(None, description="Available credit remaining")


class UsersAtCreditLimitResponse(BaseModel):
    """Response schema for users at credit limit report."""
    users: List[str] = Field(..., description="List of usernames at credit limit")
    total_count: int = Field(..., description="Total number of users at credit limit")


class TotalDuesResponse(BaseModel):
    """Response schema for total dues report."""
    total: float = Field(..., description="Total outstanding dues across all users")
    details: Dict[str, float] = Field(..., description="Dues breakdown by username")
    total_users_with_dues: int = Field(..., description="Number of users with outstanding dues")


# Error Response Schemas
class ReportErrorResponse(BaseModel):
    """Error response schema for reports."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
