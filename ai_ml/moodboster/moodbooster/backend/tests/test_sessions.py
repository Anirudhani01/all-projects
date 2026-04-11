"""
Tests for session functionality
"""

import pytest
from app.services.session_service import (
    create_session, 
    get_session, 
    update_session_activity,
    calculate_session_duration,
    cleanup_old_sessions
)
from app.models.session import Session

class TestSessionService:
    """Test class for session service functionality"""
    
    def test_create_session(self, db_session):
        """Test session creation"""
        session_id = "test-session-123"
        session_data = '{"test": "data"}'
        
        session = create_session(db_session, session_id, session_data)
        
        assert session is not None
        assert session.session_id == session_id
        assert session.session_data == session_data
        assert session.interactions == 0
        assert session.duration == 0

    def test_get_session(self, db_session):
        """Test getting session by ID"""
        session_id = "test-session-456"
        
        # Create a session first
        created_session = create_session(db_session, session_id)
        
        # Retrieve the session
        retrieved_session = get_session(db_session, session_id)
        
        assert retrieved_session is not None
        assert retrieved_session.session_id == session_id
        assert retrieved_session.id == created_session.id

    def test_get_nonexistent_session(self, db_session):
        """Test getting a session that doesn't exist"""
        session_id = "nonexistent-session"
        
        session = get_session(db_session, session_id)
        
        assert session is None

    def test_update_session_activity(self, db_session):
        """Test updating session activity"""
        session_id = "test-session-789"
        
        # Create a session
        session = create_session(db_session, session_id)
        initial_interactions = session.interactions
        
        # Update activity
        updated_session = update_session_activity(db_session, session_id, 5)
        
        assert updated_session is not None
        assert updated_session.interactions == initial_interactions + 5
        assert updated_session.last_activity is not None

    def test_update_nonexistent_session_activity(self, db_session):
        """Test updating activity for a session that doesn't exist"""
        session_id = "nonexistent-session"
        
        updated_session = update_session_activity(db_session, session_id, 5)
        
        assert updated_session is None

    def test_calculate_session_duration(self, db_session):
        """Test calculating session duration"""
        session_id = "test-session-duration"
        
        # Create a session
        session = create_session(db_session, session_id)
        
        # Update activity to set last_activity
        updated_session = update_session_activity(db_session, session_id, 1)
        
        # Calculate duration
        duration = calculate_session_duration(updated_session)
        
        assert duration >= 0
        assert isinstance(duration, int)

    def test_calculate_session_duration_no_activity(self, db_session):
        """Test calculating duration for session with no activity"""
        session_id = "test-session-no-activity"
        
        # Create a session
        session = create_session(db_session, session_id)
        
        # Calculate duration (should be 0 since no activity)
        duration = calculate_session_duration(session)
        
        assert duration == 0

    def test_cleanup_old_sessions(self, db_session):
        """Test cleaning up old sessions"""
        # This test would need to create sessions with old timestamps
        # For now, just test that the function runs without error
        count = cleanup_old_sessions(db_session, days_old=30)
        
        assert isinstance(count, int)
        assert count >= 0

    def test_session_data_handling(self, db_session):
        """Test session data handling"""
        session_id = "test-session-data"
        session_data = '{"mood": "happy", "entries": 3}'
        
        # Create session with data
        session = create_session(db_session, session_id, session_data)
        
        assert session.session_data == session_data
        
        # Update with new data
        new_data = '{"mood": "sad", "entries": 5}'
        session.session_data = new_data
        db_session.commit()
        
        # Retrieve and verify
        retrieved = get_session(db_session, session_id)
        assert retrieved.session_data == new_data

    def test_session_interactions_increment(self, db_session):
        """Test that interactions are properly incremented"""
        session_id = "test-session-interactions"
        
        # Create session
        session = create_session(db_session, session_id)
        initial_interactions = session.interactions
        
        # Update activity multiple times
        for i in range(3):
            update_session_activity(db_session, session_id, 1)
        
        # Retrieve and check
        updated_session = get_session(db_session, session_id)
        assert updated_session.interactions == initial_interactions + 3

    def test_session_creation_without_data(self, db_session):
        """Test creating session without session data"""
        session_id = "test-session-no-data"
        
        session = create_session(db_session, session_id)
        
        assert session is not None
        assert session.session_id == session_id
        assert session.session_data is None
