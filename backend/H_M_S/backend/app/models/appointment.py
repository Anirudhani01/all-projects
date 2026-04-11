"""
Appointment model for the Hospital Management System
"""
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base


class AppointmentStatus(str, enum.Enum):
    """Appointment status enum"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False, index=True)
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(Time, nullable=False, index=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING, index=True)
    notes = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, date={self.appointment_date}, time={self.appointment_time})>"
