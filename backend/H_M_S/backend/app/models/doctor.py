"""
Doctor model for the Hospital Management System
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base


class Doctor(Base):
    """Doctor model"""
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    specialization = Column(String(50), nullable=False, index=True)
    education = Column(Text)
    experience = Column(Integer, default=0)
    image_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Doctor(id={self.id}, name='{self.name}', specialization='{self.specialization}')>"
