"""
Pydantic schemas for Appointment model
"""
from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime, date, time
from .doctor import DoctorResponse
from .patient import PatientResponse


class AppointmentBase(BaseModel):
    """Base appointment schema"""
    patient_id: Union[int, str]  # Can be patient ID or email
    doctor_id: int
    appointment_date: date
    appointment_time: time
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment"""
    pass


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response"""
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AppointmentWithDetails(AppointmentResponse):
    """Schema for appointment with patient and doctor details"""
    patient: PatientResponse
    doctor: DoctorResponse


class TimeSlotRequest(BaseModel):
    """Schema for requesting available time slots"""
    doctor_id: int
    date: date


class TimeSlotResponse(BaseModel):
    """Schema for time slot response"""
    time: time
    is_available: bool
