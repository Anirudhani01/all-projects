"""
Pydantic schemas for context analysis and theme extraction
"""

from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class HistorySummary(BaseModel):
    total_entries: int
    analysis_period_days: int
    last_entry_date: Optional[datetime]

class MoodTrends(BaseModel):
    trend: str  # improving, declining, stable, unclear
    direction: float
    confidence: float
    mood_distribution: Dict[str, int]
    average_confidence: float

class MoodPatterns(BaseModel):
    patterns: List[Dict[str, Any]]
    recurring_moods: List[Dict[str, Any]]
    triggers: List[str]
    pattern_count: int

class MoodStability(BaseModel):
    stability_score: float
    volatility: float
    change_rate: float
    stability_level: str  # high, medium, low
    consistency: str  # high, low

class ContextAnalysisResponse(BaseModel):
    user_id: str
    current_mood: str
    history_summary: HistorySummary
    trends: MoodTrends
    patterns: MoodPatterns
    stability: MoodStability
    context_summary: str
    enrichment_score: float

class CurrentTextThemes(BaseModel):
    categories: Dict[str, Any]
    triggers: List[Dict[str, Any]]
    key_phrases: List[str]
    word_count: int
    sentiment_indicators: List[str]

class LDAThemes(BaseModel):
    themes: List[Dict[str, Any]]
    dominant_topics: List[Dict[str, Any]]
    confidence: float

class CategoryThemes(BaseModel):
    categories: Dict[str, Any]
    total_categories: int

class Triggers(BaseModel):
    current_triggers: List[Dict[str, Any]]
    historical_triggers: List[Dict[str, Any]]
    trigger_summary: str

class ThemeEvolution(BaseModel):
    evolution: List[Dict[str, Any]]
    trends: List[str]

class ThemeAnalysisResponse(BaseModel):
    user_id: str
    current_text_themes: CurrentTextThemes
    lda_themes: LDAThemes
    category_themes: CategoryThemes
    triggers: Triggers
    theme_evolution: ThemeEvolution
    theme_summary: str
    analysis_confidence: float

class EnrichedMoodResponse(BaseModel):
    mood: str
    confidence: float
    emotions: Dict[str, float]
    keywords: List[str]
    context: ContextAnalysisResponse
    themes: ThemeAnalysisResponse
    enrichment_score: float

class UserProfileResponse(BaseModel):
    user_id: str
    preferred_booster_types: List[str]
    mood_sensitivity: float
    analysis_depth: str
    common_themes: Optional[Dict[str, Any]]
    mood_patterns: Optional[Dict[str, Any]]
    trigger_sensitivity: Optional[Dict[str, Any]]
    total_entries: int
    avg_entry_length: float
    engagement_score: float
    created_at: datetime
    updated_at: Optional[datetime]

class UserProfileUpdate(BaseModel):
    preferred_booster_types: Optional[List[str]] = None
    mood_sensitivity: Optional[float] = None
    analysis_depth: Optional[str] = None
    common_themes: Optional[Dict[str, Any]] = None
    mood_patterns: Optional[Dict[str, Any]] = None
    trigger_sensitivity: Optional[Dict[str, Any]] = None
