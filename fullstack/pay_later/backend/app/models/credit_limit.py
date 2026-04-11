"""
Credit limit model for MongoDB document structure.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from .user import PyObjectId


class CreditLimit(BaseModel):
    """Credit limit model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(...)
    limit_amount: Decimal = Field(..., ge=0)
    used_amount: Decimal = Field(default=0, ge=0)
    available_amount: Decimal = Field(default=0, ge=0)
    credit_score: int = Field(..., ge=300, le=850)
    approval_status: str = Field(default="pending", regex="^(pending|approved|rejected)$")
    approved_by: Optional[PyObjectId] = Field(None)
    approved_at: Optional[datetime] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}
    
    def __init__(self, **data):
        super().__init__(**data)
        # Calculate available amount
        self.available_amount = self.limit_amount - self.used_amount
        # Update the updated_at field
        self.updated_at = datetime.utcnow()
