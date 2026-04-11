"""
Contact model for contact form submissions
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base


class ContactMessage(Base):
    """Contact message model for contact form submissions"""
    __tablename__ = "contact_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, index=True)
    phone = Column(String(20))
    subject = Column(String(200))
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ContactMessage(id={self.id}, name='{self.name}', email='{self.email}', read={self.is_read})>"
