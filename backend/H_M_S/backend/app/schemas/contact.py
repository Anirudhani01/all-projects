"""
Pydantic schemas for Contact model
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ContactMessageBase(BaseModel):
    """Base contact message schema"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: Optional[str] = None
    message: str


class ContactMessageCreate(ContactMessageBase):
    """Schema for creating a contact message"""
    pass


class ContactMessageUpdate(BaseModel):
    """Schema for updating a contact message"""
    is_read: Optional[bool] = None


class ContactMessageResponse(ContactMessageBase):
    """Schema for contact message response"""
    id: int
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContactMessageList(BaseModel):
    """Schema for contact message list response"""
    messages: list[ContactMessageResponse]
    total: int
    page: int
    size: int
