"""
Pydantic schemas for Patient model
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class PatientBase(BaseModel):
    """Base patient schema"""
    name: str
    phone: str
    email: EmailStr


class PatientCreate(PatientBase):
    """Schema for creating a patient"""
    pass


class PatientUpdate(BaseModel):
    """Schema for updating a patient"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class PatientResponse(PatientBase):
    """Schema for patient response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
