"""Data models for the ecommerce CLI application."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class ProductCategory(str, Enum):
    """Product category enumeration."""

    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    HOME_GARDEN = "home_garden"
    SPORTS = "sports"
    BEAUTY = "beauty"
    AUTOMOTIVE = "automotive"


class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "admin"
    CUSTOMER = "customer"
    SELLER = "seller"


class Product(BaseModel):
    """Product model."""

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=1000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    category: ProductCategory
    stock_quantity: int = Field(..., ge=0)
    sku: str = Field(..., min_length=1, max_length=50)
    brand: str = Field(..., min_length=1, max_length=100)
    tags: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    weight_kg: Optional[Decimal] = Field(None, gt=0)
    dimensions: Optional[Dict[str, Decimal]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    @validator("sku")
    def validate_sku(cls, v: str) -> str:
        """Validate SKU format."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "SKU must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v.upper()

    class Config:
        """Pydantic config."""

        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: str,
        }


class User(BaseModel):
    """User model."""

    id: UUID = Field(default_factory=uuid4)
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, regex=r"^\+?1?\d{9,15}$")
    role: UserRole = UserRole.CUSTOMER
    address: Optional[Dict[str, str]] = None
    date_of_birth: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    last_login: Optional[datetime] = None

    @validator("username")
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v.lower()

    class Config:
        """Pydantic config."""

        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class OrderItem(BaseModel):
    """Order item model."""

    product_id: UUID
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)
    total_price: Decimal = Field(..., gt=0, decimal_places=2)

    @validator("total_price")
    def validate_total_price(cls, v: Decimal, values: Dict) -> Decimal:
        """Validate total price calculation."""
        quantity = values.get("quantity", 1)
        unit_price = values.get("unit_price", Decimal("0"))
        expected_total = quantity * unit_price
        if abs(v - expected_total) > Decimal("0.01"):
            raise ValueError("Total price must equal quantity * unit_price")
        return v

    class Config:
        """Pydantic config."""

        json_encoders = {
            UUID: str,
            Decimal: str,
        }


class Order(BaseModel):
    """Order model."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    items: List[OrderItem] = Field(..., min_items=1)
    status: OrderStatus = OrderStatus.PENDING
    total_amount: Decimal = Field(..., gt=0, decimal_places=2)
    shipping_address: Dict[str, str]
    billing_address: Optional[Dict[str, str]] = None
    payment_method: str = Field(..., min_length=1)
    shipping_cost: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    tax_amount: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None

    @validator("total_amount")
    def validate_total_amount(cls, v: Decimal, values: Dict) -> Decimal:
        """Validate total amount calculation."""
        items = values.get("items", [])
        shipping_cost = values.get("shipping_cost", Decimal("0"))
        tax_amount = values.get("tax_amount", Decimal("0"))
        discount_amount = values.get("discount_amount", Decimal("0"))

        items_total = sum(item.total_price for item in items)
        expected_total = items_total + shipping_cost + tax_amount - discount_amount

        if abs(v - expected_total) > Decimal("0.01"):
            raise ValueError("Total amount calculation is incorrect")
        return v

    class Config:
        """Pydantic config."""

        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: str,
        }


class Cart(BaseModel):
    """Shopping cart model."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    items: List[OrderItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    @property
    def total_amount(self) -> Decimal:
        """Calculate total cart amount."""
        return sum(item.total_price for item in self.items)

    @property
    def total_items(self) -> int:
        """Calculate total number of items."""
        return sum(item.quantity for item in self.items)

    class Config:
        """Pydantic config."""

        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: str,
        }


class Inventory(BaseModel):
    """Inventory model for tracking stock levels."""

    product_id: UUID
    quantity_available: int = Field(..., ge=0)
    quantity_reserved: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    max_stock_level: int = Field(default=1000, gt=0)
    location: Optional[str] = None
    last_restocked: Optional[datetime] = None
    supplier: Optional[str] = None

    @property
    def quantity_in_stock(self) -> int:
        """Calculate available stock after reservations."""
        return max(0, self.quantity_available - self.quantity_reserved)

    @property
    def needs_restock(self) -> bool:
        """Check if product needs restocking."""
        return self.quantity_available <= self.reorder_level

    class Config:
        """Pydantic config."""

        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class Review(BaseModel):
    """Product review model."""

    id: UUID = Field(default_factory=uuid4)
    product_id: UUID
    user_id: UUID
    order_id: Optional[UUID] = None
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=1, max_length=200)
    comment: str = Field(..., min_length=1, max_length=2000)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_verified_purchase: bool = False
    helpful_votes: int = Field(default=0, ge=0)

    class Config:
        """Pydantic config."""

        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
