from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class WishlistItemBase(BaseModel):
    productId: str = Field(..., min_length=1)


class WishlistItemCreate(WishlistItemBase):
    pass


class WishlistItem(WishlistItemBase):
    id: str = Field(alias="_id")
    userId: str
    addedAt: datetime
    
    class Config:
        populate_by_name = True


class WishlistResponse(BaseModel):
    success: bool
    data: List[WishlistItem]
    message: str


class WishlistCheckResponse(BaseModel):
    success: bool
    data: bool
    message: str
