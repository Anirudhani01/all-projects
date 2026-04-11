# Session management service

from sqlalchemy.orm import Session
from app.models.session import Session as SessionModel
from app.utils.helpers import get_current_timestamp
from datetime import datetime, timedelta
from typing import Optional

def create_session(db: Session, session_id: str, session_data: Optional[str] = None) -> SessionModel:
    """Create a new session"""
    db_session = SessionModel(
        session_id=session_id,
        session_data=session_data,
        created_at=get_current_timestamp()
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: str) -> Optional[SessionModel]:
    """Get session by session_id"""
    return db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

def update_session_activity(db: Session, session_id: str, interactions: int = 1) -> Optional[SessionModel]:
    """Update session activity"""
    session = get_session(db, session_id)
    if session:
        session.last_activity = get_current_timestamp()
        session.interactions += interactions
        db.commit()
        db.refresh(session)
    return session

def calculate_session_duration(session: SessionModel) -> int:
    """Calculate session duration in minutes"""
    if not session.last_activity:
        return 0
    
    duration = session.last_activity - session.created_at
    return int(duration.total_seconds() / 60)

def cleanup_old_sessions(db: Session, days_old: int = 30) -> int:
    """Clean up sessions older than specified days"""
    cutoff_date = get_current_timestamp() - timedelta(days=days_old)
    old_sessions = db.query(SessionModel).filter(
        SessionModel.created_at < cutoff_date
    ).all()
    
    count = len(old_sessions)
    for session in old_sessions:
        db.delete(session)
    
    db.commit()
    return count
