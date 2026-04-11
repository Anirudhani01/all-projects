from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.diary_entry import DiaryEntry
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict

router = APIRouter()

@router.get("/trends/{session_id}")
async def get_mood_trends(
    session_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get mood trends for a session over specified days"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query mood data
        entries = db.query(DiaryEntry).filter(
            DiaryEntry.session_id == session_id,
            DiaryEntry.created_at >= start_date,
            DiaryEntry.created_at <= end_date
        ).order_by(DiaryEntry.created_at).all()
        
        # Process data for trends
        mood_counts = {}
        daily_moods = {}
        
        for entry in entries:
            mood = entry.mood
            date = entry.created_at.date()
            
            # Count moods
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            # Track daily moods
            if date not in daily_moods:
                daily_moods[date] = []
            daily_moods[date].append(mood)
        
        # Calculate most common mood
        most_common_mood = max(mood_counts, key=mood_counts.get) if mood_counts else 'neutral'
        
        # Calculate mood distribution
        total_entries = len(entries)
        mood_distribution = {
            mood: (count / total_entries * 100) if total_entries > 0 else 0
            for mood, count in mood_counts.items()
        }
        
        return {
            'session_id': session_id,
            'period_days': days,
            'total_entries': total_entries,
            'most_common_mood': most_common_mood,
            'mood_distribution': mood_distribution,
            'daily_moods': daily_moods,
            'mood_counts': mood_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting mood trends: {str(e)}")

@router.get("/stats/{session_id}")
async def get_session_stats(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get overall statistics for a session"""
    try:
        # Get all entries for session
        entries = db.query(DiaryEntry).filter(
            DiaryEntry.session_id == session_id
        ).all()
        
        if not entries:
            return {
                'session_id': session_id,
                'total_entries': 0,
                'message': 'No entries found for this session'
            }
        
        # Calculate statistics
        total_entries = len(entries)
        total_words = sum(entry.word_count for entry in entries)
        avg_words = total_words / total_entries if total_entries > 0 else 0
        
        # Mood statistics
        mood_counts = {}
        for entry in entries:
            mood_counts[entry.mood] = mood_counts.get(entry.mood, 0) + 1
        
        # Date range
        dates = [entry.created_at for entry in entries]
        first_entry = min(dates) if dates else None
        last_entry = max(dates) if dates else None
        
        return {
            'session_id': session_id,
            'total_entries': total_entries,
            'total_words': total_words,
            'average_words_per_entry': round(avg_words, 2),
            'mood_counts': mood_counts,
            'first_entry_date': first_entry.isoformat() if first_entry else None,
            'last_entry_date': last_entry.isoformat() if last_entry else None,
            'days_active': (last_entry - first_entry).days + 1 if first_entry and last_entry else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session stats: {str(e)}")
