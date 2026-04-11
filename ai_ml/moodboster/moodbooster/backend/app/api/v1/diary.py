from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.diary import DiaryEntryCreate, DiaryEntryResponse
from app.schemas.mood import MoodResponse
from app.models.diary_entry import DiaryEntry
from app.services.mood_analysis import analyze_mood
from app.services.booster_service import get_booster_for_mood
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/entry", response_model=DiaryEntryResponse)
async def create_diary_entry(
    entry: DiaryEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new diary entry and analyze mood"""
    try:
        # Analyze mood using LLM with fallback
        mood_result = await analyze_mood(entry.text)
        
        # Generate session ID if not provided
        session_id = entry.session_id or str(uuid.uuid4())
        
        # Save entry
        db_entry = DiaryEntry(
            text=entry.text,
            mood=mood_result.mood,
            confidence=mood_result.confidence,
            word_count=len(entry.text.split()),
            session_id=session_id,
            created_at=datetime.utcnow()
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        return DiaryEntryResponse(
            id=db_entry.id,
            text=db_entry.text,
            mood=db_entry.mood,
            confidence=db_entry.confidence,
            word_count=db_entry.word_count,
            session_id=db_entry.session_id,
            created_at=db_entry.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating diary entry: {str(e)}")

@router.get("/entries/{session_id}")
async def get_diary_entries(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get all diary entries for a session"""
    entries = db.query(DiaryEntry).filter(
        DiaryEntry.session_id == session_id
    ).order_by(DiaryEntry.created_at.desc()).all()
    
    return entries

@router.get("/entry/{entry_id}")
async def get_diary_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific diary entry by ID"""
    entry = db.query(DiaryEntry).filter(DiaryEntry.id == entry_id).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    return entry
