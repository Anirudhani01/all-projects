from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.booster import BoosterResponse
from app.services.booster_service import get_booster_for_mood

router = APIRouter()

@router.get("/{mood_type}")
async def get_booster_by_mood(mood_type: str):
    """Get booster content for a specific mood type"""
    valid_moods = ['happy', 'sad', 'angry', 'stressed', 'neutral']
    
    if mood_type not in valid_moods:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid mood type. Must be one of: {', '.join(valid_moods)}"
        )
    
    try:
        booster = get_booster_for_mood(mood_type)
        return booster
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting booster: {str(e)}")

@router.get("/random/{mood_type}")
async def get_random_booster(mood_type: str):
    """Get a random booster for a specific mood type"""
    # This would typically fetch from database with random selection
    # For now, return the same booster as the regular endpoint
    return await get_booster_by_mood(mood_type)
