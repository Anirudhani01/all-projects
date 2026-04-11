from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.modules.users.models import User, UserBalance, UserBank

class UserResponse(BaseModel):
    """User response schema."""
    id: str
    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        """Create UserResponse from User model."""
        return cls(
            id=user.id or "",
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

class UserBalanceResponse(BaseModel):
    """User balance response schema."""
    user_id: int
    credit_limit: float
    outstanding_amount: float
    available_credit: float
    total_merchant_usage: float
    total_purchases: float
    total_payments: float
    reached_limit: bool
    utilization_percentage: float
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

    @classmethod
    def from_user_balance(cls, balance: UserBalance) -> "UserBalanceResponse":
        """Create UserBalanceResponse from UserBalance model."""
        return cls(
            user_id=balance.user_id,
            credit_limit=balance.credit_limit,
            outstanding_amount=balance.outstanding_amount,
            available_credit=balance.available_credit,
            total_merchant_usage=balance.total_merchant_usage,
            total_purchases=balance.total_purchases,
            total_payments=balance.total_payments,
            reached_limit=balance.reached_limit,
            utilization_percentage=balance.credit_utilization_percentage,
            created_at=balance.created_at,
            updated_at=balance.updated_at
        )

class UserBankResponse(BaseModel):
    """User bank response schema."""
    user_id: int
    balance: float
    total_deposited: float
    total_withdrawn: float
    last_transaction_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

    @classmethod
    def from_user_bank(cls, bank: UserBank) -> "UserBankResponse":
        """Create UserBankResponse from UserBank model."""
        return cls(
            user_id=bank.user_id,
            balance=bank.balance,
            total_deposited=bank.total_deposited,
            total_withdrawn=bank.total_withdrawn,
            last_transaction_at=bank.last_transaction_at,
            created_at=bank.created_at,
            updated_at=bank.updated_at
        )

class UserCreditInfoResponse(BaseModel):
    """User credit information response schema."""
    user_id: int
    credit_limit: float
    available_credit: float
    outstanding_amount: float
    total_merchant_usage: float
    total_purchases: float
    total_payments: float
    reached_limit: bool
    utilization_percentage: float

    model_config = {
        "from_attributes": True
    }

class UserFinancialSummaryResponse(BaseModel):
    """User comprehensive financial summary response schema."""
    user: dict
    credit: dict
    bank: dict

    model_config = {
        "from_attributes": True
    }

class UserDuesResponse(BaseModel):
    """User dues response schema (legacy support)."""
    user_id: str
    outstanding_amount: float
    total_purchases: float
    total_payments: float
    available_credit: float
    credit_limit: float
    reached_limit: bool

    model_config = {
        "from_attributes": True
    }

class UserListResponse(BaseModel):
    """User list response schema."""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int

    model_config = {
        "from_attributes": True
    }

class CreateUserRequest(BaseModel):
    """Create user request schema."""
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: str = Field(..., description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate name."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class UpdateUserRequest(BaseModel):
    """Update user request schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's full name")
    phone: Optional[str] = Field(None, description="User's phone number")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate name if provided."""
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v

class RepaymentRequest(BaseModel):
    """Repayment request schema."""
    amount: float = Field(..., gt=0, description="Repayment amount")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate repayment amount."""
        if v <= 0:
            raise ValueError('Repayment amount must be positive')
        return round(v, 2)

class DepositRequest(BaseModel):
    """Deposit request schema."""
    amount: float = Field(..., gt=0, description="Deposit amount")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate deposit amount."""
        if v <= 0:
            raise ValueError('Deposit amount must be positive')
        return round(v, 2)

class RepaymentResponse(BaseModel):
    """Repayment response schema."""
    success: bool
    message: str
    repayment_amount: float
    new_outstanding_amount: float
    new_bank_balance: float

    model_config = {
        "from_attributes": True
    }

class DepositResponse(BaseModel):
    """Deposit response schema."""
    success: bool
    message: str
    deposit_amount: float
    new_balance: float

    model_config = {
        "from_attributes": True
    }

class BankBalanceResponse(BaseModel):
    """Bank balance response schema."""
    user_id: int
    bank_balance: float
    message: str

    model_config = {
        "from_attributes": True
    }

class MerchantUsageResponse(BaseModel):
    """Merchant usage response schema."""
    user_id: int
    total_merchant_usage: float
    total_purchases: float
    total_payments: float
    outstanding_amount: float
    available_credit: float

    model_config = {
        "from_attributes": True
    }
