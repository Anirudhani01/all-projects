"""
Enhanced Mood Analysis Service that integrates Middle Layer
Combines mood detection, context analysis, and theme extraction
"""

import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.services.mood_analysis import analyze_mood
from app.services.context_analyzer import analyze_user_context
from app.services.theme_extractor import extract_user_themes
from app.schemas.mood import MoodAnalysis
from app.schemas.context import EnrichedMoodResponse

logger = logging.getLogger(__name__)

class EnhancedMoodAnalyzer:
    """
    Enhanced mood analysis that integrates all layers:
    1. Input Layer: Mood detection
    2. Middle Layer: Context analysis + Theme extraction
    3. Decision Layer: (Future implementation)
    4. Output Layer: (Future implementation)
    """
    
    def __init__(self):
        self.enabled_layers = {
            "input": True,
            "middle": True,
            "decision": False,  # Not yet implemented
            "output": False     # Not yet implemented
        }
    
    async def analyze_enriched_mood(
        self, 
        user_id: str, 
        text: str, 
        db: Session,
        include_context: bool = True,
        include_themes: bool = True
    ) -> EnrichedMoodResponse:
        """
        Perform enriched mood analysis with context and themes
        
        Args:
            user_id: User identifier
            text: Diary text to analyze
            db: Database session
            include_context: Whether to include context analysis
            include_themes: Whether to include theme analysis
            
        Returns:
            EnrichedMoodResponse with all analysis results
        """
        try:
            # Layer 1: Input Layer - Mood Detection
            logger.info(f"🔍 Starting enhanced mood analysis for user {user_id}")
            mood_result = await analyze_mood(text)
            logger.info(f"✅ Mood detected: {mood_result.mood} (confidence: {mood_result.confidence})")
            
            # Initialize context and theme results
            context_result = None
            theme_result = None
            enrichment_score = 0.0
            
            # Layer 2: Middle Layer - Context Analysis
            if include_context and self.enabled_layers["middle"]:
                try:
                    logger.info("🔍 Analyzing user context...")
                    context_result = await analyze_user_context(user_id, mood_result.mood, text, db)
                    enrichment_score += context_result.get("enrichment_score", 0.0)
                    logger.info(f"✅ Context analysis completed (score: {context_result.get('enrichment_score', 0.0)})")
                except Exception as e:
                    logger.warning(f"❌ Context analysis failed: {e}")
                    context_result = await self._get_fallback_context(mood_result.mood)
            
            # Layer 2: Middle Layer - Theme Extraction
            if include_themes and self.enabled_layers["middle"]:
                try:
                    logger.info("🔍 Extracting themes...")
                    theme_result = await extract_user_themes(user_id, text, db)
                    enrichment_score += theme_result.get("analysis_confidence", 0.0)
                    logger.info(f"✅ Theme extraction completed (confidence: {theme_result.get('analysis_confidence', 0.0)})")
                except Exception as e:
                    logger.warning(f"❌ Theme extraction failed: {e}")
                    theme_result = await self._get_fallback_themes(text)
            
            # Calculate overall enrichment score
            enrichment_score = min(1.0, enrichment_score)
            
            # Create enriched response
            enriched_response = EnrichedMoodResponse(
                mood=mood_result.mood,
                confidence=mood_result.confidence,
                emotions=mood_result.emotions,
                keywords=mood_result.keywords,
                context=context_result,
                themes=theme_result,
                enrichment_score=enrichment_score
            )
            
            logger.info(f"🎉 Enhanced mood analysis completed (enrichment: {enrichment_score:.2f})")
            return enriched_response
            
        except Exception as e:
            logger.error(f"❌ Enhanced mood analysis failed: {e}")
            return await self._get_fallback_enriched_response(user_id, text, mood_result)
    
    async def get_mood_insights(
        self, 
        user_id: str, 
        text: str, 
        db: Session
    ) -> Dict:
        """
        Get comprehensive mood insights including trends and patterns
        
        Args:
            user_id: User identifier
            text: Diary text to analyze
            db: Database session
            
        Returns:
            Dict containing comprehensive mood insights
        """
        try:
            # Perform enriched analysis
            enriched_result = await self.analyze_enriched_mood(user_id, text, db)
            
            # Extract insights
            insights = {
                "mood_summary": {
                    "current_mood": enriched_result.mood,
                    "confidence": enriched_result.confidence,
                    "emotions": enriched_result.emotions,
                    "keywords": enriched_result.keywords
                },
                "context_insights": {},
                "theme_insights": {},
                "recommendations": [],
                "enrichment_score": enriched_result.enrichment_score
            }
            
            # Add context insights
            if enriched_result.context:
                insights["context_insights"] = {
                    "mood_trend": enriched_result.context.trends.trend,
                    "trend_confidence": enriched_result.context.trends.confidence,
                    "stability": enriched_result.context.stability.stability_level,
                    "patterns": len(enriched_result.context.patterns.patterns),
                    "summary": enriched_result.context.context_summary
                }
            
            # Add theme insights
            if enriched_result.themes:
                insights["theme_insights"] = {
                    "top_categories": list(enriched_result.themes.category_themes.categories.keys())[:3],
                    "current_triggers": len(enriched_result.themes.triggers.current_triggers),
                    "theme_confidence": enriched_result.themes.analysis_confidence,
                    "summary": enriched_result.themes.theme_summary
                }
            
            # Generate recommendations
            insights["recommendations"] = await self._generate_recommendations(enriched_result)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get mood insights: {e}")
            return {"error": str(e), "enrichment_score": 0.0}
    
    async def _generate_recommendations(self, enriched_result: EnrichedMoodResponse) -> list:
        """Generate personalized recommendations based on analysis"""
        recommendations = []
        
        # Mood-based recommendations
        mood = enriched_result.mood
        if mood == "sad":
            recommendations.append("Consider reaching out to a friend or family member")
            recommendations.append("Try some gentle self-care activities")
        elif mood == "angry":
            recommendations.append("Take some deep breaths and step away from the situation")
            recommendations.append("Try physical exercise to release tension")
        elif mood == "stressed":
            recommendations.append("Break down your tasks into smaller, manageable pieces")
            recommendations.append("Practice mindfulness or meditation")
        elif mood == "happy":
            recommendations.append("Share your positive energy with others")
            recommendations.append("Document this moment to remember it later")
        
        # Context-based recommendations
        if enriched_result.context:
            if enriched_result.context.trends.trend == "declining":
                recommendations.append("Your mood has been declining recently - consider professional support")
            elif enriched_result.context.stability.stability_level == "low":
                recommendations.append("Your emotions have been quite varied - consider tracking patterns")
        
        # Theme-based recommendations
        if enriched_result.themes:
            triggers = enriched_result.themes.triggers.current_triggers
            if triggers:
                trigger_types = set(t["type"] for t in triggers)
                if "stress_triggers" in trigger_types:
                    recommendations.append("Identify and address your stress triggers")
                if "sadness_triggers" in trigger_types:
                    recommendations.append("Consider talking to someone about what's making you sad")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def _get_fallback_context(self, mood: str) -> Dict:
        """Provide fallback context when analysis fails"""
        return {
            "user_id": "unknown",
            "current_mood": mood,
            "history_summary": {
                "total_entries": 0,
                "analysis_period_days": 0,
                "last_entry_date": None
            },
            "trends": {"trend": "insufficient_data", "direction": "stable", "confidence": 0.0},
            "patterns": {"patterns": [], "recurring_moods": [], "triggers": []},
            "stability": {"stability_score": 0.5, "volatility": "unknown", "consistency": "unknown"},
            "context_summary": "Context analysis unavailable",
            "enrichment_score": 0.0
        }
    
    async def _get_fallback_themes(self, text: str) -> Dict:
        """Provide fallback themes when analysis fails"""
        return {
            "user_id": "unknown",
            "current_text_themes": {
                "categories": {},
                "triggers": [],
                "key_phrases": [],
                "word_count": len(text.split()),
                "sentiment_indicators": []
            },
            "lda_themes": {"themes": [], "topics": [], "confidence": 0.0},
            "category_themes": {"categories": {}, "total_categories": 0},
            "triggers": {"current_triggers": [], "historical_triggers": [], "trigger_summary": ""},
            "theme_evolution": {"evolution": [], "trends": []},
            "theme_summary": "Theme analysis unavailable",
            "analysis_confidence": 0.0
        }
    
    async def _get_fallback_enriched_response(
        self, 
        user_id: str, 
        text: str, 
        mood_result: MoodAnalysis
    ) -> EnrichedMoodResponse:
        """Provide fallback enriched response when analysis fails"""
        return EnrichedMoodResponse(
            mood=mood_result.mood,
            confidence=mood_result.confidence,
            emotions=mood_result.emotions,
            keywords=mood_result.keywords,
            context=await self._get_fallback_context(mood_result.mood),
            themes=await self._get_fallback_themes(text),
            enrichment_score=0.0
        )

# Global enhanced analyzer instance
enhanced_analyzer = EnhancedMoodAnalyzer()

async def analyze_enriched_mood(
    user_id: str, 
    text: str, 
    db: Session,
    include_context: bool = True,
    include_themes: bool = True
) -> EnrichedMoodResponse:
    """Public function for enhanced mood analysis"""
    return await enhanced_analyzer.analyze_enriched_mood(
        user_id, text, db, include_context, include_themes
    )

async def get_mood_insights(user_id: str, text: str, db: Session) -> Dict:
    """Public function for mood insights"""
    return await enhanced_analyzer.get_mood_insights(user_id, text, db)
