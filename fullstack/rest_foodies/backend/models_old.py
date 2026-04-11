from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class OrderStatus(str, Enum):
    open = "open"
    paid = "paid"

class PaymentMethod(str, Enum):
    cash = "cash"
    online = "online"

class MenuItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    is_out_of_stock: bool = Field(default=False, index=True)
    is_active: bool = Field(default=True, index=True)
    order_items: List["OrderItem"] = Relationship(back_populates="menu_item")

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    table_number: int = Field(index=True)
    status: OrderStatus = Field(default=OrderStatus.open, index=True)
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None
    payment_method: Optional[PaymentMethod] = Field(default=None)
    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    menu_item_id: int = Field(foreign_key="menuitem.id", index=True)
    name_snapshot: str
    price_snapshot: float
    quantity: int = Field(ge=1)
    order: Optional[Order] = Relationship(back_populates="items")
    menu_item: Optional[MenuItem] = Relationship(back_populates="order_items")
