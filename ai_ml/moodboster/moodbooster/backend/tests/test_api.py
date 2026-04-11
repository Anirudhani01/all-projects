"""
Tests for API endpoints
"""

import pytest
import json
from fastapi.testclient import TestClient

class TestDiaryAPI:
    """Test class for diary API endpoints"""
    
    def test_create_diary_entry(self, client, sample_diary_entry):
        """Test creating a diary entry"""
        response = client.post("/api/v1/diary/entry", json=sample_diary_entry)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert "text" in data
        assert "mood" in data
        assert "confidence" in data
        assert "word_count" in data
        assert "session_id" in data
        assert "created_at" in data
        
        # Check values
        assert data["text"] == sample_diary_entry["text"]
        assert data["session_id"] == sample_diary_entry["session_id"]
        assert data["mood"] in ["happy", "sad", "angry", "stressed", "neutral"]
        assert 0.5 <= data["confidence"] <= 1.0
        assert data["word_count"] > 0

    def test_create_diary_entry_without_session_id(self, client):
        """Test creating a diary entry without session_id (should generate one)"""
        entry_data = {
            "text": "I'm feeling great today!"
        }
        
        response = client.post("/api/v1/diary/entry", json=entry_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert data["session_id"] is not None
        assert len(data["session_id"]) > 0

    def test_create_diary_entry_empty_text(self, client):
        """Test creating a diary entry with empty text"""
        entry_data = {
            "text": "",
            "session_id": "test-session"
        }
        
        response = client.post("/api/v1/diary/entry", json=entry_data)
        
        # Should return 422 (validation error) or handle gracefully
        assert response.status_code in [200, 422]

    def test_create_diary_entry_missing_text(self, client):
        """Test creating a diary entry without text field"""
        entry_data = {
            "session_id": "test-session"
        }
        
        response = client.post("/api/v1/diary/entry", json=entry_data)
        
        assert response.status_code == 422  # Validation error

    def test_get_diary_entries(self, client, db_session):
        """Test getting diary entries for a session"""
        session_id = "test-session-entries"
        
        # Create some test entries
        entries_data = [
            {"text": "I'm happy today!", "session_id": session_id},
            {"text": "I'm sad today.", "session_id": session_id},
            {"text": "I'm angry today!", "session_id": session_id}
        ]
        
        # Create entries
        for entry_data in entries_data:
            response = client.post("/api/v1/diary/entry", json=entry_data)
            assert response.status_code == 200
        
        # Get entries
        response = client.get(f"/api/v1/diary/entries/{session_id}")
        
        assert response.status_code == 200
        entries = response.json()
        
        assert len(entries) == 3
        assert all(entry["session_id"] == session_id for entry in entries)

    def test_get_diary_entries_empty_session(self, client):
        """Test getting diary entries for a session with no entries"""
        session_id = "empty-session"
        
        response = client.get(f"/api/v1/diary/entries/{session_id}")
        
        assert response.status_code == 200
        entries = response.json()
        
        assert len(entries) == 0

    def test_get_diary_entry_by_id(self, client, sample_diary_entry):
        """Test getting a specific diary entry by ID"""
        # Create an entry
        create_response = client.post("/api/v1/diary/entry", json=sample_diary_entry)
        assert create_response.status_code == 200
        
        entry_id = create_response.json()["id"]
        
        # Get the entry
        response = client.get(f"/api/v1/diary/entry/{entry_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == entry_id
        assert data["text"] == sample_diary_entry["text"]

    def test_get_nonexistent_diary_entry(self, client):
        """Test getting a diary entry that doesn't exist"""
        entry_id = 99999
        
        response = client.get(f"/api/v1/diary/entry/{entry_id}")
        
        assert response.status_code == 404

class TestMoodAPI:
    """Test class for mood API endpoints"""
    
    def test_analyze_mood_endpoint(self, client):
        """Test the mood analysis endpoint"""
        text = "I'm so happy today! Everything is going great!"
        
        response = client.post("/api/v1/mood/analyze", json={"text": text})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "mood" in data
        assert "confidence" in data
        assert "emotions" in data
        assert "keywords" in data
        
        assert data["mood"] in ["happy", "sad", "angry", "stressed", "neutral"]
        assert 0.5 <= data["confidence"] <= 1.0
        assert isinstance(data["emotions"], dict)
        assert isinstance(data["keywords"], list)

    def test_analyze_mood_empty_text(self, client):
        """Test mood analysis with empty text"""
        response = client.post("/api/v1/mood/analyze", json={"text": ""})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["mood"] == "neutral"
        assert data["confidence"] == 0.5

class TestBoosterAPI:
    """Test class for booster API endpoints"""
    
    def test_get_booster_for_mood(self, client):
        """Test getting booster for a specific mood"""
        moods = ["happy", "sad", "angry", "stressed", "neutral"]
        
        for mood in moods:
            response = client.get(f"/api/v1/booster/{mood}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "title" in data
            assert "type" in data
            assert "content" in data
            assert "action" in data
            assert "booster_metadata" in data

    def test_get_booster_invalid_mood(self, client):
        """Test getting booster for invalid mood"""
        response = client.get("/api/v1/booster/invalid_mood")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return neutral booster
        assert "title" in data
        assert "type" in data

class TestHealthAPI:
    """Test class for health check endpoint"""
    
    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "message" in data
        assert data["status"] == "healthy"

class TestRootAPI:
    """Test class for root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Welcome to MoodBooster API" in data["message"]
