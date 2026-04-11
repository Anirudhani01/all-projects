"""
Pydantic schemas for Blog model
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BlogPostBase(BaseModel):
    """Base blog post schema"""
    title: str
    content: str
    category: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: bool = False


class BlogPostCreate(BlogPostBase):
    """Schema for creating a blog post"""
    pass


class BlogPostUpdate(BaseModel):
    """Schema for updating a blog post"""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: Optional[bool] = None


class BlogPostResponse(BlogPostBase):
    """Schema for blog post response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BlogPostList(BaseModel):
    """Schema for blog post list response"""
    posts: list[BlogPostResponse]
    total: int
    page: int
    size: int
