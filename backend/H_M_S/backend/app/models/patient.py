"""
Patient model for the Hospital Management System
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..database import Base


class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}', email='{self.email}')>"
