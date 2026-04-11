from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId


class CreateMerchantRequest(BaseModel):
    """Request schema for creating a merchant."""
    name: str = Field(..., min_length=1, max_length=100, description="Merchant name")
    email: str = Field(..., description="Merchant email address")
    fee_pct: float = Field(..., ge=0.0, le=100.0, description="Fee percentage")


class UpdateFeeRequest(BaseModel):
    """Request schema for updating merchant fee."""
    fee_pct: float = Field(..., ge=0.0, le=100.0, description="New fee percentage")


class MerchantResponse(BaseModel):
    """Response schema for merchant data."""
    id: str = Field(..., description="Merchant ID (MongoDB ObjectId)")
    merchant_id: Optional[int] = Field(None, description="Merchant ID (Auto-increment)")
    name: str = Field(..., description="Merchant name")
    email: Optional[str] = Field(None, description="Merchant email address")
    current_fee_pct: float = Field(..., description="Current fee percentage")
    created_at: datetime = Field(..., description="Merchant creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            ObjectId: str
        }
    }


class MerchantListResponse(BaseModel):
    """Response schema for merchant list with pagination."""
    merchants: List[MerchantResponse] = Field(..., description="List of merchants")
    total: int = Field(..., description="Total number of merchants")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether there are more pages")
    
    model_config = {
        "json_encoders": {
            ObjectId: str
        }
    }


class FeeHistoryEntry(BaseModel):
    """Response schema for fee history entry."""
    id: str = Field(..., description="History entry ID")
    fee_pct: float = Field(..., description="Fee percentage")
    effective_from: datetime = Field(..., description="When this fee became effective")
    changed_by: str = Field(..., description="Who changed the fee")
    created_at: datetime = Field(..., description="When this entry was created")
    
    model_config = {
        "json_encoders": {
            ObjectId: str
        }
    }


class FeeHistoryResponse(BaseModel):
    """Response schema for fee history."""
    merchant_id: str = Field(..., description="Merchant ID")
    history: List[FeeHistoryEntry] = Field(..., description="Fee history entries")
    total: int = Field(..., description="Total number of entries")
    
    model_config = {
        "json_encoders": {
            ObjectId: str
        }
    }


class MerchantFeeHistoryFilter(BaseModel):
    """Query parameters for fee history."""
    from_date: Optional[datetime] = Field(None, description="Filter from date")
    to_date: Optional[datetime] = Field(None, description="Filter to date")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
