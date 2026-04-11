"""
Transaction model for MongoDB document structure.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from .user import PyObjectId


class Transaction(BaseModel):
    """Transaction model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(...)
    merchant_id: PyObjectId = Field(...)
    transaction_type: str = Field(..., regex="^(purchase|payment|refund)$")
    amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD", regex="^[A-Z]{3}$")
    status: str = Field(default="pending", regex="^(pending|completed|failed|cancelled)$")
    description: str = Field(..., min_length=1, max_length=500)
    reference_id: Optional[str] = Field(None, max_length=100)
    payment_method: Optional[str] = Field(None, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}
    
    def __init__(self, **data):
        super().__init__(**data)
        # Update the updated_at field
        self.updated_at = datetime.utcnow()
