"""
Decision Engine Service for Decision Layer
Intelligently selects response strategies based on mood, context, and themes
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.schemas.context import EnrichedMoodResponse
from app.schemas.decision import DecisionResponse, ResponseStrategy, ContentType
import random
import json

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Decision Engine for intelligent response strategy selection
    Uses rule-based + ML approach to determine optimal response mix
    """
    
    def __init__(self):
        # Response strategy rules based on mood and context
        self.strategy_rules = {
            'happy': {
                'primary': ['story', 'game'],
                'secondary': ['quote', 'music'],
                'avoid': ['meditation'],
                'intensity_modifier': 1.2
            },
            'sad': {
                'primary': ['story', 'meditation'],
                'secondary': ['quote', 'music'],
                'avoid': ['game'],
                'intensity_modifier': 1.5
            },
            'angry': {
                'primary': ['meditation', 'music'],
                'secondary': ['story', 'quote'],
                'avoid': ['game'],
                'intensity_modifier': 1.8
            },
            'stressed': {
                'primary': ['meditation', 'music'],
                'secondary': ['story', 'quote'],
                'avoid': ['game'],
                'intensity_modifier': 1.6
            },
            'neutral': {
                'primary': ['quote', 'activity'],
                'secondary': ['story', 'music'],
                'avoid': [],
                'intensity_modifier': 1.0
            }
        }
        
        # Context-based strategy adjustments
        self.context_adjustments = {
            'trend_declining': {
                'boost': ['meditation', 'story'],
                'reduce': ['game'],
                'multiplier': 1.3
            },
            'trend_improving': {
                'boost': ['game', 'music'],
                'reduce': ['meditation'],
                'multiplier': 0.8
            },
            'high_volatility': {
                'boost': ['meditation', 'quote'],
                'reduce': ['game'],
                'multiplier': 1.4
            },
            'low_volatility': {
                'boost': ['story', 'activity'],
                'reduce': ['meditation'],
                'multiplier': 0.9
            }
        }
        
        # Theme-based strategy adjustments
        self.theme_adjustments = {
            'work': {
                'boost': ['meditation', 'music'],
                'reduce': ['game'],
                'multiplier': 1.2
            },
            'relationships': {
                'boost': ['story', 'quote'],
                'reduce': ['meditation'],
                'multiplier': 1.1
            },
            'health': {
                'boost': ['meditation', 'activity'],
                'reduce': ['game'],
                'multiplier': 1.3
            },
            'finance': {
                'boost': ['quote', 'story'],
                'reduce': ['game'],
                'multiplier': 1.1
            }
        }
        
        # Trigger-based strategy adjustments
        self.trigger_adjustments = {
            'stress_triggers': {
                'boost': ['meditation', 'music'],
                'reduce': ['game'],
                'multiplier': 1.5
            },
            'sadness_triggers': {
                'boost': ['story', 'quote'],
                'reduce': ['game'],
                'multiplier': 1.4
            },
            'anger_triggers': {
                'boost': ['meditation', 'music'],
                'reduce': ['game'],
                'multiplier': 1.6
            },
            'anxiety_triggers': {
                'boost': ['meditation', 'breathing'],
                'reduce': ['game'],
                'multiplier': 1.7
            }
        }
    
    async def decide_response_strategy(
        self, 
        enriched_mood: EnrichedMoodResponse,
        user_preferences: Optional[Dict] = None
    ) -> DecisionResponse:
        """
        Decide on response strategy based on enriched mood analysis
        
        Args:
            enriched_mood: Enriched mood analysis result
            user_preferences: User's preferred content types
            
        Returns:
            DecisionResponse with selected strategy and content types
        """
        try:
            logger.info(f"🎯 Making decision for mood: {enriched_mood.mood}")
            
            # Start with base strategy for the mood
            base_strategy = self.strategy_rules.get(enriched_mood.mood, self.strategy_rules['neutral'])
            
            # Calculate content type scores
            content_scores = await self._calculate_content_scores(
                enriched_mood, base_strategy, user_preferences
            )
            
            # Apply context adjustments
            content_scores = await self._apply_context_adjustments(
                content_scores, enriched_mood
            )
            
            # Apply theme adjustments
            content_scores = await self._apply_theme_adjustments(
                content_scores, enriched_mood
            )
            
            # Apply trigger adjustments
            content_scores = await self._apply_trigger_adjustments(
                content_scores, enriched_mood
            )
            
            # Select final content types
            selected_content = await self._select_content_types(content_scores)
            
            # Generate response strategy
            strategy = await self._generate_response_strategy(
                selected_content, enriched_mood, user_preferences
            )
            
            # Calculate decision confidence
            confidence = await self._calculate_decision_confidence(
                content_scores, enriched_mood
            )
            
            logger.info(f"✅ Decision made: {[c.type for c in selected_content]} (confidence: {confidence:.2f})")
            
            return DecisionResponse(
                strategy=strategy,
                selected_content=selected_content,
                confidence=confidence,
                reasoning=await self._generate_reasoning(enriched_mood, selected_content),
                estimated_duration=await self._estimate_duration(selected_content),
                personalization_score=await self._calculate_personalization_score(enriched_mood, selected_content)
            )
            
        except Exception as e:
            logger.error(f"❌ Decision making failed: {e}")
            return await self._get_fallback_decision(enriched_mood.mood)
    
    async def _calculate_content_scores(
        self, 
        enriched_mood: EnrichedMoodResponse, 
        base_strategy: Dict,
        user_preferences: Optional[Dict]
    ) -> Dict[str, float]:
        """Calculate initial content type scores"""
        content_types = ['quote', 'story', 'meditation', 'music', 'game', 'activity', 'breathing']
        scores = {}
        
        for content_type in content_types:
            base_score = 0.5  # Neutral base score
            
            # Apply mood-based scoring
            if content_type in base_strategy.get('primary', []):
                base_score += 0.4
            elif content_type in base_strategy.get('secondary', []):
                base_score += 0.2
            elif content_type in base_strategy.get('avoid', []):
                base_score -= 0.3
            
            # Apply user preferences
            if user_preferences and content_type in user_preferences.get('preferred_booster_types', []):
                base_score += 0.2
            
            # Apply mood confidence
            confidence_multiplier = enriched_mood.confidence
            base_score *= confidence_multiplier
            
            # Apply intensity modifier
            intensity_modifier = base_strategy.get('intensity_modifier', 1.0)
            base_score *= intensity_modifier
            
            scores[content_type] = max(0.0, min(1.0, base_score))
        
        return scores
    
    async def _apply_context_adjustments(
        self, 
        content_scores: Dict[str, float], 
        enriched_mood: EnrichedMoodResponse
    ) -> Dict[str, float]:
        """Apply context-based adjustments to content scores"""
        if not enriched_mood.context:
            return content_scores
        
        adjusted_scores = content_scores.copy()
        
        # Apply trend adjustments
        trend = enriched_mood.context.trends.trend
        if trend in self.context_adjustments:
            adjustment = self.context_adjustments[trend]
            for content_type in adjustment.get('boost', []):
                if content_type in adjusted_scores:
                    adjusted_scores[content_type] *= adjustment['multiplier']
            for content_type in adjustment.get('reduce', []):
                if content_type in adjusted_scores:
                    adjusted_scores[content_type] *= (2 - adjustment['multiplier'])
        
        # Apply stability adjustments
        stability = enriched_mood.context.stability.stability_level
        if stability == 'low' and 'high_volatility' in self.context_adjustments:
            adjustment = self.context_adjustments['high_volatility']
            for content_type in adjustment.get('boost', []):
                if content_type in adjusted_scores:
                    adjusted_scores[content_type] *= adjustment['multiplier']
        
        # Normalize scores
        max_score = max(adjusted_scores.values()) if adjusted_scores.values() else 1.0
        if max_score > 0:
            for content_type in adjusted_scores:
                adjusted_scores[content_type] = min(1.0, adjusted_scores[content_type] / max_score)
        
        return adjusted_scores
    
    async def _apply_theme_adjustments(
        self, 
        content_scores: Dict[str, float], 
        enriched_mood: EnrichedMoodResponse
    ) -> Dict[str, float]:
        """Apply theme-based adjustments to content scores"""
        if not enriched_mood.themes:
            return content_scores
        
        adjusted_scores = content_scores.copy()
        
        # Get top themes
        top_themes = list(enriched_mood.themes.category_themes.categories.keys())[:3]
        
        for theme in top_themes:
            if theme in self.theme_adjustments:
                adjustment = self.theme_adjustments[theme]
                for content_type in adjustment.get('boost', []):
                    if content_type in adjusted_scores:
                        adjusted_scores[content_type] *= adjustment['multiplier']
                for content_type in adjustment.get('reduce', []):
                    if content_type in adjusted_scores:
                        adjusted_scores[content_type] *= (2 - adjustment['multiplier'])
        
        return adjusted_scores
    
    async def _apply_trigger_adjustments(
        self, 
        content_scores: Dict[str, float], 
        enriched_mood: EnrichedMoodResponse
    ) -> Dict[str, float]:
        """Apply trigger-based adjustments to content scores"""
        if not enriched_mood.themes:
            return content_scores
        
        adjusted_scores = content_scores.copy()
        
        # Get current triggers
        current_triggers = enriched_mood.themes.triggers.current_triggers
        trigger_types = set(trigger.get('type', '') for trigger in current_triggers)
        
        for trigger_type in trigger_types:
            if trigger_type in self.trigger_adjustments:
                adjustment = self.trigger_adjustments[trigger_type]
                for content_type in adjustment.get('boost', []):
                    if content_type in adjusted_scores:
                        adjusted_scores[content_type] *= adjustment['multiplier']
                for content_type in adjustment.get('reduce', []):
                    if content_type in adjusted_scores:
                        adjusted_scores[content_type] *= (2 - adjustment['multiplier'])
        
        return adjusted_scores
    
    async def _select_content_types(self, content_scores: Dict[str, float]) -> List[ContentType]:
        """Select final content types based on scores"""
        # Sort by score
        sorted_content = sorted(content_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Select top content types (max 3)
        selected = []
        for content_type, score in sorted_content[:3]:
            if score > 0.3:  # Minimum threshold
                selected.append(ContentType(
                    type=content_type,
                    priority=len(selected) + 1,
                    score=score,
                    estimated_duration=self._get_content_duration(content_type)
                ))
        
        # Ensure at least one content type
        if not selected:
            selected.append(ContentType(
                type='quote',
                priority=1,
                score=0.5,
                estimated_duration=2
            ))
        
        return selected
    
    async def _generate_response_strategy(
        self, 
        selected_content: List[ContentType],
        enriched_mood: EnrichedMoodResponse,
        user_preferences: Optional[Dict]
    ) -> ResponseStrategy:
        """Generate response strategy based on selected content"""
        
        # Determine strategy type
        if len(selected_content) == 1:
            strategy_type = "focused"
        elif len(selected_content) == 2:
            strategy_type = "balanced"
        else:
            strategy_type = "comprehensive"
        
        # Determine delivery approach
        if enriched_mood.mood in ['sad', 'stressed']:
            delivery_approach = "gentle"
        elif enriched_mood.mood in ['angry']:
            delivery_approach = "calming"
        elif enriched_mood.mood in ['happy']:
            delivery_approach = "energetic"
        else:
            delivery_approach = "neutral"
        
        # Determine interaction level
        if any(content.type in ['game', 'activity'] for content in selected_content):
            interaction_level = "high"
        elif any(content.type in ['story', 'meditation'] for content in selected_content):
            interaction_level = "medium"
        else:
            interaction_level = "low"
        
        return ResponseStrategy(
            strategy_type=strategy_type,
            delivery_approach=delivery_approach,
            interaction_level=interaction_level,
            content_sequence=[content.type for content in selected_content],
            personalization_factors=await self._identify_personalization_factors(enriched_mood)
        )
    
    async def _calculate_decision_confidence(
        self, 
        content_scores: Dict[str, float], 
        enriched_mood: EnrichedMoodResponse
    ) -> float:
        """Calculate confidence in the decision"""
        if not content_scores:
            return 0.5
        
        # Base confidence from score distribution
        scores = list(content_scores.values())
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        
        # Confidence based on score separation
        sorted_scores = sorted(scores, reverse=True)
        if len(sorted_scores) > 1:
            separation = sorted_scores[0] - sorted_scores[1]
        else:
            separation = max_score
        
        # Confidence based on mood confidence
        mood_confidence = enriched_mood.confidence
        
        # Confidence based on enrichment
        enrichment_score = enriched_mood.enrichment_score
        
        # Combine factors
        confidence = (max_score * 0.4 + separation * 0.3 + mood_confidence * 0.2 + enrichment_score * 0.1)
        
        return min(1.0, max(0.5, confidence))
    
    async def _generate_reasoning(
        self, 
        enriched_mood: EnrichedMoodResponse, 
        selected_content: List[ContentType]
    ) -> str:
        """Generate human-readable reasoning for the decision"""
        reasoning_parts = []
        
        # Mood-based reasoning
        mood = enriched_mood.mood
        if mood == 'sad':
            reasoning_parts.append("I can see you're feeling down, so I've selected gentle, comforting content")
        elif mood == 'angry':
            reasoning_parts.append("I notice you're feeling angry, so I've chosen calming activities to help you relax")
        elif mood == 'stressed':
            reasoning_parts.append("You seem stressed, so I've picked relaxing content to help you unwind")
        elif mood == 'happy':
            reasoning_parts.append("You're in a great mood! I've selected engaging content to keep the positivity flowing")
        
        # Context-based reasoning
        if enriched_mood.context:
            if enriched_mood.context.trends.trend == 'declining':
                reasoning_parts.append("I've noticed your mood has been declining recently, so I've prioritized supportive content")
            elif enriched_mood.context.stability.stability_level == 'low':
                reasoning_parts.append("Your emotions have been quite varied lately, so I've chosen stabilizing content")
        
        # Theme-based reasoning
        if enriched_mood.themes and enriched_mood.themes.category_themes.categories:
            top_theme = max(enriched_mood.themes.category_themes.categories.items(), key=lambda x: x[1]['score'])
            reasoning_parts.append(f"I see you're dealing with {top_theme[0]} issues, so I've tailored the content accordingly")
        
        # Content-based reasoning
        content_types = [content.type for content in selected_content]
        if 'meditation' in content_types:
            reasoning_parts.append("I've included meditation to help you find inner peace")
        if 'story' in content_types:
            reasoning_parts.append("I've added a story to provide comfort and perspective")
        if 'music' in content_types:
            reasoning_parts.append("I've included music to help set the right mood")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "I've selected content based on your current emotional state."
    
    async def _estimate_duration(self, selected_content: List[ContentType]) -> int:
        """Estimate total duration in minutes"""
        return sum(content.estimated_duration for content in selected_content)
    
    async def _calculate_personalization_score(
        self, 
        enriched_mood: EnrichedMoodResponse, 
        selected_content: List[ContentType]
    ) -> float:
        """Calculate how personalized the response is"""
        score = 0.0
        
        # Base personalization from enrichment
        score += enriched_mood.enrichment_score * 0.4
        
        # Personalization from context usage
        if enriched_mood.context and enriched_mood.context.enrichment_score > 0:
            score += 0.3
        
        # Personalization from theme usage
        if enriched_mood.themes and enriched_mood.themes.analysis_confidence > 0:
            score += 0.3
        
        return min(1.0, score)
    
    def _get_content_duration(self, content_type: str) -> int:
        """Get estimated duration for content type in minutes"""
        durations = {
            'quote': 2,
            'story': 5,
            'meditation': 10,
            'music': 5,
            'game': 8,
            'activity': 15,
            'breathing': 5
        }
        return durations.get(content_type, 5)
    
    async def _identify_personalization_factors(self, enriched_mood: EnrichedMoodResponse) -> List[str]:
        """Identify factors used for personalization"""
        factors = []
        
        if enriched_mood.context and enriched_mood.context.enrichment_score > 0:
            factors.append("user_history")
        if enriched_mood.themes and enriched_mood.themes.analysis_confidence > 0:
            factors.append("theme_analysis")
        if enriched_mood.confidence > 0.8:
            factors.append("mood_confidence")
        if enriched_mood.enrichment_score > 0.7:
            factors.append("enrichment_quality")
        
        return factors
    
    async def _get_fallback_decision(self, mood: str) -> DecisionResponse:
        """Provide fallback decision when analysis fails"""
        fallback_content = [ContentType(
            type='quote',
            priority=1,
            score=0.5,
            estimated_duration=2
        )]
        
        return DecisionResponse(
            strategy=ResponseStrategy(
                strategy_type="focused",
                delivery_approach="neutral",
                interaction_level="low",
                content_sequence=['quote'],
                personalization_factors=[]
            ),
            selected_content=fallback_content,
            confidence=0.5,
            reasoning="I've selected a general quote to help you feel better.",
            estimated_duration=2,
            personalization_score=0.0
        )

# Global decision engine instance
decision_engine = DecisionEngine()

async def decide_response_strategy(
    enriched_mood: EnrichedMoodResponse,
    user_preferences: Optional[Dict] = None
) -> DecisionResponse:
    """Public function for decision making"""
    return await decision_engine.decide_response_strategy(enriched_mood, user_preferences)
