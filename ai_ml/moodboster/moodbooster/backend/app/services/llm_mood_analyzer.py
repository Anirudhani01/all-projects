"""
LLM-based mood analysis service with Gemini API and Ollama fallback
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from app.schemas.mood import MoodAnalysis
from app.config import settings
import asyncio
import httpx

logger = logging.getLogger(__name__)

class LLMMoodAnalyzer:
    """
    Advanced mood analysis using LLMs with fallback system:
    1. Gemini API (Primary)
    2. Local Ollama phi3:mini (Secondary)
    3. Keyword-based analysis (Fallback)
    """
    
    def __init__(self):
        self.gemini_available = False
        self.ollama_available = False
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize LLM services"""
        # Check Gemini availability
        if settings.gemini_api_key and settings.use_gemini:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_available = True
                logger.info("✅ Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"❌ Gemini API initialization failed: {e}")
                self.gemini_available = False
        
        # Check Ollama availability
        if settings.use_ollama:
            try:
                import ollama
                # Test connection
                ollama.list()
                self.ollama_available = True
                logger.info("✅ Ollama initialized successfully")
            except Exception as e:
                logger.warning(f"❌ Ollama initialization failed: {e}")
                self.ollama_available = False
    
    async def analyze_mood(self, text: str) -> MoodAnalysis:
        """
        Analyze mood using LLM with fallback system
        """
        if not text or not text.strip():
            return MoodAnalysis(mood='neutral', confidence=0.5, emotions={}, keywords=[])
        
        # Try Gemini first
        if self.gemini_available:
            try:
                result = await self._analyze_with_gemini(text)
                if result:
                    logger.info(f"✅ Mood analyzed with Gemini: {result.mood}")
                    return result
            except Exception as e:
                logger.warning(f"❌ Gemini analysis failed: {e}")
        
        # Try Ollama as fallback
        if self.ollama_available:
            try:
                result = await self._analyze_with_ollama(text)
                if result:
                    logger.info(f"✅ Mood analyzed with Ollama: {result.mood}")
                    return result
            except Exception as e:
                logger.warning(f"❌ Ollama analysis failed: {e}")
        
        # Fallback to keyword-based analysis
        if settings.use_keyword_fallback:
            logger.info("🔄 Falling back to keyword-based analysis")
            from app.services.mood_analysis import analyze_mood as keyword_analyze
            return keyword_analyze(text)
        
        # Default fallback
        return MoodAnalysis(mood='neutral', confidence=0.5, emotions={}, keywords=[])
    
    async def _analyze_with_gemini(self, text: str) -> Optional[MoodAnalysis]:
        """Analyze mood using Gemini API"""
        try:
            import google.generativeai as genai
            
            # Configure the model
            model = genai.GenerativeModel(settings.gemini_model)
            
            # Create the prompt
            prompt = self._create_mood_analysis_prompt(text)
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content, 
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=500,
                )
            )
            
            # Parse the response
            return self._parse_llm_response(response.text)
            
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            return None
    
    async def _analyze_with_ollama(self, text: str) -> Optional[MoodAnalysis]:
        """Analyze mood using local Ollama phi3:mini"""
        try:
            import ollama
            
            # Create the prompt
            prompt = self._create_mood_analysis_prompt(text)
            
            # Generate response
            response = await asyncio.to_thread(
                ollama.generate,
                model=settings.ollama_model,
                prompt=prompt,
                options={
                    'temperature': 0.1,
                    'top_p': 0.9,
                    'max_tokens': 500
                }
            )
            
            # Parse the response
            return self._parse_llm_response(response['response'])
            
        except Exception as e:
            logger.error(f"Ollama analysis error: {e}")
            return None
    
    def _create_mood_analysis_prompt(self, text: str) -> str:
        """Create a structured prompt for mood analysis"""
        return f"""
You are an expert emotional intelligence analyst. Analyze the following text and determine the primary mood and emotional state.

Text: "{text}"

Please analyze this text and respond with a JSON object containing:
1. mood: The primary mood (happy, sad, angry, stressed, neutral)
2. confidence: A confidence score between 0.5 and 1.0
3. emotions: A dictionary with scores for each mood category (happy, sad, angry, stressed, neutral)
4. keywords: A list of key emotional words/phrases that influenced the analysis
5. reasoning: A brief explanation of why this mood was detected

Consider:
- Explicit emotional words and phrases
- Implicit emotional indicators
- Context and tone
- Intensity and modifiers
- Negation and contradiction
- Overall sentiment patterns

Respond ONLY with valid JSON in this exact format:
{{
    "mood": "happy",
    "confidence": 0.85,
    "emotions": {{
        "happy": 0.8,
        "sad": 0.1,
        "angry": 0.05,
        "stressed": 0.05,
        "neutral": 0.0
    }},
    "keywords": ["happy", "excited", "great"],
    "reasoning": "The text contains positive emotional indicators and celebratory language"
}}
"""
    
    def _parse_llm_response(self, response: str) -> Optional[MoodAnalysis]:
        """Parse LLM response and create MoodAnalysis object"""
        try:
            # Clean the response
            response = response.strip()
            
            # Find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON found in LLM response")
                return None
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['mood', 'confidence', 'emotions', 'keywords']
            if not all(field in data for field in required_fields):
                logger.warning("Missing required fields in LLM response")
                return None
            
            # Validate mood
            valid_moods = ['happy', 'sad', 'angry', 'stressed', 'neutral']
            if data['mood'] not in valid_moods:
                logger.warning(f"Invalid mood: {data['mood']}")
                data['mood'] = 'neutral'
            
            # Validate confidence
            confidence = float(data['confidence'])
            confidence = max(0.5, min(1.0, confidence))
            
            # Validate emotions dict
            emotions = data.get('emotions', {})
            for mood in valid_moods:
                if mood not in emotions:
                    emotions[mood] = 0.0
                else:
                    emotions[mood] = float(emotions[mood])
            
            # Validate keywords
            keywords = data.get('keywords', [])
            if not isinstance(keywords, list):
                keywords = []
            
            return MoodAnalysis(
                mood=data['mood'],
                confidence=confidence,
                emotions=emotions,
                keywords=keywords
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"Response parsing error: {e}")
            return None

# Global LLM analyzer instance
_llm_analyzer = LLMMoodAnalyzer()

async def analyze_mood_with_llm(text: str) -> MoodAnalysis:
    """Public function for LLM-based mood analysis"""
    return await _llm_analyzer.analyze_mood(text)
