from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    session_data = Column(Text, nullable=True)
    duration = Column(Integer, default=0)  # in minutes
    interactions = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, nullable=True)
