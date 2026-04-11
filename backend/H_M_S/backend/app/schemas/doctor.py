"""
Pydantic schemas for Doctor model
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class DoctorBase(BaseModel):
    """Base doctor schema"""
    name: str
    specialization: str
    education: Optional[str] = None
    experience: int = 0
    image_url: Optional[str] = None
    is_active: bool = True


class DoctorCreate(DoctorBase):
    """Schema for creating a doctor"""
    pass


class DoctorUpdate(BaseModel):
    """Schema for updating a doctor"""
    name: Optional[str] = None
    specialization: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class DoctorResponse(DoctorBase):
    """Schema for doctor response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DoctorList(BaseModel):
    """Schema for doctor list response"""
    doctors: list[DoctorResponse]
    total: int
    page: int
    size: int
