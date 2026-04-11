"""
User model for MongoDB document structure.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Address(BaseModel):
    """Address model."""
    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    zip_code: str = Field(..., min_length=5, max_length=10)
    country: str = Field(..., min_length=1, max_length=100)


class User(BaseModel):
    """User model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr = Field(..., unique=True, index=True)
    password_hash: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=10, max_length=15)
    date_of_birth: datetime = Field(...)
    ssn_hash: Optional[str] = Field(None, min_length=64, max_length=64)
    address: Address = Field(...)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    role: str = Field(default="user", regex="^(user|admin|merchant)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip_code": "10001",
                    "country": "USA"
                },
                "role": "user"
            }
        }
    
    def __init__(self, **data):
        super().__init__(**data)
        # Update the updated_at field
        self.updated_at = datetime.utcnow()
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "_id": self.id,
            "email": self.email,
            "password_hash": self.password_hash,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "date_of_birth": self.date_of_birth,
            "ssn_hash": self.ssn_hash,
            "address": self.address.dict(),
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from dictionary."""
        if "_id" in data:
            data["id"] = data.pop("_id")
        return cls(**data)
