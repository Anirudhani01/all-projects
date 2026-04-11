"""
All database models for the Hospital Management System
"""
from .doctor import Doctor
from .patient import Patient
from .appointment import Appointment, AppointmentStatus
from .timeslot import TimeSlot
from .blog import BlogPost
from .contact import ContactMessage

# Add relationships
from sqlalchemy.orm import relationship

# Add relationships to existing models
Doctor.appointments = relationship("Appointment", back_populates="doctor")
Patient.appointments = relationship("Appointment", back_populates="patient")

# Export all models
__all__ = [
    "Doctor",
    "Patient", 
    "Appointment",
    "AppointmentStatus",
    "TimeSlot",
    "BlogPost",
    "ContactMessage"
]
