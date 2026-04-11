"""
Tests for mood analysis functionality
"""

import pytest
import asyncio
from app.services.mood_analysis import analyze_mood, analyze_mood_sync
from app.services.llm_mood_analyzer import analyze_mood_with_llm

class TestMoodAnalysis:
    """Test class for mood analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_analyze_mood_happy(self):
        """Test mood analysis for happy text"""
        text = "I'm so happy today! Everything is going great and I feel amazing!"
        result = await analyze_mood(text)
        
        assert result.mood == "happy"
        assert result.confidence > 0.5
        assert "happy" in result.keywords

    @pytest.mark.asyncio
    async def test_analyze_mood_sad(self):
        """Test mood analysis for sad text"""
        text = "I'm feeling really down and sad today. Nothing seems to be going right."
        result = await analyze_mood(text)
        
        assert result.mood == "sad"
        assert result.confidence > 0.5
        assert "sad" in result.keywords

    @pytest.mark.asyncio
    async def test_analyze_mood_angry(self):
        """Test mood analysis for angry text"""
        text = "I'm so angry and frustrated! This is making me furious!"
        result = await analyze_mood(text)
        
        assert result.mood == "angry"
        assert result.confidence > 0.5
        assert "angry" in result.keywords

    @pytest.mark.asyncio
    async def test_analyze_mood_stressed(self):
        """Test mood analysis for stressed text"""
        text = "I'm feeling so stressed and overwhelmed with all this work!"
        result = await analyze_mood(text)
        
        assert result.mood == "stressed"
        assert result.confidence > 0.5
        assert "stressed" in result.keywords

    @pytest.mark.asyncio
    async def test_analyze_mood_neutral(self):
        """Test mood analysis for neutral text"""
        text = "Today was just a regular day. Nothing special happened."
        result = await analyze_mood(text)
        
        assert result.mood == "neutral"
        assert result.confidence >= 0.5

    @pytest.mark.asyncio
    async def test_analyze_mood_empty(self):
        """Test mood analysis for empty text"""
        text = ""
        result = await analyze_mood(text)
        
        assert result.mood == "neutral"
        assert result.confidence == 0.5

    def test_analyze_mood_sync_wrapper(self):
        """Test synchronous wrapper for mood analysis"""
        text = "I'm so happy today!"
        result = analyze_mood_sync(text)
        
        assert result.mood == "happy"
        assert result.confidence > 0.5

    @pytest.mark.asyncio
    async def test_llm_mood_analysis_fallback(self):
        """Test LLM mood analysis with fallback"""
        text = "I'm extremely excited about my new job!"
        
        # This will test the full LLM integration with fallback
        result = await analyze_mood_with_llm(text)
        
        # Should return a valid result even if LLMs are not available
        assert result is not None
        assert result.mood in ["happy", "sad", "angry", "stressed", "neutral"]
        assert 0.5 <= result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_mood_analysis_consistency(self):
        """Test that mood analysis is consistent for the same input"""
        text = "I'm so happy today! Everything is going great!"
        
        # Run analysis multiple times
        results = []
        for _ in range(3):
            result = await analyze_mood(text)
            results.append((result.mood, result.confidence))
        
        # All results should be the same
        moods = [r[0] for r in results]
        confidences = [r[1] for r in results]
        
        assert len(set(moods)) == 1, f"Inconsistent moods: {moods}"
        assert all(abs(c - confidences[0]) < 0.01 for c in confidences), f"Inconsistent confidences: {confidences}"

    @pytest.mark.asyncio
    async def test_mood_analysis_edge_cases(self):
        """Test mood analysis with edge cases"""
        test_cases = [
            ("", "neutral"),
            ("   ", "neutral"),
            ("I'm not happy at all", "neutral"),  # Negation
            ("I'm very very very happy!", "happy"),  # Intensifiers
            ("I'm extremely sad and depressed", "sad"),  # Multiple emotions
        ]
        
        for text, expected_mood in test_cases:
            result = await analyze_mood(text)
            assert result.mood == expected_mood, f"Failed for text: '{text}'"
            assert 0.5 <= result.confidence <= 1.0
