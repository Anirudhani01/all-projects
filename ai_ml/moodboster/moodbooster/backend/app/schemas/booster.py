from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class BoosterBase(BaseModel):
    mood_type: str
    content_type: str
    title: str
    content: str
    booster_metadata: Optional[Dict[str, Any]] = None

class BoosterCreate(BoosterBase):
    pass

class BoosterResponse(BoosterBase):
    id: int
    popularity_score: float
    is_active: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
