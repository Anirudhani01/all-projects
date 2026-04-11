from sqlalchemy import Column, Integer, String, Text, Float, JSON, DateTime
from app.database import Base

class Booster(Base):
    __tablename__ = "boosters"
    
    id = Column(Integer, primary_key=True, index=True)
    mood_type = Column(String(50), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)  # story, music, video, game, meditation
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    booster_metadata = Column(JSON, nullable=True)  # Additional data like URLs, settings, etc.
    popularity_score = Column(Float, default=0.0)
    is_active = Column(String(10), default="true")
    created_at = Column(DateTime, nullable=True)
