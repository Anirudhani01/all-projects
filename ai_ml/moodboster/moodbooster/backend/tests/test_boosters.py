"""
Tests for booster functionality
"""

import pytest
from app.services.booster_service import get_booster_for_mood

class TestBoosterService:
    """Test class for booster service functionality"""
    
    def test_get_booster_happy(self):
        """Test booster for happy mood"""
        booster = get_booster_for_mood("happy")
        
        assert booster["title"] == "Keep the Joy Going! 🎉"
        assert booster["type"] == "game"
        assert "booster_metadata" in booster
        assert "action" in booster
        assert "content" in booster

    def test_get_booster_sad(self):
        """Test booster for sad mood"""
        booster = get_booster_for_mood("sad")
        
        assert booster["title"] == "Gentle Comfort 💙"
        assert booster["type"] == "story"
        assert "booster_metadata" in booster
        assert "action" in booster
        assert "content" in booster

    def test_get_booster_angry(self):
        """Test booster for angry mood"""
        booster = get_booster_for_mood("angry")
        
        assert booster["title"] == "Release & Relax 🔥"
        assert booster["type"] == "meditation"
        assert "booster_metadata" in booster
        assert "action" in booster
        assert "content" in booster

    def test_get_booster_stressed(self):
        """Test booster for stressed mood"""
        booster = get_booster_for_mood("stressed")
        
        assert booster["title"] == "Find Your Calm 🌸"
        assert booster["type"] == "meditation"
        assert "booster_metadata" in booster
        assert "action" in booster
        assert "content" in booster

    def test_get_booster_neutral(self):
        """Test booster for neutral mood"""
        booster = get_booster_for_mood("neutral")
        
        assert booster["title"] == "Mindful Moment 🌱"
        assert booster["type"] == "activity"
        assert "booster_metadata" in booster
        assert "action" in booster
        assert "content" in booster

    def test_get_booster_invalid(self):
        """Test booster for invalid mood (should return neutral)"""
        booster = get_booster_for_mood("invalid_mood")
        
        assert booster["title"] == "Mindful Moment 🌱"
        assert booster["type"] == "activity"

    def test_booster_structure(self):
        """Test that all boosters have the required structure"""
        moods = ["happy", "sad", "angry", "stressed", "neutral"]
        
        for mood in moods:
            booster = get_booster_for_mood(mood)
            
            # Check required fields
            assert "title" in booster
            assert "type" in booster
            assert "content" in booster
            assert "action" in booster
            assert "booster_metadata" in booster
            
            # Check field types
            assert isinstance(booster["title"], str)
            assert isinstance(booster["type"], str)
            assert isinstance(booster["content"], str)
            assert isinstance(booster["action"], str)
            assert isinstance(booster["booster_metadata"], dict)
            
            # Check that fields are not empty
            assert len(booster["title"]) > 0
            assert len(booster["type"]) > 0
            assert len(booster["content"]) > 0
            assert len(booster["action"]) > 0

    def test_booster_metadata_structure(self):
        """Test that booster metadata has appropriate structure"""
        moods = ["happy", "sad", "angry", "stressed", "neutral"]
        
        for mood in moods:
            booster = get_booster_for_mood(mood)
            metadata = booster["booster_metadata"]
            
            # Metadata should be a dictionary
            assert isinstance(metadata, dict)
            
            # Should have at least one key
            assert len(metadata) > 0

    def test_booster_types(self):
        """Test that booster types are valid"""
        valid_types = ["game", "story", "meditation", "activity", "music", "video"]
        moods = ["happy", "sad", "angry", "stressed", "neutral"]
        
        for mood in moods:
            booster = get_booster_for_mood(mood)
            assert booster["type"] in valid_types, f"Invalid type for {mood}: {booster['type']}"
