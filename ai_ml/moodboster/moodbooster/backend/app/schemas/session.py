from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionBase(BaseModel):
    session_id: str
    session_data: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: int
    duration: int
    interactions: int
    created_at: datetime
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True
