"""
Merchant model for MongoDB document structure.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from .user import PyObjectId, Address


class Merchant(BaseModel):
    """Merchant model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr = Field(..., unique=True, index=True)
    phone: str = Field(..., min_length=10, max_length=15)
    address: Address = Field(...)
    business_type: str = Field(..., min_length=1, max_length=100)
    tax_id: str = Field(..., min_length=1, max_length=50)
    is_active: bool = Field(default=True)
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
