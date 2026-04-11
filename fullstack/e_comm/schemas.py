from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_url: str
    class Config:
        orm_mode = True

class CartItem(BaseModel):
    product_id: int
    quantity: int

class PaymentInfo(BaseModel):
    product_name: str
    amount: float
    mode: str
    email: EmailStr

class OrderOut(BaseModel):
    id: int
    product_name: str
    price: float
    status: str
    order_date: datetime
    email: EmailStr
    class Config:
        orm_mode = True
