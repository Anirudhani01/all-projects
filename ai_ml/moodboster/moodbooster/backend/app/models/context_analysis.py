"""
Database models for context analysis and theme extraction
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class ContextAnalysis(Base):
    """Store context analysis results for diary entries"""
    __tablename__ = "context_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    diary_entry_id = Column(Integer, ForeignKey("diary_entries.id"), nullable=False)
    user_id = Column(String(100), nullable=False)
    
    # Context analysis results
    mood_trend = Column(String(50), nullable=True)  # improving, declining, stable
    trend_confidence = Column(Float, nullable=True)
    mood_stability = Column(String(50), nullable=True)  # high, medium, low
    stability_score = Column(Float, nullable=True)
    
    # Pattern analysis
    recurring_moods = Column(JSON, nullable=True)  # List of recurring moods
    day_patterns = Column(JSON, nullable=True)  # Day-of-week patterns
    mood_sequences = Column(JSON, nullable=True)  # Common mood progressions
    
    # Context summary
    context_summary = Column(Text, nullable=True)
    enrichment_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    diary_entry = relationship("DiaryEntry", back_populates="context_analysis")

class ThemeAnalysis(Base):
    """Store theme analysis results for diary entries"""
    __tablename__ = "theme_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    diary_entry_id = Column(Integer, ForeignKey("diary_entries.id"), nullable=False)
    user_id = Column(String(100), nullable=False)
    
    # LDA themes
    lda_themes = Column(JSON, nullable=True)  # LDA topic analysis
    lda_confidence = Column(Float, nullable=True)
    
    # Category themes
    category_themes = Column(JSON, nullable=True)  # Predefined category analysis
    top_categories = Column(JSON, nullable=True)  # Top 3 categories
    
    # Emotional triggers
    current_triggers = Column(JSON, nullable=True)  # Triggers in current text
    historical_triggers = Column(JSON, nullable=True)  # Historical trigger patterns
    
    # Theme evolution
    theme_evolution = Column(JSON, nullable=True)  # How themes have changed
    new_themes = Column(JSON, nullable=True)  # Newly emerging themes
    disappeared_themes = Column(JSON, nullable=True)  # Themes that have faded
    
    # Analysis metadata
    analysis_confidence = Column(Float, nullable=True)
    theme_summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    diary_entry = relationship("DiaryEntry", back_populates="theme_analysis")

class UserProfile(Base):
    """Store user profile and preferences for personalization"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False)
    
    # User preferences
    preferred_booster_types = Column(JSON, nullable=True)  # User's preferred response types
    mood_sensitivity = Column(Float, default=0.5)  # How sensitive to mood changes
    analysis_depth = Column(String(20), default="medium")  # shallow, medium, deep
    
    # Personalization data
    common_themes = Column(JSON, nullable=True)  # User's most common themes
    mood_patterns = Column(JSON, nullable=True)  # User's mood patterns
    trigger_sensitivity = Column(JSON, nullable=True)  # Sensitivity to different triggers
    
    # Engagement metrics
    total_entries = Column(Integer, default=0)
    avg_entry_length = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

class AnalysisSession(Base):
    """Store analysis session data for batch processing"""
    __tablename__ = "analysis_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    session_type = Column(String(50), nullable=False)  # context, theme, full
    
    # Analysis parameters
    analysis_window_days = Column(Integer, default=7)
    include_lda = Column(String(10), default="true")
    include_triggers = Column(String(10), default="true")
    
    # Results
    analysis_results = Column(JSON, nullable=True)
    processing_time = Column(Float, nullable=True)  # Time taken in seconds
    success = Column(String(10), default="true")
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
