from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    credit_limit: int

class MerchantCreate(BaseModel):
    name: str
    transaction_fee_percent: float

class FeeUpdate(BaseModel):
    transaction_fee_percent: float

class TransactionCreate(BaseModel):
    user_id: int
    merchant_id: int
    amount: float

class Repayment(BaseModel):
    user_id: int
    amount: float
