from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("diary_entries.id"), nullable=False)
    booster_id = Column(Integer, ForeignKey("boosters.id"), nullable=True)
    rating = Column(Integer, nullable=False)  # 1-5 scale
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    diary_entry = relationship("DiaryEntry", back_populates="feedback")
    booster = relationship("Booster")
