from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DiaryEntryBase(BaseModel):
    text: str
    session_id: Optional[str] = None

class DiaryEntryCreate(DiaryEntryBase):
    pass

class DiaryEntryResponse(DiaryEntryBase):
    id: int
    mood: str
    confidence: float
    word_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
