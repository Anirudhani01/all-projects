from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field as SQLField, Relationship

# SQLModel ORM Models
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    user_id: Optional[int] = SQLField(default=None, primary_key=True)
    email: str = SQLField(index=True, max_length=100)
    password_hash: str = SQLField(max_length=255)
    full_name: Optional[str] = SQLField(max_length=100, default=None)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    cart_items: List["CartItem"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    category_id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str = SQLField(index=True, max_length=100)
    
    # Relationships
    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    __tablename__ = "products"
    
    product_id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str = SQLField(max_length=255, index=True)
    description: Optional[str] = SQLField(default=None)
    price: Decimal = SQLField()
    stock_quantity: int = SQLField(default=0)
    category_id: Optional[int] = SQLField(default=None, foreign_key="categories.category_id")
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    category: Optional[Category] = Relationship(back_populates="products")
    cart_items: List["CartItem"] = Relationship(back_populates="product")
    order_items: List["OrderItem"] = Relationship(back_populates="product")

class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"
    
    cart_item_id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(foreign_key="users.user_id")
    product_id: int = SQLField(foreign_key="products.product_id")
    quantity: int = SQLField(default=1)
    
    # Relationships
    user: User = Relationship(back_populates="cart_items")
    product: Product = Relationship(back_populates="cart_items")

class Order(SQLModel, table=True):
    __tablename__ = "orders"
    
    order_id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(foreign_key="users.user_id")
    total_amount: Decimal = SQLField()
    status: str = SQLField(default="PENDING", max_length=50)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")
    payment: Optional["Payment"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    
    order_item_id: Optional[int] = SQLField(default=None, primary_key=True)
    order_id: int = SQLField(foreign_key="orders.order_id")
    product_id: int = SQLField(foreign_key="products.product_id")
    quantity: int = SQLField(default=1)
    price_at_purchase: Decimal = SQLField()
    
    # Relationships
    order: Order = Relationship(back_populates="order_items")
    product: Product = Relationship(back_populates="order_items")

class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    
    payment_id: Optional[int] = SQLField(default=None, primary_key=True)
    order_id: int = SQLField(foreign_key="orders.order_id")
    amount: Decimal = SQLField()
    payment_method: Optional[str] = SQLField(max_length=50, default=None)
    status: str = SQLField(max_length=50)
    transaction_id: Optional[str] = SQLField(max_length=255, default=None)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    order: Order = Relationship(back_populates="payment")

# Pydantic Models (existing code continues...)
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class CategoryCreate(CategoryBase):
    pass

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    stock_quantity: int = Field(..., ge=0)
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None

class ProductDetail(ProductBase):
    product_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    product_id: int
    name: str
    description: Optional[str]
    price: Decimal
    stock_quantity: int
    category_id: int

# Cart Models
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItem(CartItemBase):
    cart_item_id: int
    user_id: int
    
    class Config:
        from_attributes = True

class CartItemWithProduct(CartItem):
    product: ProductDetail

# Cart Service Models
class CartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)  # Quantity must be positive

class CartItemResponse(BaseModel):
    product_id: int
    name: str
    price: Decimal
    quantity: int
    sub_total: Decimal

class CartResponse(BaseModel):
    items: list
    total_price: Decimal

# Order Models
class OrderBase(BaseModel):
    total_amount: Decimal = Field(..., ge=0)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None

class Order(OrderBase):
    order_id: int
    user_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order Item Models
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    price_at_purchase: Decimal = Field(..., ge=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    order_item_id: int
    order_id: int
    
    class Config:
        from_attributes = True

class OrderItemWithProduct(OrderItem):
    product: ProductDetail

# Payment Models
class PaymentBase(BaseModel):
    amount: Decimal = Field(..., ge=0)
    payment_method: Optional[str] = None

class PaymentCreate(PaymentBase):
    order_id: int

class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    transaction_id: Optional[str] = None

class Payment(PaymentBase):
    payment_id: int
    order_id: int
    status: str
    transaction_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Response Models
class OrderWithItems(Order):
    order_items: List[OrderItemWithProduct]

class OrderWithPayment(Order):
    payment: Optional[Payment] = None

# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int

# Order Service Models
class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: Decimal

class OrderResponse(BaseModel):
    order_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    items: list

class OrderSummaryResponse(BaseModel):
    order_id: int
    status: str
    total_amount: Decimal
    created_at: datetime

# Payment Service Models
class PaymentRequest(BaseModel):
    order_id: int
    payment_token: str  # e.g., "tok_visa_4242"

class PaymentResponse(BaseModel):
    status: str
    transaction_id: str
