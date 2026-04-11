"""
Pydantic schemas for decision layer and content generation
"""

from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from enum import Enum

class ContentTypeEnum(str, Enum):
    QUOTE = "quote"
    STORY = "story"
    MEDITATION = "meditation"
    MUSIC = "music"
    GAME = "game"
    ACTIVITY = "activity"
    BREATHING = "breathing"

class StrategyTypeEnum(str, Enum):
    FOCUSED = "focused"
    BALANCED = "balanced"
    COMPREHENSIVE = "comprehensive"

class DeliveryApproachEnum(str, Enum):
    GENTLE = "gentle"
    CALMING = "calming"
    ENERGETIC = "energetic"
    NEUTRAL = "neutral"

class InteractionLevelEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ContentType(BaseModel):
    type: str
    priority: int
    score: float
    estimated_duration: int  # in minutes

class ResponseStrategy(BaseModel):
    strategy_type: StrategyTypeEnum
    delivery_approach: DeliveryApproachEnum
    interaction_level: InteractionLevelEnum
    content_sequence: List[str]
    personalization_factors: List[str]

class DecisionResponse(BaseModel):
    strategy: ResponseStrategy
    selected_content: List[ContentType]
    confidence: float
    reasoning: str
    estimated_duration: int
    personalization_score: float

class ContentRequest(BaseModel):
    content_type: str
    mood: str
    context: Optional[Dict[str, Any]] = None
    themes: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None

class QuoteContent(BaseModel):
    text: str
    author: Optional[str] = None
    category: str
    mood_affinity: float
    source: str

class StoryContent(BaseModel):
    title: str
    content: str
    genre: str
    mood_affinity: float
    estimated_reading_time: int
    themes: List[str]

class MeditationContent(BaseModel):
    title: str
    description: str
    duration: int
    type: str  # breathing, mindfulness, body_scan, etc.
    mood_affinity: float
    audio_url: Optional[str] = None
    instructions: List[str]

class MusicContent(BaseModel):
    title: str
    artist: str
    genre: str
    mood_affinity: float
    duration: int
    spotify_id: Optional[str] = None
    youtube_id: Optional[str] = None
    preview_url: Optional[str] = None

class GameContent(BaseModel):
    title: str
    description: str
    type: str  # memory, puzzle, trivia, etc.
    difficulty: str
    estimated_duration: int
    mood_affinity: float
    instructions: List[str]
    interactive_elements: List[str]

class ActivityContent(BaseModel):
    title: str
    description: str
    category: str  # physical, creative, social, etc.
    estimated_duration: int
    mood_affinity: float
    materials_needed: List[str]
    instructions: List[str]
    benefits: List[str]

class BreathingContent(BaseModel):
    title: str
    description: str
    pattern: str  # 4-7-8, box breathing, etc.
    duration: int
    mood_affinity: float
    instructions: List[str]
    visual_guide: Optional[str] = None

class GeneratedContent(BaseModel):
    content_type: str
    content: Dict[str, Any]  # Flexible content based on type
    metadata: Dict[str, Any]
    generation_confidence: float
    personalization_score: float

class ContentGenerationResponse(BaseModel):
    success: bool
    generated_content: List[GeneratedContent]
    total_duration: int
    generation_time: float
    fallback_used: bool
    error_message: Optional[str] = None

class ResponseCombination(BaseModel):
    primary_content: GeneratedContent
    secondary_content: List[GeneratedContent]
    combination_strategy: str
    total_duration: int
    interaction_flow: List[str]
    engagement_score: float

class DecisionAnalysis(BaseModel):
    mood_analysis: Dict[str, Any]
    context_analysis: Dict[str, Any]
    theme_analysis: Dict[str, Any]
    decision_factors: List[str]
    confidence_breakdown: Dict[str, float]
    alternative_strategies: List[ResponseStrategy]
