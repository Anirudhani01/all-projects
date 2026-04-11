"""
Complete Mood Analysis Service that integrates all layers
Input Layer + Middle Layer + Decision Layer + Output Layer
"""

import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.schemas.context import EnrichedMoodResponse
from app.schemas.decision import DecisionResponse, ResponseCombination
from app.services.enhanced_mood_analysis import analyze_enriched_mood
from app.services.decision_engine import decide_response_strategy
from app.services.content_generators import generate_content
from app.services.response_combiner import (
    combine_response, create_personalized_intro,
    create_engagement_prompts, create_follow_up_suggestions
)

logger = logging.getLogger(__name__)

class CompleteMoodAnalysis:
    """
    Complete mood analysis integrating all four layers:
    1. Input Layer: Mood detection
    2. Middle Layer: Context analysis + Theme extraction
    3. Decision Layer: Response strategy + Content generation
    4. Output Layer: Response combination + Engagement
    """
    
    def __init__(self):
        self.enabled_layers = {
            "input": True,
            "middle": True,
            "decision": True,
            "output": True
        }
    
    async def analyze_complete_mood(
        self,
        user_id: str,
        text: str,
        db: Session,
        user_preferences: Optional[Dict] = None,
        include_context: bool = True,
        include_themes: bool = True
    ) -> Dict:
        """
        Complete mood analysis with all layers
        
        Args:
            user_id: User identifier
            text: Diary text to analyze
            db: Database session
            user_preferences: User's preferences
            include_context: Whether to include context analysis
            include_themes: Whether to include theme analysis
            
        Returns:
            Dict containing complete analysis and response
        """
        try:
            logger.info(f"🚀 Starting complete mood analysis for user {user_id}")
            
            # Layer 1: Input Layer - Mood Detection
            logger.info("🔍 Layer 1: Analyzing mood...")
            enriched_mood = await analyze_enriched_mood(
                user_id, text, db, include_context, include_themes
            )
            
            # Layer 2: Middle Layer - Context & Themes (already included in enriched_mood)
            logger.info("🔍 Layer 2: Context and themes analyzed")
            
            # Layer 3: Decision Layer - Strategy & Content Generation
            logger.info("🔍 Layer 3: Making decision and generating content...")
            decision = await decide_response_strategy(enriched_mood, user_preferences)
            
            # Generate content for selected types
            generated_content = []
            for content_type in decision.selected_content:
                try:
                    content = await generate_content(
                        content_type=content_type.type,
                        mood=enriched_mood.mood,
                        context=enriched_mood.context.dict() if enriched_mood.context else None,
                        themes=enriched_mood.themes.dict() if enriched_mood.themes else None,
                        user_preferences=user_preferences
                    )
                    generated_content.append(content)
                except Exception as e:
                    logger.warning(f"Failed to generate {content_type.type}: {e}")
                    continue
            
            # Layer 4: Output Layer - Response Combination & Engagement
            logger.info("🔍 Layer 4: Combining response and creating engagement...")
            combination = await combine_response(decision, generated_content)
            
            # Create personalized intro
            intro = await create_personalized_intro(
                decision, enriched_mood.context.dict() if enriched_mood.context else None
            )
            
            # Create engagement prompts
            prompts = await create_engagement_prompts(combination, decision)
            
            # Create follow-up suggestions
            suggestions = await create_follow_up_suggestions(combination)
            
            # Calculate overall success score
            success_score = await self._calculate_success_score(
                enriched_mood, decision, combination
            )
            
            logger.info(f"✅ Complete analysis finished (success: {success_score:.2f})")
            
            return {
                "user_id": user_id,
                "analysis_timestamp": __import__('datetime').datetime.now().isoformat(),
                "layers_completed": list(self.enabled_layers.keys()),
                "success_score": success_score,
                
                # Input Layer Results
                "mood_analysis": {
                    "mood": enriched_mood.mood,
                    "confidence": enriched_mood.confidence,
                    "emotions": enriched_mood.emotions,
                    "keywords": enriched_mood.keywords
                },
                
                # Middle Layer Results
                "context_analysis": enriched_mood.context.dict() if enriched_mood.context else None,
                "theme_analysis": enriched_mood.themes.dict() if enriched_mood.themes else None,
                
                # Decision Layer Results
                "decision": decision.dict(),
                "generated_content": [content.dict() for content in generated_content],
                
                # Output Layer Results
                "response_combination": combination.dict(),
                "personalized_intro": intro,
                "engagement_prompts": prompts,
                "follow_up_suggestions": suggestions,
                
                # Summary
                "summary": await self._generate_analysis_summary(
                    enriched_mood, decision, combination
                )
            }
            
        except Exception as e:
            logger.error(f"❌ Complete mood analysis failed: {e}")
            return await self._get_fallback_analysis(user_id, text, str(e))
    
    async def _calculate_success_score(
        self,
        enriched_mood: EnrichedMoodResponse,
        decision: DecisionResponse,
        combination: ResponseCombination
    ) -> float:
        """Calculate overall success score for the analysis"""
        score = 0.0
        
        # Mood analysis quality (30%)
        score += enriched_mood.confidence * 0.3
        
        # Enrichment quality (20%)
        score += enriched_mood.enrichment_score * 0.2
        
        # Decision confidence (20%)
        score += decision.confidence * 0.2
        
        # Content generation success (15%)
        if combination.primary_content:
            score += 0.15
        
        # Engagement potential (15%)
        score += combination.engagement_score * 0.15
        
        return min(1.0, score)
    
    async def _generate_analysis_summary(
        self,
        enriched_mood: EnrichedMoodResponse,
        decision: DecisionResponse,
        combination: ResponseCombination
    ) -> str:
        """Generate a human-readable summary of the analysis"""
        summary_parts = []
        
        # Mood summary
        mood = enriched_mood.mood
        confidence = enriched_mood.confidence
        summary_parts.append(f"I can see you're feeling {mood} (confidence: {confidence:.0%})")
        
        # Context summary
        if enriched_mood.context and enriched_mood.context.context_summary:
            summary_parts.append(enriched_mood.context.context_summary)
        
        # Theme summary
        if enriched_mood.themes and enriched_mood.themes.theme_summary:
            summary_parts.append(enriched_mood.themes.theme_summary)
        
        # Decision summary
        strategy_type = decision.strategy.strategy_type
        content_types = [content.type for content in decision.selected_content]
        summary_parts.append(f"I've prepared a {strategy_type} response with {', '.join(content_types)}")
        
        # Engagement summary
        engagement_score = combination.engagement_score
        if engagement_score > 0.8:
            summary_parts.append("This should be highly engaging for you")
        elif engagement_score > 0.6:
            summary_parts.append("This should be quite engaging")
        else:
            summary_parts.append("This should provide gentle support")
        
        return ". ".join(summary_parts) + "."
    
    async def _get_fallback_analysis(
        self, 
        user_id: str, 
        text: str, 
        error_message: str
    ) -> Dict:
        """Provide fallback analysis when complete analysis fails"""
        return {
            "user_id": user_id,
            "analysis_timestamp": __import__('datetime').datetime.now().isoformat(),
            "layers_completed": ["input"],
            "success_score": 0.3,
            "error": error_message,
            "mood_analysis": {
                "mood": "neutral",
                "confidence": 0.5,
                "emotions": {"neutral": 1.0},
                "keywords": []
            },
            "context_analysis": None,
            "theme_analysis": None,
            "decision": {
                "strategy": {
                    "strategy_type": "focused",
                    "delivery_approach": "neutral",
                    "interaction_level": "low",
                    "content_sequence": ["quote"],
                    "personalization_factors": []
                },
                "selected_content": [{"type": "quote", "priority": 1, "score": 0.5, "estimated_duration": 2}],
                "confidence": 0.5,
                "reasoning": "Fallback response due to analysis error",
                "estimated_duration": 2,
                "personalization_score": 0.0
            },
            "generated_content": [{
                "content_type": "quote",
                "content": {"text": "This too shall pass.", "author": "Persian Proverb"},
                "metadata": {"generation_method": "fallback"},
                "generation_confidence": 0.5,
                "personalization_score": 0.0
            }],
            "response_combination": {
                "primary_content": {
                    "content_type": "quote",
                    "content": {"text": "This too shall pass.", "author": "Persian Proverb"},
                    "metadata": {"generation_method": "fallback"},
                    "generation_confidence": 0.5,
                    "personalization_score": 0.0
                },
                "secondary_content": [],
                "combination_strategy": "focused",
                "total_duration": 2,
                "interaction_flow": ["Let's try this simple quote", "Take your time", "How do you feel?"],
                "engagement_score": 0.5
            },
            "personalized_intro": "I've prepared a simple quote to help you feel better.",
            "engagement_prompts": ["How does this quote make you feel?", "Would you like to try something else?"],
            "follow_up_suggestions": ["Would you like to try a different type of content?"],
            "summary": "I've provided a simple fallback response due to an analysis error."
        }
    
    async def get_quick_booster(
        self,
        mood: str,
        user_id: str,
        db: Session
    ) -> Dict:
        """
        Quick booster without full analysis (for simple use cases)
        """
        try:
            # Create minimal enriched mood
            enriched_mood = EnrichedMoodResponse(
                mood=mood,
                confidence=0.8,
                emotions={mood: 0.8},
                keywords=[],
                context=None,
                themes=None,
                enrichment_score=0.5
            )
            
            # Run decision and content generation
            decision = await decide_response_strategy(enriched_mood)
            
            # Generate content
            generated_content = []
            for content_type in decision.selected_content:
                content = await generate_content(
                    content_type=content_type.type,
                    mood=mood,
                    context=None,
                    themes=None,
                    user_preferences=None
                )
                generated_content.append(content)
            
            # Combine response
            combination = await combine_response(decision, generated_content)
            
            return {
                "mood": mood,
                "user_id": user_id,
                "quick_mode": True,
                "booster": {
                    "decision": decision.dict(),
                    "content": [content.dict() for content in generated_content],
                    "combination": combination.dict(),
                    "intro": "Here's a quick booster to help you feel better.",
                    "prompts": ["How does this make you feel?", "Would you like to try something else?"]
                }
            }
            
        except Exception as e:
            logger.error(f"Quick booster failed: {e}")
            return {
                "mood": mood,
                "user_id": user_id,
                "quick_mode": True,
                "error": str(e),
                "booster": {
                    "content": [{
                        "content_type": "quote",
                        "content": {"text": "This too shall pass.", "author": "Persian Proverb"},
                        "metadata": {"generation_method": "fallback"}
                    }],
                    "intro": "Here's a simple quote to help you feel better.",
                    "prompts": ["How does this make you feel?"]
                }
            }

# Global complete analysis instance
complete_analyzer = CompleteMoodAnalysis()

async def analyze_complete_mood(
    user_id: str,
    text: str,
    db: Session,
    user_preferences: Optional[Dict] = None,
    include_context: bool = True,
    include_themes: bool = True
) -> Dict:
    """Public function for complete mood analysis"""
    return await complete_analyzer.analyze_complete_mood(
        user_id, text, db, user_preferences, include_context, include_themes
    )

async def get_quick_booster(
    mood: str,
    user_id: str,
    db: Session
) -> Dict:
    """Public function for quick booster"""
    return await complete_analyzer.get_quick_booster(mood, user_id, db)
