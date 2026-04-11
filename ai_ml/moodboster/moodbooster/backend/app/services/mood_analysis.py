from app.schemas.mood import MoodAnalysis
import re
import math
from typing import Dict, List, Tuple
import hashlib
import asyncio
import logging

logger = logging.getLogger(__name__)

class MoodAnalyzer:
    """
    Advanced mood analysis using multiple techniques:
    1. Sentiment analysis with weighted keywords
    2. Context-aware emotion detection
    3. Intensity scoring
    4. Consistency validation
    """
    
    def __init__(self):
        # Enhanced mood keywords with weights and context
        self.mood_patterns = {
            'happy': {
                'keywords': {
                    'explicit': ['happy', 'joy', 'joyful', 'cheerful', 'delighted', 'ecstatic', 'elated', 'thrilled', 'excited', 'pleased', 'content', 'satisfied'],
                    'implicit': ['great', 'wonderful', 'amazing', 'fantastic', 'awesome', 'brilliant', 'excellent', 'perfect', 'excited', 'thrilled', 'delighted'],
                    'actions': ['smile', 'laugh', 'laughing', 'celebrate', 'dance', 'sing', 'cheer'],
                    'achievements': ['success', 'win', 'achievement', 'accomplish', 'proud', 'victory', 'triumph'],
                    'gratitude': ['grateful', 'blessed', 'lucky', 'thankful', 'appreciate', 'love', 'loved']
                },
                'weights': {'explicit': 3, 'implicit': 2, 'actions': 2, 'achievements': 2, 'gratitude': 2},
                'intensity_modifiers': ['very', 'extremely', 'incredibly', 'absolutely', 'completely', 'totally']
            },
            'sad': {
                'keywords': {
                    'explicit': ['sad', 'depressed', 'down', 'upset', 'miserable', 'unhappy', 'gloomy', 'melancholy'],
                    'emotional': ['cry', 'crying', 'tears', 'hurt', 'pain', 'sorrow', 'grief', 'heartbroken'],
                    'loneliness': ['lonely', 'alone', 'isolated', 'empty', 'abandoned', 'rejected'],
                    'hopelessness': ['hopeless', 'despair', 'devastated', 'broken', 'defeated', 'lost'],
                    'disappointment': ['disappointed', 'let down', 'betrayed', 'crushed', 'shattered']
                },
                'weights': {'explicit': 3, 'emotional': 2.5, 'loneliness': 2, 'hopelessness': 2.5, 'disappointment': 2},
                'intensity_modifiers': ['very', 'extremely', 'incredibly', 'completely', 'totally', 'deeply']
            },
            'angry': {
                'keywords': {
                    'explicit': ['angry', 'mad', 'furious', 'rage', 'livid', 'outraged', 'incensed', 'enraged'],
                    'frustration': ['frustrated', 'irritated', 'annoyed', 'aggravated', 'bothered', 'vexed'],
                    'hostility': ['hostile', 'aggressive', 'hate', 'hated', 'despise', 'loathe', 'detest'],
                    'intensity': ['fuming', 'seething', 'boiling', 'steaming', 'explosive', 'volatile'],
                    'actions': ['yell', 'scream', 'shout', 'rage', 'explode', 'burst']
                },
                'weights': {'explicit': 3, 'frustration': 2, 'hostility': 2.5, 'intensity': 2.5, 'actions': 2},
                'intensity_modifiers': ['very', 'extremely', 'incredibly', 'absolutely', 'completely', 'totally']
            },
            'stressed': {
                'keywords': {
                    'explicit': ['stressed', 'anxious', 'worried', 'nervous', 'tense', 'overwhelmed'],
                    'pressure': ['pressure', 'strain', 'burden', 'heavy', 'weight', 'load', 'responsibility'],
                    'exhaustion': ['exhausted', 'tired', 'drained', 'burnout', 'fatigued', 'weary'],
                    'fear': ['panic', 'fear', 'scared', 'afraid', 'terrified', 'frightened', 'alarmed'],
                    'uncertainty': ['concerned', 'uneasy', 'restless', 'jittery', 'on edge', 'apprehensive']
                },
                'weights': {'explicit': 3, 'pressure': 2, 'exhaustion': 2, 'fear': 2.5, 'uncertainty': 2},
                'intensity_modifiers': ['very', 'extremely', 'incredibly', 'completely', 'totally', 'deeply']
            }
        }
        
        # Negation words that can reverse sentiment
        self.negation_words = ['not', 'no', 'never', 'none', 'nothing', 'nobody', 'nowhere', 'neither', 'nor', 'hardly', 'barely', 'scarcely']
        
        # Intensifier words that amplify emotion
        self.intensifiers = ['very', 'extremely', 'incredibly', 'absolutely', 'completely', 'totally', 'deeply', 'really', 'so', 'quite', 'rather']
    
    def analyze_mood(self, text: str) -> MoodAnalysis:
        """Main mood analysis function"""
        if not text or not text.strip():
            return MoodAnalysis(mood='neutral', confidence=0.5, emotions={}, keywords=[])
        
        # Normalize text
        text_lower = text.lower().strip()
        
        # Calculate mood scores using multiple techniques
        mood_scores = self._calculate_mood_scores(text_lower)
        
        # Apply consistency checks
        mood_scores = self._apply_consistency_checks(text_lower, mood_scores)
        
        # Determine final mood and confidence
        detected_mood, confidence = self._determine_mood_and_confidence(mood_scores)
        
        # Extract relevant keywords
        keywords = self._extract_keywords(text_lower, detected_mood)
        
        return MoodAnalysis(
            mood=detected_mood,
            confidence=confidence,
            emotions=mood_scores,
            keywords=keywords
        )
    
    def _calculate_mood_scores(self, text: str) -> Dict[str, float]:
        """Calculate mood scores using weighted keyword analysis"""
        mood_scores = {mood: 0.0 for mood in self.mood_patterns.keys()}
        
        for mood, patterns in self.mood_patterns.items():
            total_score = 0.0
            keyword_count = 0
            
            for category, keywords in patterns['keywords'].items():
                weight = patterns['weights'][category]
                
                for keyword in keywords:
                    # Check for exact matches and word boundaries
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    matches = re.findall(pattern, text)
                    
                    if matches:
                        # Check for negation
                        negated = self._is_negated(text, keyword)
                        # Check for intensifiers
                        intensified = self._is_intensified(text, keyword)
                        
                        # Calculate score
                        base_score = len(matches) * weight
                        if negated:
                            base_score *= -0.5  # Reduce score for negated emotions
                        if intensified:
                            base_score *= 1.5   # Increase score for intensified emotions
                        
                        total_score += base_score
                        keyword_count += len(matches)
            
            # Normalize score based on text length and keyword density
            if keyword_count > 0 and total_score > 0:
                # Apply logarithmic scaling to prevent extreme scores
                text_length = len(text.split())
                if text_length > 0:
                    mood_scores[mood] = math.log(1 + abs(total_score)) * (keyword_count / text_length)
                else:
                    mood_scores[mood] = 0.0
            else:
                mood_scores[mood] = 0.0
        
        return mood_scores
    
    def _is_negated(self, text: str, keyword: str) -> bool:
        """Check if a keyword is negated in the text"""
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return False
        
        # Check for negation words before the keyword
        before_keyword = text[:keyword_pos].split()
        for negation in self.negation_words:
            if negation in before_keyword[-3:]:  # Check last 3 words before keyword
                return True
        
        return False
    
    def _is_intensified(self, text: str, keyword: str) -> bool:
        """Check if a keyword is intensified in the text"""
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return False
        
        # Check for intensifier words before the keyword
        before_keyword = text[:keyword_pos].split()
        for intensifier in self.intensifiers:
            if intensifier in before_keyword[-2:]:  # Check last 2 words before keyword
                return True
        
        return False
    
    def _apply_consistency_checks(self, text: str, mood_scores: Dict[str, float]) -> Dict[str, float]:
        """Apply consistency checks to ensure reliable results"""
        # Check for conflicting emotions
        max_score = max(mood_scores.values())
        if max_score > 0:
            # If there are multiple high scores, reduce the lower ones
            threshold = max_score * 0.7
            for mood in mood_scores:
                if mood_scores[mood] < threshold:
                    mood_scores[mood] *= 0.5
        
        # Check for neutral indicators
        neutral_indicators = ['okay', 'ok', 'fine', 'normal', 'regular', 'average', 'meh', 'whatever']
        neutral_count = sum(1 for indicator in neutral_indicators if indicator in text)
        if neutral_count > 0:
            # Boost neutral score if neutral indicators are present
            mood_scores['neutral'] = max(mood_scores.get('neutral', 0), neutral_count * 0.5)
        
        return mood_scores
    
    def _determine_mood_and_confidence(self, mood_scores: Dict[str, float]) -> Tuple[str, float]:
        """Determine the final mood and confidence score"""
        # Add neutral as a default option
        mood_scores['neutral'] = mood_scores.get('neutral', 0.1)
        
        # Find the mood with highest score
        detected_mood = max(mood_scores, key=mood_scores.get)
        max_score = mood_scores[detected_mood]
        
        # Calculate confidence based on score distribution
        total_score = sum(mood_scores.values())
        if total_score == 0:
            return 'neutral', 0.5
        
        # Confidence is based on how much higher the top score is than others
        sorted_scores = sorted(mood_scores.values(), reverse=True)
        if len(sorted_scores) > 1:
            confidence = (sorted_scores[0] - sorted_scores[1]) / max(total_score, 1)
        else:
            confidence = max_score / max(total_score, 1)
        
        # Ensure confidence is between 0.5 and 1.0
        confidence = max(0.5, min(1.0, confidence))
        
        return detected_mood, confidence
    
    def _extract_keywords(self, text: str, mood: str) -> List[str]:
        """Extract relevant keywords for the detected mood"""
        if mood not in self.mood_patterns:
            return []
        
        keywords = []
        patterns = self.mood_patterns[mood]
        
        for category, keyword_list in patterns['keywords'].items():
            for keyword in keyword_list:
                if keyword in text:
                    keywords.append(keyword)
        
        return keywords[:10]  # Limit to top 10 keywords

# Global analyzer instance
_analyzer = MoodAnalyzer()

async def analyze_mood(text: str) -> MoodAnalysis:
    """Public function for mood analysis with LLM integration"""
    try:
        # Try LLM-based analysis first
        from app.services.llm_mood_analyzer import analyze_mood_with_llm
        llm_result = await analyze_mood_with_llm(text)
        if llm_result and llm_result.confidence > 0.7:
            logger.info(f"✅ LLM analysis successful: {llm_result.mood}")
            return llm_result
    except Exception as e:
        logger.warning(f"LLM analysis failed, falling back to keyword analysis: {e}")
    
    # Fallback to keyword-based analysis
    logger.info("🔄 Using keyword-based analysis")
    return _analyzer.analyze_mood(text)

def analyze_mood_sync(text: str) -> MoodAnalysis:
    """Synchronous wrapper for mood analysis"""
    return asyncio.run(analyze_mood(text))
