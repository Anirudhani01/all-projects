from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base

class DiaryEntry(Base):
    __tablename__ = "diary_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    mood = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    word_count = Column(Integer, default=0)
    session_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="diary_entry", cascade="all, delete-orphan")
    context_analysis = relationship("ContextAnalysis", back_populates="diary_entry", cascade="all, delete-orphan")
    theme_analysis = relationship("ThemeAnalysis", back_populates="diary_entry", cascade="all, delete-orphan")
