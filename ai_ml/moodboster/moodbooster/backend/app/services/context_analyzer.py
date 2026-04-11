"""
Context Analyzer Service for Middle Layer
Analyzes user history and mood trends to provide enriched context
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models.diary_entry import DiaryEntry
from app.models.session import Session as UserSession
import statistics
import json

logger = logging.getLogger(__name__)

class ContextAnalyzer:
    """
    Context Analyzer for enriching mood data with user history and trends
    """
    
    def __init__(self):
        self.analysis_window_days = 7  # Analyze last 7 days by default
        self.trend_threshold = 0.3  # Threshold for significant mood changes
    
    async def analyze_context(self, user_id: str, current_mood: str, current_text: str, db: Session) -> Dict:
        """
        Analyze user context including history, trends, and patterns
        
        Args:
            user_id: User identifier
            current_mood: Current detected mood
            current_text: Current diary text
            db: Database session
            
        Returns:
            Dict containing enriched context information
        """
        try:
            # Get user history
            history = await self._get_user_history(user_id, db)
            
            # Analyze mood trends
            trends = await self._analyze_mood_trends(history)
            
            # Detect patterns
            patterns = await self._detect_patterns(history, current_mood)
            
            # Calculate mood stability
            stability = await self._calculate_mood_stability(history)
            
            # Generate context summary
            context_summary = await self._generate_context_summary(
                current_mood, trends, patterns, stability
            )
            
            return {
                "user_id": user_id,
                "current_mood": current_mood,
                "history_summary": {
                    "total_entries": len(history),
                    "analysis_period_days": self.analysis_window_days,
                    "last_entry_date": history[0].created_at if history else None
                },
                "trends": trends,
                "patterns": patterns,
                "stability": stability,
                "context_summary": context_summary,
                "enrichment_score": await self._calculate_enrichment_score(trends, patterns, stability)
            }
            
        except Exception as e:
            logger.error(f"Context analysis failed: {e}")
            return await self._get_fallback_context(current_mood)
    
    async def _get_user_history(self, user_id: str, db: Session) -> List[DiaryEntry]:
        """Get user's diary history for analysis"""
        try:
            # Get entries from the last analysis window
            cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
            
            entries = db.query(DiaryEntry)\
                .join(UserSession, DiaryEntry.session_id == UserSession.id)\
                .filter(UserSession.user_id == user_id)\
                .filter(DiaryEntry.created_at >= cutoff_date)\
                .order_by(desc(DiaryEntry.created_at))\
                .limit(50)\
                .all()
            
            logger.info(f"Retrieved {len(entries)} entries for user {user_id}")
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get user history: {e}")
            return []
    
    async def _analyze_mood_trends(self, history: List[DiaryEntry]) -> Dict:
        """Analyze mood trends over time"""
        if not history:
            return {"trend": "insufficient_data", "direction": "stable", "confidence": 0.0}
        
        try:
            # Extract mood scores over time
            mood_scores = []
            mood_counts = {"happy": 0, "sad": 0, "angry": 0, "stressed": 0, "neutral": 0}
            
            for entry in history:
                mood_counts[entry.mood] += 1
                # Convert mood to numeric score for trend analysis
                mood_score = self._mood_to_score(entry.mood)
                mood_scores.append(mood_score)
            
            # Calculate trend direction
            if len(mood_scores) >= 3:
                # Simple linear trend calculation
                trend_direction = self._calculate_trend_direction(mood_scores)
                trend_confidence = self._calculate_trend_confidence(mood_scores)
            else:
                trend_direction = "stable"
                trend_confidence = 0.5
            
            # Determine overall trend
            if trend_confidence > 0.6:
                if trend_direction > 0.1:
                    trend = "improving"
                elif trend_direction < -0.1:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "unclear"
            
            return {
                "trend": trend,
                "direction": trend_direction,
                "confidence": trend_confidence,
                "mood_distribution": mood_counts,
                "average_confidence": statistics.mean([entry.confidence for entry in history]) if history else 0.0
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {"trend": "error", "direction": "stable", "confidence": 0.0}
    
    async def _detect_patterns(self, history: List[DiaryEntry], current_mood: str) -> Dict:
        """Detect patterns in user's mood and behavior"""
        if not history:
            return {"patterns": [], "recurring_moods": [], "triggers": []}
        
        try:
            patterns = []
            recurring_moods = []
            triggers = []
            
            # Analyze mood frequency
            mood_frequency = {}
            for entry in history:
                mood_frequency[entry.mood] = mood_frequency.get(entry.mood, 0) + 1
            
            # Find recurring moods (appearing in >30% of entries)
            total_entries = len(history)
            for mood, count in mood_frequency.items():
                frequency = count / total_entries
                if frequency > 0.3:
                    recurring_moods.append({
                        "mood": mood,
                        "frequency": frequency,
                        "count": count
                    })
            
            # Detect day-of-week patterns
            day_patterns = self._analyze_day_patterns(history)
            if day_patterns:
                patterns.append({
                    "type": "day_of_week",
                    "description": f"Common mood patterns by day: {day_patterns}",
                    "confidence": 0.7
                })
            
            # Detect mood sequences
            mood_sequences = self._analyze_mood_sequences(history)
            if mood_sequences:
                patterns.append({
                    "type": "mood_sequence",
                    "description": f"Common mood progressions: {mood_sequences}",
                    "confidence": 0.6
                })
            
            # Detect current mood context
            if current_mood in [m["mood"] for m in recurring_moods]:
                patterns.append({
                    "type": "recurring_mood",
                    "description": f"This {current_mood} mood appears frequently in your entries",
                    "confidence": 0.8
                })
            
            return {
                "patterns": patterns,
                "recurring_moods": recurring_moods,
                "triggers": triggers,
                "pattern_count": len(patterns)
            }
            
        except Exception as e:
            logger.error(f"Pattern detection failed: {e}")
            return {"patterns": [], "recurring_moods": [], "triggers": []}
    
    async def _calculate_mood_stability(self, history: List[DiaryEntry]) -> Dict:
        """Calculate mood stability metrics"""
        if len(history) < 2:
            return {"stability_score": 0.5, "volatility": "unknown", "consistency": "unknown"}
        
        try:
            mood_scores = [self._mood_to_score(entry.mood) for entry in history]
            
            # Calculate standard deviation as volatility measure
            if len(mood_scores) > 1:
                volatility = statistics.stdev(mood_scores)
            else:
                volatility = 0.0
            
            # Calculate consistency (how often mood changes)
            mood_changes = 0
            for i in range(1, len(history)):
                if history[i].mood != history[i-1].mood:
                    mood_changes += 1
            
            change_rate = mood_changes / (len(history) - 1) if len(history) > 1 else 0
            
            # Determine stability levels
            if volatility < 0.5 and change_rate < 0.3:
                stability_level = "high"
                stability_score = 0.8
            elif volatility < 1.0 and change_rate < 0.6:
                stability_level = "medium"
                stability_score = 0.6
            else:
                stability_level = "low"
                stability_score = 0.3
            
            return {
                "stability_score": stability_score,
                "volatility": volatility,
                "change_rate": change_rate,
                "stability_level": stability_level,
                "consistency": "high" if change_rate < 0.4 else "low"
            }
            
        except Exception as e:
            logger.error(f"Stability calculation failed: {e}")
            return {"stability_score": 0.5, "volatility": "unknown", "consistency": "unknown"}
    
    async def _generate_context_summary(self, current_mood: str, trends: Dict, patterns: Dict, stability: Dict) -> str:
        """Generate a human-readable context summary"""
        summary_parts = []
        
        # Add trend information
        if trends["trend"] != "insufficient_data":
            if trends["trend"] == "improving":
                summary_parts.append("Your mood has been improving recently")
            elif trends["trend"] == "declining":
                summary_parts.append("You've been experiencing some challenges lately")
            elif trends["trend"] == "stable":
                summary_parts.append("Your mood has been relatively stable")
        
        # Add pattern information
        if patterns["recurring_moods"]:
            most_common = max(patterns["recurring_moods"], key=lambda x: x["frequency"])
            if most_common["mood"] == current_mood:
                summary_parts.append(f"This {current_mood} mood is something you experience regularly")
        
        # Add stability information
        if stability["stability_level"] == "low":
            summary_parts.append("Your emotions have been quite varied recently")
        elif stability["stability_level"] == "high":
            summary_parts.append("Your emotional state has been quite consistent")
        
        return ". ".join(summary_parts) if summary_parts else "This is a new emotional experience for you."
    
    async def _calculate_enrichment_score(self, trends: Dict, patterns: Dict, stability: Dict) -> float:
        """Calculate how much context enrichment was achieved"""
        score = 0.0
        
        # Trend analysis contribution
        if trends["trend"] != "insufficient_data":
            score += 0.3
        
        # Pattern detection contribution
        if patterns["patterns"]:
            score += min(0.4, len(patterns["patterns"]) * 0.1)
        
        # Stability analysis contribution
        if stability["stability_score"] > 0:
            score += 0.3
        
        return min(1.0, score)
    
    def _mood_to_score(self, mood: str) -> float:
        """Convert mood string to numeric score for trend analysis"""
        mood_scores = {
            "sad": 1.0,
            "angry": 1.5,
            "stressed": 2.0,
            "neutral": 3.0,
            "happy": 4.0
        }
        return mood_scores.get(mood, 3.0)
    
    def _calculate_trend_direction(self, scores: List[float]) -> float:
        """Calculate trend direction using simple linear regression"""
        if len(scores) < 2:
            return 0.0
        
        n = len(scores)
        x = list(range(n))
        y = scores
        
        # Simple linear regression slope
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _calculate_trend_confidence(self, scores: List[float]) -> float:
        """Calculate confidence in trend analysis"""
        if len(scores) < 3:
            return 0.5
        
        # Calculate R-squared for trend confidence
        n = len(scores)
        x = list(range(n))
        y = scores
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        # Calculate correlation coefficient
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        x_var = sum((x[i] - x_mean) ** 2 for i in range(n))
        y_var = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        if x_var == 0 or y_var == 0:
            return 0.5
        
        correlation = numerator / (x_var * y_var) ** 0.5
        return min(1.0, abs(correlation))
    
    def _analyze_day_patterns(self, history: List[DiaryEntry]) -> Dict:
        """Analyze mood patterns by day of week"""
        day_moods = {}
        for entry in history:
            day = entry.created_at.strftime('%A')
            if day not in day_moods:
                day_moods[day] = []
            day_moods[day].append(entry.mood)
        
        patterns = {}
        for day, moods in day_moods.items():
            if len(moods) >= 2:  # Need at least 2 entries for pattern
                most_common = max(set(moods), key=moods.count)
                patterns[day] = most_common
        
        return patterns
    
    def _analyze_mood_sequences(self, history: List[DiaryEntry]) -> List[str]:
        """Analyze common mood sequences"""
        if len(history) < 3:
            return []
        
        sequences = []
        for i in range(len(history) - 2):
            seq = f"{history[i].mood} -> {history[i+1].mood} -> {history[i+2].mood}"
            sequences.append(seq)
        
        # Find most common sequences
        from collections import Counter
        sequence_counts = Counter(sequences)
        common_sequences = [seq for seq, count in sequence_counts.items() if count > 1]
        
        return common_sequences[:3]  # Return top 3
    
    async def _get_fallback_context(self, current_mood: str) -> Dict:
        """Provide fallback context when analysis fails"""
        return {
            "user_id": "unknown",
            "current_mood": current_mood,
            "history_summary": {
                "total_entries": 0,
                "analysis_period_days": 0,
                "last_entry_date": None
            },
            "trends": {"trend": "insufficient_data", "direction": "stable", "confidence": 0.0},
            "patterns": {"patterns": [], "recurring_moods": [], "triggers": []},
            "stability": {"stability_score": 0.5, "volatility": "unknown", "consistency": "unknown"},
            "context_summary": "This is a new emotional experience for you.",
            "enrichment_score": 0.0
        }

# Global context analyzer instance
context_analyzer = ContextAnalyzer()

async def analyze_user_context(user_id: str, current_mood: str, current_text: str, db: Session) -> Dict:
    """Public function for context analysis"""
    return await context_analyzer.analyze_context(user_id, current_mood, current_text, db)
