from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Optional
from app.database import get_db
from app.schemas.mood import MoodResponse
from app.schemas.context import EnrichedMoodResponse
from app.services.mood_analysis import analyze_mood
from app.services.enhanced_mood_analysis import analyze_enriched_mood, get_mood_insights
from app.services.complete_mood_analysis import analyze_complete_mood, get_quick_booster

router = APIRouter()

@router.post("/analyze", response_model=MoodResponse)
async def analyze_text_mood(text: str):
    """Analyze mood from text input (basic analysis)"""
    try:
        mood_result = await analyze_mood(text)
        
        # Generate suggestions based on mood
        suggestions = {
            'happy': [
                "Share your joy with others",
                "Document this positive moment",
                "Try a fun activity to maintain the good mood"
            ],
            'sad': [
                "Consider talking to someone you trust",
                "Try some gentle self-care activities",
                "Remember that this feeling is temporary"
            ],
            'angry': [
                "Take some deep breaths",
                "Try physical exercise to release tension",
                "Consider what's really bothering you"
            ],
            'stressed': [
                "Take a break and do something relaxing",
                "Try organizing your tasks by priority",
                "Practice mindfulness or meditation"
            ],
            'neutral': [
                "Reflect on what you're grateful for",
                "Try a new activity or hobby",
                "Connect with nature or go for a walk"
            ]
        }
        
        return MoodResponse(
            mood=mood_result.mood,
            confidence=mood_result.confidence,
            analysis=f"Based on your text, I can sense you're feeling {mood_result.mood}.",
            suggestions=suggestions.get(mood_result.mood, [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing mood: {str(e)}")

@router.post("/analyze/enriched", response_model=EnrichedMoodResponse)
async def analyze_text_mood_enriched(
    user_id: str,
    text: str,
    include_context: bool = True,
    include_themes: bool = True,
    db: Session = Depends(get_db)
):
    """Analyze mood with enriched context and theme analysis"""
    try:
        enriched_result = await analyze_enriched_mood(
            user_id, text, db, include_context, include_themes
        )
        return enriched_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in enriched mood analysis: {str(e)}")

@router.post("/insights")
async def get_mood_insights_endpoint(
    user_id: str,
    text: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive mood insights including trends and patterns"""
    try:
        insights = await get_mood_insights(user_id, text, db)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting mood insights: {str(e)}")

@router.post("/complete-analysis")
async def complete_mood_analysis_endpoint(
    user_id: str,
    text: str,
    include_context: bool = True,
    include_themes: bool = True,
    user_preferences: Optional[Dict] = None,
    db: Session = Depends(get_db)
):
    """Complete mood analysis with all layers (Input + Middle + Decision + Output)"""
    try:
        analysis = await analyze_complete_mood(
            user_id, text, db, user_preferences, include_context, include_themes
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complete analysis failed: {str(e)}")

@router.post("/quick-booster")
async def quick_booster_endpoint(
    mood: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Quick booster without full analysis"""
    try:
        booster = await get_quick_booster(mood, user_id, db)
        return booster
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick booster failed: {str(e)}")
