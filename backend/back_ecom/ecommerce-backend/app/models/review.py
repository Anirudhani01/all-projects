from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=10, max_length=1000)


class ReviewCreate(ReviewBase):
    productId: str
    userName: str = Field(..., min_length=1, max_length=100)


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, min_length=10, max_length=1000)


class Review(ReviewBase):
    id: str = Field(alias="_id")
    productId: str
    userId: str
    userName: str
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True


class ReviewResponse(BaseModel):
    success: bool
    data: Review
    message: str


class ReviewList(BaseModel):
    success: bool
    data: List[Review]
    message: str
