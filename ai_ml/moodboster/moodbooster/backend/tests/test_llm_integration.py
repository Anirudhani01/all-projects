"""
Tests for LLM integration functionality
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.services.llm_mood_analyzer import LLMMoodAnalyzer, analyze_mood_with_llm

class TestLLMMoodAnalyzer:
    """Test class for LLM mood analyzer functionality"""
    
    def test_llm_analyzer_initialization(self):
        """Test LLM analyzer initialization"""
        analyzer = LLMMoodAnalyzer()
        
        assert analyzer is not None
        # Should initialize without errors even if services are not available
        assert hasattr(analyzer, 'gemini_available')
        assert hasattr(analyzer, 'ollama_available')

    @pytest.mark.asyncio
    async def test_analyze_mood_empty_text(self):
        """Test mood analysis with empty text"""
        analyzer = LLMMoodAnalyzer()
        result = await analyzer.analyze_mood("")
        
        assert result.mood == "neutral"
        assert result.confidence == 0.5
        assert result.emotions == {}
        assert result.keywords == []

    @pytest.mark.asyncio
    async def test_analyze_mood_whitespace_text(self):
        """Test mood analysis with whitespace-only text"""
        analyzer = LLMMoodAnalyzer()
        result = await analyzer.analyze_mood("   \n\t   ")
        
        assert result.mood == "neutral"
        assert result.confidence == 0.5

    @pytest.mark.asyncio
    async def test_analyze_mood_fallback_to_keyword(self):
        """Test that analyzer falls back to keyword analysis when LLMs fail"""
        analyzer = LLMMoodAnalyzer()
        
        # Mock both LLM services to fail
        with patch.object(analyzer, 'gemini_available', False), \
             patch.object(analyzer, 'ollama_available', False):
            
            result = await analyzer.analyze_mood("I'm so happy today!")
            
            # Should still return a valid result
            assert result is not None
            assert result.mood in ["happy", "sad", "angry", "stressed", "neutral"]
            assert 0.5 <= result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_gemini_analysis_success(self):
        """Test successful Gemini analysis"""
        analyzer = LLMMoodAnalyzer()
        
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "mood": "happy",
            "confidence": 0.9,
            "emotions": {
                "happy": 0.9,
                "sad": 0.05,
                "angry": 0.02,
                "stressed": 0.02,
                "neutral": 0.01
            },
            "keywords": ["happy", "excited", "great"],
            "reasoning": "The text contains positive emotional indicators"
        }
        '''
        
        with patch.object(analyzer, 'gemini_available', True), \
             patch('google.generativeai.GenerativeModel') as mock_model:
            
            mock_model.return_value.generate_content.return_value = mock_response
            
            result = await analyzer._analyze_with_gemini("I'm so happy today!")
            
            assert result is not None
            assert result.mood == "happy"
            assert result.confidence == 0.9
            assert result.emotions["happy"] == 0.9
            assert "happy" in result.keywords

    @pytest.mark.asyncio
    async def test_gemini_analysis_failure(self):
        """Test Gemini analysis failure handling"""
        analyzer = LLMMoodAnalyzer()
        
        with patch.object(analyzer, 'gemini_available', True), \
             patch('google.generativeai.GenerativeModel') as mock_model:
            
            mock_model.side_effect = Exception("API Error")
            
            result = await analyzer._analyze_with_gemini("I'm so happy today!")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_ollama_analysis_success(self):
        """Test successful Ollama analysis"""
        analyzer = LLMMoodAnalyzer()
        
        # Mock Ollama response
        mock_response = {
            'response': '''
            {
                "mood": "sad",
                "confidence": 0.85,
                "emotions": {
                    "happy": 0.1,
                    "sad": 0.85,
                    "angry": 0.03,
                    "stressed": 0.02,
                    "neutral": 0.0
                },
                "keywords": ["sad", "down", "depressed"],
                "reasoning": "The text expresses sadness and low mood"
            }
            '''
        }
        
        with patch.object(analyzer, 'ollama_available', True), \
             patch('ollama.generate', return_value=mock_response) as mock_ollama:
            
            result = await analyzer._analyze_with_ollama("I'm feeling really down today.")
            
            assert result is not None
            assert result.mood == "sad"
            assert result.confidence == 0.85
            assert result.emotions["sad"] == 0.85
            assert "sad" in result.keywords

    @pytest.mark.asyncio
    async def test_ollama_analysis_failure(self):
        """Test Ollama analysis failure handling"""
        analyzer = LLMMoodAnalyzer()
        
        with patch.object(analyzer, 'ollama_available', True), \
             patch('ollama.generate', side_effect=Exception("Connection Error")):
            
            result = await analyzer._analyze_with_ollama("I'm so happy today!")
            
            assert result is None

    def test_parse_llm_response_valid_json(self):
        """Test parsing valid LLM response"""
        analyzer = LLMMoodAnalyzer()
        
        response = '''
        {
            "mood": "angry",
            "confidence": 0.8,
            "emotions": {
                "happy": 0.05,
                "sad": 0.1,
                "angry": 0.8,
                "stressed": 0.05,
                "neutral": 0.0
            },
            "keywords": ["angry", "furious", "mad"],
            "reasoning": "The text shows clear anger indicators"
        }
        '''
        
        result = analyzer._parse_llm_response(response)
        
        assert result is not None
        assert result.mood == "angry"
        assert result.confidence == 0.8
        assert result.emotions["angry"] == 0.8
        assert "angry" in result.keywords

    def test_parse_llm_response_invalid_json(self):
        """Test parsing invalid LLM response"""
        analyzer = LLMMoodAnalyzer()
        
        response = "This is not valid JSON"
        
        result = analyzer._parse_llm_response(response)
        
        assert result is None

    def test_parse_llm_response_missing_fields(self):
        """Test parsing LLM response with missing required fields"""
        analyzer = LLMMoodAnalyzer()
        
        response = '''
        {
            "mood": "happy",
            "confidence": 0.8
        }
        '''
        
        result = analyzer._parse_llm_response(response)
        
        assert result is None

    def test_parse_llm_response_invalid_mood(self):
        """Test parsing LLM response with invalid mood"""
        analyzer = LLMMoodAnalyzer()
        
        response = '''
        {
            "mood": "invalid_mood",
            "confidence": 0.8,
            "emotions": {
                "happy": 0.8,
                "sad": 0.1,
                "angry": 0.05,
                "stressed": 0.05,
                "neutral": 0.0
            },
            "keywords": ["happy", "great"]
        }
        '''
        
        result = analyzer._parse_llm_response(response)
        
        assert result is not None
        assert result.mood == "neutral"  # Should default to neutral

    def test_parse_llm_response_invalid_confidence(self):
        """Test parsing LLM response with invalid confidence"""
        analyzer = LLMMoodAnalyzer()
        
        response = '''
        {
            "mood": "happy",
            "confidence": 1.5,
            "emotions": {
                "happy": 0.8,
                "sad": 0.1,
                "angry": 0.05,
                "stressed": 0.05,
                "neutral": 0.0
            },
            "keywords": ["happy", "great"]
        }
        '''
        
        result = analyzer._parse_llm_response(response)
        
        assert result is not None
        assert result.confidence == 1.0  # Should be clamped to 1.0

    def test_create_mood_analysis_prompt(self):
        """Test prompt creation for mood analysis"""
        analyzer = LLMMoodAnalyzer()
        
        text = "I'm so excited about my new job!"
        prompt = analyzer._create_mood_analysis_prompt(text)
        
        assert isinstance(prompt, str)
        assert text in prompt
        assert "mood" in prompt
        assert "confidence" in prompt
        assert "emotions" in prompt
        assert "keywords" in prompt
        assert "JSON" in prompt

    @pytest.mark.asyncio
    async def test_analyze_mood_with_llm_public_function(self):
        """Test the public analyze_mood_with_llm function"""
        text = "I'm feeling great today!"
        
        result = await analyze_mood_with_llm(text)
        
        assert result is not None
        assert result.mood in ["happy", "sad", "angry", "stressed", "neutral"]
        assert 0.5 <= result.confidence <= 1.0
        assert isinstance(result.emotions, dict)
        assert isinstance(result.keywords, list)

    @pytest.mark.asyncio
    async def test_llm_analyzer_consistency(self):
        """Test that LLM analyzer produces consistent results"""
        analyzer = LLMMoodAnalyzer()
        text = "I'm so happy today! Everything is going great!"
        
        # Run analysis multiple times
        results = []
        for _ in range(3):
            result = await analyzer.analyze_mood(text)
            results.append((result.mood, result.confidence))
        
        # All results should be the same
        moods = [r[0] for r in results]
        confidences = [r[1] for r in results]
        
        assert len(set(moods)) == 1, f"Inconsistent moods: {moods}"
        assert all(abs(c - confidences[0]) < 0.01 for c in confidences), f"Inconsistent confidences: {confidences}"

    @pytest.mark.asyncio
    async def test_llm_analyzer_edge_cases(self):
        """Test LLM analyzer with edge cases"""
        analyzer = LLMMoodAnalyzer()
        
        test_cases = [
            ("", "neutral"),
            ("   ", "neutral"),
            ("I'm not happy at all", "neutral"),  # Negation
            ("I'm very very very happy!", "happy"),  # Intensifiers
            ("I'm extremely sad and depressed", "sad"),  # Multiple emotions
        ]
        
        for text, expected_mood in test_cases:
            result = await analyzer.analyze_mood(text)
            assert result.mood == expected_mood, f"Failed for text: '{text}'"
            assert 0.5 <= result.confidence <= 1.0
