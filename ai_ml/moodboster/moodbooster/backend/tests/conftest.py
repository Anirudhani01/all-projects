"""
Pytest configuration and fixtures for MoodBooster tests
"""

import pytest
import asyncio
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.database import get_db, Base
from app.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_moodbooster.db"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create a new session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_diary_entry():
    """Sample diary entry for testing."""
    return {
        "text": "I'm so happy today! Everything is going great!",
        "session_id": "test-session-123"
    }

@pytest.fixture
def sample_mood_analysis():
    """Sample mood analysis result for testing."""
    return {
        "mood": "happy",
        "confidence": 0.85,
        "emotions": {
            "happy": 0.8,
            "sad": 0.1,
            "angry": 0.05,
            "stressed": 0.05,
            "neutral": 0.0
        },
        "keywords": ["happy", "great", "excited"]
    }
