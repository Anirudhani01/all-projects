"""
Response Combiner Service for Decision Layer
Combines different content types into cohesive, engaging responses
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.schemas.decision import (
    GeneratedContent, ResponseCombination, DecisionResponse, ContentType
)
import random

logger = logging.getLogger(__name__)

class ResponseCombiner:
    """
    Combines different content types into cohesive responses
    """
    
    def __init__(self):
        self.combination_strategies = {
            'focused': self._combine_focused,
            'balanced': self._combine_balanced,
            'comprehensive': self._combine_comprehensive
        }
        
        self.content_flow_patterns = {
            'gentle': ['quote', 'meditation', 'breathing'],
            'calming': ['meditation', 'music', 'breathing'],
            'energetic': ['story', 'game', 'activity'],
            'neutral': ['quote', 'story', 'activity']
        }
    
    async def combine_response(
        self, 
        decision_response: DecisionResponse,
        generated_content: List[GeneratedContent]
    ) -> ResponseCombination:
        """
        Combine generated content into a cohesive response
        
        Args:
            decision_response: Decision made by the decision engine
            generated_content: List of generated content
            
        Returns:
            ResponseCombination with combined response
        """
        try:
            logger.info(f"🔄 Combining {len(generated_content)} content pieces")
            
            # Sort content by priority
            sorted_content = sorted(generated_content, key=lambda x: x.metadata.get('priority', 1))
            
            # Select primary content
            primary_content = sorted_content[0] if sorted_content else None
            
            # Select secondary content
            secondary_content = sorted_content[1:] if len(sorted_content) > 1 else []
            
            # Determine combination strategy
            strategy_type = decision_response.strategy.strategy_type
            combination_strategy = self.combination_strategies.get(strategy_type, self._combine_balanced)
            
            # Combine content
            combined_response = await combination_strategy(
                primary_content, secondary_content, decision_response
            )
            
            # Generate interaction flow
            interaction_flow = await self._generate_interaction_flow(
                combined_response, decision_response
            )
            
            # Calculate engagement score
            engagement_score = await self._calculate_engagement_score(
                combined_response, decision_response
            )
            
            logger.info(f"✅ Response combined successfully (engagement: {engagement_score:.2f})")
            
            return ResponseCombination(
                primary_content=primary_content,
                secondary_content=secondary_content,
                combination_strategy=strategy_type,
                total_duration=await self._calculate_total_duration(combined_response),
                interaction_flow=interaction_flow,
                engagement_score=engagement_score
            )
            
        except Exception as e:
            logger.error(f"❌ Response combination failed: {e}")
            return await self._get_fallback_combination(decision_response, generated_content)
    
    async def _combine_focused(
        self, 
        primary_content: GeneratedContent, 
        secondary_content: List[GeneratedContent],
        decision_response: DecisionResponse
    ) -> Dict[str, Any]:
        """Combine content for focused strategy"""
        return {
            "approach": "single_focus",
            "primary_focus": primary_content.content_type,
            "supporting_elements": [content.content_type for content in secondary_content[:1]],
            "flow": "linear",
            "interaction_level": "medium"
        }
    
    async def _combine_balanced(
        self, 
        primary_content: GeneratedContent, 
        secondary_content: List[GeneratedContent],
        decision_response: DecisionResponse
    ) -> Dict[str, Any]:
        """Combine content for balanced strategy"""
        return {
            "approach": "dual_focus",
            "primary_focus": primary_content.content_type,
            "secondary_focus": secondary_content[0].content_type if secondary_content else None,
            "supporting_elements": [content.content_type for content in secondary_content[1:]],
            "flow": "parallel",
            "interaction_level": "medium"
        }
    
    async def _combine_comprehensive(
        self, 
        primary_content: GeneratedContent, 
        secondary_content: List[GeneratedContent],
        decision_response: DecisionResponse
    ) -> Dict[str, Any]:
        """Combine content for comprehensive strategy"""
        return {
            "approach": "multi_focus",
            "primary_focus": primary_content.content_type,
            "secondary_focus": [content.content_type for content in secondary_content],
            "supporting_elements": [],
            "flow": "layered",
            "interaction_level": "high"
        }
    
    async def _generate_interaction_flow(
        self, 
        combined_response: Dict[str, Any],
        decision_response: DecisionResponse
    ) -> List[str]:
        """Generate interaction flow for the combined response"""
        flow = []
        
        # Start with greeting based on mood
        mood = decision_response.strategy.delivery_approach
        if mood == 'gentle':
            flow.append("Welcome to your gentle wellness moment")
        elif mood == 'calming':
            flow.append("Let's find your calm together")
        elif mood == 'energetic':
            flow.append("Ready to boost your positive energy?")
        else:
            flow.append("Let's explore some helpful content together")
        
        # Add content-specific interactions
        approach = combined_response.get("approach", "single_focus")
        
        if approach == "single_focus":
            flow.append("Focus on this one activity")
            flow.append("Take your time and engage fully")
        elif approach == "dual_focus":
            flow.append("Start with the primary activity")
            flow.append("Then explore the secondary option")
            flow.append("Choose what feels right for you")
        else:  # multi_focus
            flow.append("Explore these different options")
            flow.append("Mix and match as you like")
            flow.append("Take breaks between activities")
        
        # Add mood-specific guidance
        if decision_response.strategy.delivery_approach == 'gentle':
            flow.append("Remember to be kind to yourself")
            flow.append("There's no rush - go at your own pace")
        elif decision_response.strategy.delivery_approach == 'calming':
            flow.append("Focus on your breathing")
            flow.append("Let tension melt away")
        elif decision_response.strategy.delivery_approach == 'energetic':
            flow.append("Channel your energy positively")
            flow.append("Enjoy the movement and engagement")
        
        # Add closing
        flow.append("How are you feeling now?")
        flow.append("Would you like to try something else?")
        
        return flow
    
    async def _calculate_engagement_score(
        self, 
        combined_response: Dict[str, Any],
        decision_response: DecisionResponse
    ) -> float:
        """Calculate engagement score for the combined response"""
        score = 0.0
        
        # Base score from decision confidence
        score += decision_response.confidence * 0.3
        
        # Score from personalization
        score += decision_response.personalization_score * 0.3
        
        # Score from content variety
        approach = combined_response.get("approach", "single_focus")
        if approach == "single_focus":
            score += 0.2
        elif approach == "dual_focus":
            score += 0.4
        else:  # multi_focus
            score += 0.6
        
        # Score from interaction level
        interaction_level = decision_response.strategy.interaction_level
        if interaction_level == "high":
            score += 0.3
        elif interaction_level == "medium":
            score += 0.2
        else:
            score += 0.1
        
        # Score from delivery approach appropriateness
        delivery_approach = decision_response.strategy.delivery_approach
        if delivery_approach in ['gentle', 'calming']:
            score += 0.2  # These approaches are generally more engaging
        
        return min(1.0, score)
    
    async def _calculate_total_duration(self, combined_response: Dict[str, Any]) -> int:
        """Calculate total duration for the combined response"""
        # This would be calculated based on actual content durations
        # For now, return estimated duration
        approach = combined_response.get("approach", "single_focus")
        
        if approach == "single_focus":
            return 10  # 10 minutes
        elif approach == "dual_focus":
            return 20  # 20 minutes
        else:  # multi_focus
            return 30  # 30 minutes
    
    async def _get_fallback_combination(
        self, 
        decision_response: DecisionResponse,
        generated_content: List[GeneratedContent]
    ) -> ResponseCombination:
        """Provide fallback combination when combination fails"""
        primary_content = generated_content[0] if generated_content else GeneratedContent(
            content_type="quote",
            content={"text": "This too shall pass.", "author": "Persian Proverb"},
            metadata={"generation_method": "fallback"},
            generation_confidence=0.5,
            personalization_score=0.0
        )
        
        return ResponseCombination(
            primary_content=primary_content,
            secondary_content=generated_content[1:] if len(generated_content) > 1 else [],
            combination_strategy="focused",
            total_duration=5,
            interaction_flow=["Let's try this simple activity", "Take your time", "How do you feel?"],
            engagement_score=0.5
        )
    
    async def create_personalized_intro(
        self, 
        decision_response: DecisionResponse,
        user_context: Optional[Dict] = None
    ) -> str:
        """Create personalized introduction for the response"""
        mood = decision_response.strategy.delivery_approach
        reasoning = decision_response.reasoning
        
        # Base introduction
        intro_parts = []
        
        # Mood-based greeting
        if mood == 'gentle':
            intro_parts.append("I can see you're going through a tough time.")
        elif mood == 'calming':
            intro_parts.append("I notice you're feeling some intense emotions.")
        elif mood == 'energetic':
            intro_parts.append("You're in a great mood! Let's keep that energy flowing.")
        else:
            intro_parts.append("I've prepared some content that might help you right now.")
        
        # Add reasoning
        if reasoning:
            intro_parts.append(reasoning)
        
        # Add context if available
        if user_context and user_context.get('context_summary'):
            intro_parts.append(f"Based on your recent entries, {user_context['context_summary'].lower()}")
        
        # Add encouragement
        intro_parts.append("I hope this helps you feel better.")
        
        return ". ".join(intro_parts) + "."
    
    async def create_engagement_prompts(
        self, 
        response_combination: ResponseCombination,
        decision_response: DecisionResponse
    ) -> List[str]:
        """Create engagement prompts to keep user interaction going"""
        prompts = []
        
        # Content-specific prompts
        primary_type = response_combination.primary_content.content_type
        
        if primary_type == 'quote':
            prompts.extend([
                "How does this quote resonate with you?",
                "Would you like to share your thoughts about it?",
                "Does this remind you of any personal experiences?"
            ])
        elif primary_type == 'story':
            prompts.extend([
                "What part of the story stood out to you?",
                "How do you relate to the main character?",
                "What would you do differently in that situation?"
            ])
        elif primary_type == 'meditation':
            prompts.extend([
                "How do you feel after the meditation?",
                "What thoughts came up during your practice?",
                "Would you like to try a different type of meditation?"
            ])
        elif primary_type == 'music':
            prompts.extend([
                "How does this music make you feel?",
                "Does it remind you of any memories?",
                "Would you like to explore more music like this?"
            ])
        elif primary_type == 'game':
            prompts.extend([
                "How did you do in the game?",
                "What was the most challenging part?",
                "Would you like to try a different type of game?"
            ])
        elif primary_type == 'activity':
            prompts.extend([
                "How did the activity make you feel?",
                "What did you learn about yourself?",
                "Would you like to try a similar activity?"
            ])
        elif primary_type == 'breathing':
            prompts.extend([
                "How do you feel after the breathing exercise?",
                "Did you notice any changes in your body?",
                "Would you like to try a different breathing pattern?"
            ])
        
        # Mood-specific prompts
        mood = decision_response.strategy.delivery_approach
        
        if mood == 'gentle':
            prompts.extend([
                "Remember to be kind to yourself today.",
                "Is there anything else you need right now?",
                "How can I support you better?"
            ])
        elif mood == 'calming':
            prompts.extend([
                "Take a moment to notice how you feel now.",
                "What helped you feel more calm?",
                "Would you like to continue with more calming activities?"
            ])
        elif mood == 'energetic':
            prompts.extend([
                "How's your energy level now?",
                "What made you feel most energized?",
                "Ready to try something else exciting?"
            ])
        
        # General engagement prompts
        prompts.extend([
            "How are you feeling overall?",
            "Is there anything specific you'd like to work on?",
            "Would you like to explore a different type of content?"
        ])
        
        return prompts[:5]  # Return top 5 prompts
    
    async def create_follow_up_suggestions(
        self, 
        response_combination: ResponseCombination,
        user_feedback: Optional[Dict] = None
    ) -> List[str]:
        """Create follow-up suggestions based on user feedback"""
        suggestions = []
        
        # Analyze user feedback if available
        if user_feedback:
            mood_change = user_feedback.get('mood_change', 'neutral')
            engagement_level = user_feedback.get('engagement_level', 'medium')
            
            if mood_change == 'improved':
                suggestions.extend([
                    "Great! Let's build on this positive momentum.",
                    "Would you like to try something more challenging?",
                    "How about exploring a different type of content?"
                ])
            elif mood_change == 'declined':
                suggestions.extend([
                    "I understand. Let's try something gentler.",
                    "Would you prefer a different approach?",
                    "Let's focus on just one simple activity."
                ])
            else:
                suggestions.extend([
                    "Let's try a different type of content.",
                    "Would you like to explore something new?",
                    "How about mixing different activities?"
                ])
        else:
            # Default suggestions based on content type
            primary_type = response_combination.primary_content.content_type
            
            if primary_type in ['quote', 'story']:
                suggestions.extend([
                    "Would you like to try a more interactive activity?",
                    "How about some gentle movement or meditation?",
                    "Would you like to explore music or games?"
                ])
            elif primary_type in ['meditation', 'breathing']:
                suggestions.extend([
                    "Would you like to try a creative activity?",
                    "How about reading a story or quote?",
                    "Would you like to try a gentle game?"
                ])
            elif primary_type in ['game', 'activity']:
                suggestions.extend([
                    "Would you like to try something more calming?",
                    "How about meditation or breathing exercises?",
                    "Would you like to read a story or quote?"
                ])
            else:
                suggestions.extend([
                    "Would you like to try something different?",
                    "How about exploring a new type of content?",
                    "What would feel most helpful right now?"
                ])
        
        return suggestions[:3]  # Return top 3 suggestions

# Global response combiner instance
response_combiner = ResponseCombiner()

async def combine_response(
    decision_response: DecisionResponse,
    generated_content: List[GeneratedContent]
) -> ResponseCombination:
    """Public function for response combination"""
    return await response_combiner.combine_response(decision_response, generated_content)

async def create_personalized_intro(
    decision_response: DecisionResponse,
    user_context: Optional[Dict] = None
) -> str:
    """Public function for creating personalized intro"""
    return await response_combiner.create_personalized_intro(decision_response, user_context)

async def create_engagement_prompts(
    response_combination: ResponseCombination,
    decision_response: DecisionResponse
) -> List[str]:
    """Public function for creating engagement prompts"""
    return await response_combiner.create_engagement_prompts(response_combination, decision_response)

async def create_follow_up_suggestions(
    response_combination: ResponseCombination,
    user_feedback: Optional[Dict] = None
) -> List[str]:
    """Public function for creating follow-up suggestions"""
    return await response_combiner.create_follow_up_suggestions(response_combination, user_feedback)
