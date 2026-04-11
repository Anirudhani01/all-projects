"""
Context Analysis API endpoints for Middle Layer
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime
from app.database import get_db
from app.services.context_analyzer import analyze_user_context
from app.services.theme_extractor import extract_user_themes
from app.models.context_analysis import ContextAnalysis, ThemeAnalysis, UserProfile
from app.schemas.context import ContextAnalysisResponse, ThemeAnalysisResponse, EnrichedMoodResponse

router = APIRouter()

@router.post("/analyze", response_model=ContextAnalysisResponse)
async def analyze_context(
    user_id: str,
    current_mood: str,
    current_text: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Analyze user context including history, trends, and patterns
    """
    try:
        # Perform context analysis
        context_result = await analyze_user_context(user_id, current_mood, current_text, db)
        
        # Store analysis in background
        background_tasks.add_task(
            _store_context_analysis,
            user_id=user_id,
            diary_entry_id=None,  # Will be set when diary entry is created
            context_result=context_result,
            db=db
        )
        
        return ContextAnalysisResponse(
            user_id=context_result["user_id"],
            current_mood=context_result["current_mood"],
            history_summary=context_result["history_summary"],
            trends=context_result["trends"],
            patterns=context_result["patterns"],
            stability=context_result["stability"],
            context_summary=context_result["context_summary"],
            enrichment_score=context_result["enrichment_score"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context analysis failed: {str(e)}")

@router.post("/themes", response_model=ThemeAnalysisResponse)
async def analyze_themes(
    user_id: str,
    current_text: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Extract themes and triggers from user's diary entries
    """
    try:
        # Perform theme analysis
        theme_result = await extract_user_themes(user_id, current_text, db)
        
        # Store analysis in background
        background_tasks.add_task(
            _store_theme_analysis,
            user_id=user_id,
            diary_entry_id=None,  # Will be set when diary entry is created
            theme_result=theme_result,
            db=db
        )
        
        return ThemeAnalysisResponse(
            user_id=theme_result["user_id"],
            current_text_themes=theme_result["current_text_themes"],
            lda_themes=theme_result["lda_themes"],
            category_themes=theme_result["category_themes"],
            triggers=theme_result["triggers"],
            theme_evolution=theme_result["theme_evolution"],
            theme_summary=theme_result["theme_summary"],
            analysis_confidence=theme_result["analysis_confidence"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Theme analysis failed: {str(e)}")

@router.post("/enriched-mood", response_model=EnrichedMoodResponse)
async def get_enriched_mood_analysis(
    user_id: str,
    current_text: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Get enriched mood analysis combining mood detection, context, and themes
    """
    try:
        # First, analyze mood (using existing service)
        from app.services.mood_analysis import analyze_mood
        mood_result = await analyze_mood(current_text)
        
        # Then analyze context
        context_result = await analyze_user_context(user_id, mood_result.mood, current_text, db)
        
        # Then analyze themes
        theme_result = await extract_user_themes(user_id, current_text, db)
        
        # Store both analyses in background
        background_tasks.add_task(
            _store_enriched_analysis,
            user_id=user_id,
            mood_result=mood_result,
            context_result=context_result,
            theme_result=theme_result,
            db=db
        )
        
        return EnrichedMoodResponse(
            mood=mood_result.mood,
            confidence=mood_result.confidence,
            emotions=mood_result.emotions,
            keywords=mood_result.keywords,
            context=context_result,
            themes=theme_result,
            enrichment_score=context_result["enrichment_score"] + theme_result["analysis_confidence"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enriched mood analysis failed: {str(e)}")

@router.get("/history/{user_id}")
async def get_user_context_history(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get user's context analysis history
    """
    try:
        context_analyses = db.query(ContextAnalysis)\
            .filter(ContextAnalysis.user_id == user_id)\
            .order_by(ContextAnalysis.created_at.desc())\
            .limit(limit)\
            .all()
        
        return {
            "user_id": user_id,
            "analyses": [
                {
                    "id": analysis.id,
                    "mood_trend": analysis.mood_trend,
                    "trend_confidence": analysis.trend_confidence,
                    "mood_stability": analysis.mood_stability,
                    "stability_score": analysis.stability_score,
                    "context_summary": analysis.context_summary,
                    "enrichment_score": analysis.enrichment_score,
                    "created_at": analysis.created_at
                }
                for analysis in context_analyses
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get context history: {str(e)}")

@router.get("/themes/{user_id}")
async def get_user_theme_history(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get user's theme analysis history
    """
    try:
        theme_analyses = db.query(ThemeAnalysis)\
            .filter(ThemeAnalysis.user_id == user_id)\
            .order_by(ThemeAnalysis.created_at.desc())\
            .limit(limit)\
            .all()
        
        return {
            "user_id": user_id,
            "analyses": [
                {
                    "id": analysis.id,
                    "category_themes": analysis.category_themes,
                    "top_categories": analysis.top_categories,
                    "current_triggers": analysis.current_triggers,
                    "historical_triggers": analysis.historical_triggers,
                    "theme_summary": analysis.theme_summary,
                    "analysis_confidence": analysis.analysis_confidence,
                    "created_at": analysis.created_at
                }
                for analysis in theme_analyses
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get theme history: {str(e)}")

@router.get("/profile/{user_id}")
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user profile for personalization
    """
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            # Create default profile
            profile = UserProfile(
                user_id=user_id,
                preferred_booster_types=["story", "meditation"],
                mood_sensitivity=0.5,
                analysis_depth="medium",
                total_entries=0,
                avg_entry_length=0.0,
                engagement_score=0.0,
                created_at=datetime.now()
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        return {
            "user_id": profile.user_id,
            "preferred_booster_types": profile.preferred_booster_types,
            "mood_sensitivity": profile.mood_sensitivity,
            "analysis_depth": profile.analysis_depth,
            "common_themes": profile.common_themes,
            "mood_patterns": profile.mood_patterns,
            "trigger_sensitivity": profile.trigger_sensitivity,
            "total_entries": profile.total_entries,
            "avg_entry_length": profile.avg_entry_length,
            "engagement_score": profile.engagement_score,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

@router.put("/profile/{user_id}")
async def update_user_profile(
    user_id: str,
    profile_data: Dict,
    db: Session = Depends(get_db)
):
    """
    Update user profile for personalization
    """
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Update profile fields
        for field, value in profile_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        profile.updated_at = datetime.now()
        db.commit()
        db.refresh(profile)
        
        return {"message": "Profile updated successfully", "profile_id": profile.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

# Background task functions
async def _store_context_analysis(user_id: str, diary_entry_id: Optional[int], context_result: Dict, db: Session):
    """Store context analysis results in database"""
    try:
        analysis = ContextAnalysis(
            diary_entry_id=diary_entry_id,
            user_id=user_id,
            mood_trend=context_result["trends"].get("trend"),
            trend_confidence=context_result["trends"].get("confidence"),
            mood_stability=context_result["stability"].get("stability_level"),
            stability_score=context_result["stability"].get("stability_score"),
            recurring_moods=context_result["patterns"].get("recurring_moods"),
            day_patterns=context_result["patterns"].get("patterns"),
            mood_sequences=context_result["patterns"].get("patterns"),
            context_summary=context_result["context_summary"],
            enrichment_score=context_result["enrichment_score"],
            created_at=datetime.now()
        )
        
        db.add(analysis)
        db.commit()
        
    except Exception as e:
        print(f"Failed to store context analysis: {e}")

async def _store_theme_analysis(user_id: str, diary_entry_id: Optional[int], theme_result: Dict, db: Session):
    """Store theme analysis results in database"""
    try:
        analysis = ThemeAnalysis(
            diary_entry_id=diary_entry_id,
            user_id=user_id,
            lda_themes=theme_result["lda_themes"],
            lda_confidence=theme_result["lda_themes"].get("confidence"),
            category_themes=theme_result["category_themes"],
            top_categories=list(theme_result["category_themes"].get("categories", {}).keys())[:3],
            current_triggers=theme_result["triggers"].get("current_triggers"),
            historical_triggers=theme_result["triggers"].get("historical_triggers"),
            theme_evolution=theme_result["theme_evolution"],
            new_themes=[e for e in theme_result["theme_evolution"].get("evolution", []) if e["type"] == "new"],
            disappeared_themes=[e for e in theme_result["theme_evolution"].get("evolution", []) if e["type"] == "disappeared"],
            analysis_confidence=theme_result["analysis_confidence"],
            theme_summary=theme_result["theme_summary"],
            created_at=datetime.now()
        )
        
        db.add(analysis)
        db.commit()
        
    except Exception as e:
        print(f"Failed to store theme analysis: {e}")

async def _store_enriched_analysis(user_id: str, mood_result, context_result: Dict, theme_result: Dict, db: Session):
    """Store enriched analysis results"""
    try:
        # Store context analysis
        await _store_context_analysis(user_id, None, context_result, db)
        
        # Store theme analysis
        await _store_theme_analysis(user_id, None, theme_result, db)
        
    except Exception as e:
        print(f"Failed to store enriched analysis: {e}")
