from pydantic import BaseModel
from typing import Dict, Any

class MoodAnalysis(BaseModel):
    mood: str
    confidence: float
    emotions: Dict[str, float] = {}
    keywords: list[str] = []

class MoodResponse(BaseModel):
    mood: str
    confidence: float
    analysis: str
    suggestions: list[str] = []
