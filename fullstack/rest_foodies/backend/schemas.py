from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from .models import PaymentMethod

class MenuItemRead(BaseModel):
    id: int
    name: str
    main_category: str
    sub_category: str
    price: float
    description: Optional[str]
    is_out_of_stock: bool
    is_active: bool
    class Config:
        from_attributes = True

class MenuItemCreate(BaseModel):
    name: str
    main_category: str
    sub_category: str
    price: float
    description: Optional[str] = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class MenuItemToggleOutOfStock(BaseModel):
    ids: List[int] = Field(default_factory=list)

class OrderItemAdd(BaseModel):
    menu_item_id: int
    quantity: int = Field(ge=1)

class OrderItemUpdate(BaseModel):
    quantity: int

class OrderItemRead(BaseModel):
    id: int
    menu_item_id: int
    name_snapshot: str
    price_snapshot: float
    quantity: int
    class Config:
        from_attributes = True

class OrderRead(BaseModel):
    id: int
    table_number: int
    status: str
    opened_at: datetime
    paid_at: Optional[datetime]
    payment_method: Optional[PaymentMethod]
    items: List[OrderItemRead]
    total_amount: float

class TableSummary(BaseModel):
    table_number: int
    status: str
    items: List[OrderItemRead]
    total_amount: float

class PayOrder(BaseModel):
    payment_method: PaymentMethod
