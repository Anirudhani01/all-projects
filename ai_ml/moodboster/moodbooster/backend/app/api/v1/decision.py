"""
Decision Layer API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.database import get_db
from app.schemas.decision import (
    DecisionResponse, ContentGenerationResponse, ResponseCombination,
    ContentRequest, GeneratedContent
)
from app.schemas.context import EnrichedMoodResponse
from app.services.decision_engine import decide_response_strategy
from app.services.content_generators import generate_content
from app.services.response_combiner import (
    combine_response, create_personalized_intro, 
    create_engagement_prompts, create_follow_up_suggestions
)

router = APIRouter()

@router.post("/decide", response_model=DecisionResponse)
async def make_decision(
    enriched_mood: EnrichedMoodResponse,
    user_preferences: Optional[Dict] = None
):
    """
    Make decision on response strategy based on enriched mood analysis
    """
    try:
        decision = await decide_response_strategy(enriched_mood, user_preferences)
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision making failed: {str(e)}")

@router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_booster_content(
    content_requests: List[ContentRequest],
    background_tasks: BackgroundTasks
):
    """
    Generate content for multiple content types
    """
    try:
        generated_content = []
        total_duration = 0
        generation_start = __import__('time').time()
        
        for request in content_requests:
            try:
                content = await generate_content(
                    content_type=request.content_type,
                    mood=request.mood,
                    context=request.context,
                    themes=request.themes,
                    user_preferences=request.user_preferences
                )
                generated_content.append(content)
                total_duration += content.metadata.get('estimated_duration', 5)
            except Exception as e:
                # Log error but continue with other content
                print(f"Failed to generate {request.content_type}: {e}")
                continue
        
        generation_time = __import__('time').time() - generation_start
        
        return ContentGenerationResponse(
            success=len(generated_content) > 0,
            generated_content=generated_content,
            total_duration=total_duration,
            generation_time=generation_time,
            fallback_used=len(generated_content) < len(content_requests)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.post("/combine", response_model=ResponseCombination)
async def combine_booster_response(
    decision_response: DecisionResponse,
    generated_content: List[GeneratedContent]
):
    """
    Combine generated content into cohesive response
    """
    try:
        combination = await combine_response(decision_response, generated_content)
        return combination
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response combination failed: {str(e)}")

@router.post("/full-pipeline")
async def full_decision_pipeline(
    enriched_mood: EnrichedMoodResponse,
    user_preferences: Optional[Dict] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Complete decision pipeline: decide -> generate -> combine
    """
    try:
        # Step 1: Make decision
        decision = await decide_response_strategy(enriched_mood, user_preferences)
        
        # Step 2: Generate content for selected types
        content_requests = []
        for content_type in decision.selected_content:
            content_requests.append(ContentRequest(
                content_type=content_type.type,
                mood=enriched_mood.mood,
                context=enriched_mood.context.dict() if enriched_mood.context else None,
                themes=enriched_mood.themes.dict() if enriched_mood.themes else None,
                user_preferences=user_preferences
            ))
        
        # Generate content
        content_response = await generate_booster_content(content_requests, background_tasks)
        
        # Step 3: Combine response
        combination = await combine_response(decision, content_response.generated_content)
        
        # Step 4: Create personalized intro
        intro = await create_personalized_intro(decision, enriched_mood.context.dict() if enriched_mood.context else None)
        
        # Step 5: Create engagement prompts
        prompts = await create_engagement_prompts(combination, decision)
        
        # Step 6: Create follow-up suggestions
        suggestions = await create_follow_up_suggestions(combination)
        
        return {
            "decision": decision,
            "content_generation": content_response,
            "combination": combination,
            "personalized_intro": intro,
            "engagement_prompts": prompts,
            "follow_up_suggestions": suggestions,
            "pipeline_success": True,
            "total_processing_time": content_response.generation_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full pipeline failed: {str(e)}")

@router.post("/quick-booster")
async def quick_booster(
    mood: str,
    user_id: str,
    include_context: bool = True,
    include_themes: bool = True,
    db: Session = Depends(get_db)
):
    """
    Quick booster generation without full enriched analysis
    """
    try:
        # Create minimal enriched mood response
        from app.schemas.context import EnrichedMoodResponse
        enriched_mood = EnrichedMoodResponse(
            mood=mood,
            confidence=0.8,
            emotions={mood: 0.8},
            keywords=[],
            context=None,
            themes=None,
            enrichment_score=0.5
        )
        
        # Run full pipeline
        result = await full_decision_pipeline(enriched_mood, None, None)
        
        return {
            "mood": mood,
            "user_id": user_id,
            "booster": result,
            "quick_mode": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick booster failed: {str(e)}")

@router.get("/content-types")
async def get_available_content_types():
    """
    Get list of available content types
    """
    return {
        "content_types": [
            {
                "type": "quote",
                "description": "Inspirational quotes and wisdom",
                "estimated_duration": "2 minutes",
                "interaction_level": "low"
            },
            {
                "type": "story",
                "description": "Short stories and narratives",
                "estimated_duration": "5 minutes",
                "interaction_level": "medium"
            },
            {
                "type": "meditation",
                "description": "Guided meditation and mindfulness",
                "estimated_duration": "10 minutes",
                "interaction_level": "medium"
            },
            {
                "type": "music",
                "description": "Music recommendations and playlists",
                "estimated_duration": "5 minutes",
                "interaction_level": "low"
            },
            {
                "type": "game",
                "description": "Interactive games and puzzles",
                "estimated_duration": "8 minutes",
                "interaction_level": "high"
            },
            {
                "type": "activity",
                "description": "Physical and creative activities",
                "estimated_duration": "15 minutes",
                "interaction_level": "high"
            },
            {
                "type": "breathing",
                "description": "Breathing exercises and techniques",
                "estimated_duration": "5 minutes",
                "interaction_level": "medium"
            }
        ]
    }

@router.get("/strategy-types")
async def get_available_strategies():
    """
    Get list of available response strategies
    """
    return {
        "strategies": [
            {
                "type": "focused",
                "description": "Single focused content type",
                "best_for": "Specific mood needs",
                "duration": "5-10 minutes"
            },
            {
                "type": "balanced",
                "description": "Two complementary content types",
                "best_for": "Moderate mood support",
                "duration": "10-20 minutes"
            },
            {
                "type": "comprehensive",
                "description": "Multiple content types",
                "best_for": "Complex emotional states",
                "duration": "20-30 minutes"
            }
        ],
        "delivery_approaches": [
            {
                "type": "gentle",
                "description": "Soft, supportive approach",
                "best_for": "Sad, vulnerable moods"
            },
            {
                "type": "calming",
                "description": "Relaxing, peaceful approach",
                "best_for": "Angry, stressed moods"
            },
            {
                "type": "energetic",
                "description": "Dynamic, engaging approach",
                "best_for": "Happy, motivated moods"
            },
            {
                "type": "neutral",
                "description": "Balanced, neutral approach",
                "best_for": "Neutral, contemplative moods"
            }
        ]
    }

@router.post("/feedback")
async def process_user_feedback(
    user_id: str,
    response_id: str,
    feedback_data: Dict,
    background_tasks: BackgroundTasks
):
    """
    Process user feedback on generated content
    """
    try:
        # Store feedback in background
        background_tasks.add_task(
            _store_user_feedback,
            user_id=user_id,
            response_id=response_id,
            feedback_data=feedback_data
        )
        
        # Generate follow-up suggestions based on feedback
        suggestions = await create_follow_up_suggestions(
            None,  # Would need actual response combination
            feedback_data
        )
        
        return {
            "message": "Feedback received successfully",
            "follow_up_suggestions": suggestions,
            "feedback_id": f"feedback_{user_id}_{response_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback processing failed: {str(e)}")

@router.get("/analytics/{user_id}")
async def get_decision_analytics(
    user_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get analytics for user's decision patterns
    """
    try:
        # This would query the database for user's decision history
        # For now, return mock data
        return {
            "user_id": user_id,
            "period_days": days,
            "total_decisions": 15,
            "most_common_strategies": [
                {"strategy": "focused", "count": 8, "percentage": 53.3},
                {"strategy": "balanced", "count": 5, "percentage": 33.3},
                {"strategy": "comprehensive", "count": 2, "percentage": 13.3}
            ],
            "most_common_content_types": [
                {"type": "meditation", "count": 12, "percentage": 80.0},
                {"type": "quote", "count": 10, "percentage": 66.7},
                {"type": "story", "count": 7, "percentage": 46.7}
            ],
            "average_engagement_score": 0.75,
            "average_decision_confidence": 0.82,
            "mood_distribution": {
                "sad": 6,
                "stressed": 4,
                "angry": 3,
                "happy": 2,
                "neutral": 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

# Background task functions
async def _store_user_feedback(user_id: str, response_id: str, feedback_data: Dict):
    """Store user feedback in database"""
    try:
        # This would store feedback in the database
        # For now, just log it
        print(f"Storing feedback for user {user_id}, response {response_id}: {feedback_data}")
    except Exception as e:
        print(f"Failed to store feedback: {e}")
