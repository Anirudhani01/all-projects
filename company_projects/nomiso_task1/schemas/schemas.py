from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# Base schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    category: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class CartItemBase(BaseModel):
    item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=1000)
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        if v > 1000:
            raise ValueError('Quantity cannot exceed 1000')
        return v

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    user_id: int
    added_at: datetime
    item: Item
    
    class Config:
        orm_mode = True

class CartResponse(BaseModel):
    items: List[CartItem]
    total: float
    item_count: int

class AddToCartResponse(BaseModel):
    message: str
    cart_total: float
    item_added: dict

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    username: Optional[str] = None

# Error response schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    error: str
    details: List[dict]
