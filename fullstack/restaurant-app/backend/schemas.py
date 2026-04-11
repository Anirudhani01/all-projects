from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict

class OrderBase(BaseModel):
    table_number: int
    items: List[Dict[str, float]]
    total_bill: float

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    entry_time: datetime
    closing_time: datetime | None

    class Config:
        from_attributes = True