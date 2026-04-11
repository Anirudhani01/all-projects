"""
TimeSlot model for managing appointment availability
"""
from sqlalchemy import Column, Integer, Time, Date, Boolean, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base


class TimeSlot(Base):
    """TimeSlot model for managing appointment availability"""
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    time = Column(Time, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    is_available = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Ensure unique combination of time and date
    __table_args__ = (
        UniqueConstraint('time', 'date', name='unique_time_date'),
    )
    
    def __repr__(self):
        return f"<TimeSlot(id={self.id}, time={self.time}, date={self.date}, available={self.is_available})>"
