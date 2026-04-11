"""
Theme Extractor Service for Middle Layer
Uses topic modeling (LDA) to identify themes and triggers in diary entries
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.diary_entry import DiaryEntry
from app.models.session import Session as UserSession
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
from collections import Counter
import json

logger = logging.getLogger(__name__)

class ThemeExtractor:
    """
    Theme Extractor for identifying topics and triggers in diary entries
    """
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.nltk_downloaded = False
        self._ensure_nltk_data()
        
        # Predefined theme categories for better classification
        self.theme_categories = {
            'work': ['work', 'job', 'office', 'meeting', 'project', 'boss', 'colleague', 'deadline', 'career', 'business'],
            'relationships': ['friend', 'family', 'partner', 'relationship', 'love', 'marriage', 'dating', 'social', 'lonely', 'alone'],
            'health': ['health', 'sick', 'illness', 'doctor', 'hospital', 'pain', 'exercise', 'fitness', 'medical', 'treatment'],
            'finance': ['money', 'financial', 'budget', 'expensive', 'cheap', 'cost', 'payment', 'debt', 'income', 'spending'],
            'education': ['school', 'study', 'learning', 'exam', 'test', 'student', 'teacher', 'class', 'homework', 'education'],
            'hobbies': ['hobby', 'sport', 'music', 'art', 'reading', 'gaming', 'travel', 'cooking', 'gardening', 'craft'],
            'personal': ['personal', 'self', 'identity', 'growth', 'development', 'goal', 'dream', 'future', 'past', 'memory'],
            'environment': ['weather', 'season', 'nature', 'outdoor', 'indoor', 'home', 'place', 'location', 'travel', 'vacation']
        }
        
        # Emotional trigger patterns
        self.trigger_patterns = {
            'stress_triggers': ['deadline', 'pressure', 'overwhelmed', 'busy', 'rush', 'urgent', 'demanding'],
            'sadness_triggers': ['loss', 'death', 'breakup', 'rejection', 'failure', 'disappointment', 'lonely'],
            'anger_triggers': ['unfair', 'wrong', 'mistake', 'blame', 'criticism', 'frustrated', 'annoyed'],
            'anxiety_triggers': ['worry', 'fear', 'scared', 'nervous', 'uncertain', 'unknown', 'change']
        }
    
    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        if not self.nltk_downloaded:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)
                self.nltk_downloaded = True
                logger.info("✅ NLTK data downloaded successfully")
            except Exception as e:
                logger.warning(f"❌ NLTK data download failed: {e}")
                self.nltk_downloaded = False
    
    async def extract_themes(self, user_id: str, current_text: str, db: Session) -> Dict:
        """
        Extract themes and triggers from user's diary entries
        
        Args:
            user_id: User identifier
            current_text: Current diary text
            db: Database session
            
        Returns:
            Dict containing theme analysis
        """
        try:
            # Get user's recent entries for context
            recent_entries = await self._get_recent_entries(user_id, db)
            
            # Combine current text with recent entries for better analysis
            all_texts = [entry.text for entry in recent_entries] + [current_text]
            
            # Extract themes using LDA
            lda_themes = await self._extract_lda_themes(all_texts)
            
            # Extract category-based themes
            category_themes = await self._extract_category_themes(all_texts)
            
            # Extract emotional triggers
            triggers = await self._extract_triggers(current_text, all_texts)
            
            # Analyze theme evolution
            theme_evolution = await self._analyze_theme_evolution(recent_entries)
            
            # Generate theme summary
            theme_summary = await self._generate_theme_summary(
                lda_themes, category_themes, triggers, theme_evolution
            )
            
            return {
                "user_id": user_id,
                "current_text_themes": await self._analyze_single_text(current_text),
                "lda_themes": lda_themes,
                "category_themes": category_themes,
                "triggers": triggers,
                "theme_evolution": theme_evolution,
                "theme_summary": theme_summary,
                "analysis_confidence": await self._calculate_theme_confidence(lda_themes, category_themes)
            }
            
        except Exception as e:
            logger.error(f"Theme extraction failed: {e}")
            return await self._get_fallback_themes(current_text)
    
    async def _get_recent_entries(self, user_id: str, db: Session, limit: int = 20) -> List[DiaryEntry]:
        """Get recent diary entries for theme analysis"""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)  # Last 30 days
            
            entries = db.query(DiaryEntry)\
                .join(UserSession, DiaryEntry.session_id == UserSession.id)\
                .filter(UserSession.user_id == user_id)\
                .filter(DiaryEntry.created_at >= cutoff_date)\
                .order_by(DiaryEntry.created_at.desc())\
                .limit(limit)\
                .all()
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get recent entries: {e}")
            return []
    
    async def _extract_lda_themes(self, texts: List[str]) -> Dict:
        """Extract themes using Latent Dirichlet Allocation"""
        if len(texts) < 2:
            return {"themes": [], "topics": [], "confidence": 0.0}
        
        try:
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # Remove empty texts
            processed_texts = [text for text in processed_texts if text.strip()]
            
            if len(processed_texts) < 2:
                return {"themes": [], "topics": [], "confidence": 0.0}
            
            # Create document-term matrix
            vectorizer = CountVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
            
            doc_term_matrix = vectorizer.fit_transform(processed_texts)
            
            # Apply LDA
            n_topics = min(5, len(processed_texts) // 2)  # Adaptive number of topics
            if n_topics < 2:
                n_topics = 2
            
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=10
            )
            
            lda.fit(doc_term_matrix)
            
            # Extract topics
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words_idx = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topics.append({
                    "topic_id": topic_idx,
                    "words": top_words,
                    "weight": float(topic.sum())
                })
            
            # Get document-topic distributions
            doc_topic_dist = lda.transform(doc_term_matrix)
            
            # Find dominant topics
            dominant_topics = []
            for i, dist in enumerate(doc_topic_dist):
                topic_idx = np.argmax(dist)
                confidence = dist[topic_idx]
                if confidence > 0.3:  # Only include topics with reasonable confidence
                    dominant_topics.append({
                        "text_index": i,
                        "topic_id": topic_idx,
                        "confidence": float(confidence)
                    })
            
            return {
                "themes": topics,
                "dominant_topics": dominant_topics,
                "confidence": float(np.mean(doc_topic_dist.max(axis=1)))
            }
            
        except Exception as e:
            logger.error(f"LDA theme extraction failed: {e}")
            return {"themes": [], "topics": [], "confidence": 0.0}
    
    async def _extract_category_themes(self, texts: List[str]) -> Dict:
        """Extract themes based on predefined categories"""
        try:
            all_text = " ".join(texts).lower()
            category_scores = {}
            
            for category, keywords in self.theme_categories.items():
                score = 0
                matched_keywords = []
                
                for keyword in keywords:
                    # Count keyword occurrences
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    matches = len(re.findall(pattern, all_text))
                    if matches > 0:
                        score += matches
                        matched_keywords.append(keyword)
                
                if score > 0:
                    category_scores[category] = {
                        "score": score,
                        "matched_keywords": matched_keywords,
                        "confidence": min(1.0, score / 10)  # Normalize confidence
                    }
            
            # Sort by score
            sorted_categories = sorted(
                category_scores.items(),
                key=lambda x: x[1]["score"],
                reverse=True
            )
            
            return {
                "categories": dict(sorted_categories[:5]),  # Top 5 categories
                "total_categories": len(category_scores)
            }
            
        except Exception as e:
            logger.error(f"Category theme extraction failed: {e}")
            return {"categories": {}, "total_categories": 0}
    
    async def _extract_triggers(self, current_text: str, all_texts: List[str]) -> Dict:
        """Extract emotional triggers from text"""
        try:
            current_triggers = []
            historical_triggers = []
            
            # Analyze current text
            current_text_lower = current_text.lower()
            for trigger_type, keywords in self.trigger_patterns.items():
                for keyword in keywords:
                    if keyword in current_text_lower:
                        current_triggers.append({
                            "type": trigger_type,
                            "keyword": keyword,
                            "context": self._extract_trigger_context(current_text, keyword)
                        })
            
            # Analyze historical texts
            all_text_lower = " ".join(all_texts).lower()
            for trigger_type, keywords in self.trigger_patterns.items():
                for keyword in keywords:
                    if keyword in all_text_lower:
                        historical_triggers.append({
                            "type": trigger_type,
                            "keyword": keyword,
                            "frequency": all_text_lower.count(keyword)
                        })
            
            # Remove duplicates and sort by frequency
            historical_triggers = list({t["keyword"]: t for t in historical_triggers}.values())
            historical_triggers.sort(key=lambda x: x["frequency"], reverse=True)
            
            return {
                "current_triggers": current_triggers,
                "historical_triggers": historical_triggers[:5],  # Top 5
                "trigger_summary": await self._generate_trigger_summary(current_triggers, historical_triggers)
            }
            
        except Exception as e:
            logger.error(f"Trigger extraction failed: {e}")
            return {"current_triggers": [], "historical_triggers": [], "trigger_summary": ""}
    
    async def _analyze_theme_evolution(self, entries: List[DiaryEntry]) -> Dict:
        """Analyze how themes have evolved over time"""
        if len(entries) < 3:
            return {"evolution": [], "trends": []}
        
        try:
            # Split entries into time periods
            mid_point = len(entries) // 2
            recent_entries = entries[:mid_point]
            older_entries = entries[mid_point:]
            
            # Extract themes for each period
            recent_themes = await self._extract_category_themes([e.text for e in recent_entries])
            older_themes = await self._extract_category_themes([e.text for e in older_entries])
            
            # Compare themes
            evolution = []
            recent_categories = set(recent_themes.get("categories", {}).keys())
            older_categories = set(older_themes.get("categories", {}).keys())
            
            # New themes
            new_themes = recent_categories - older_categories
            for theme in new_themes:
                evolution.append({
                    "type": "new",
                    "theme": theme,
                    "confidence": recent_themes["categories"][theme]["confidence"]
                })
            
            # Disappeared themes
            disappeared_themes = older_categories - recent_categories
            for theme in disappeared_themes:
                evolution.append({
                    "type": "disappeared",
                    "theme": theme,
                    "confidence": older_themes["categories"][theme]["confidence"]
                })
            
            # Evolved themes (changed confidence)
            common_themes = recent_categories & older_categories
            for theme in common_themes:
                recent_conf = recent_themes["categories"][theme]["confidence"]
                older_conf = older_themes["categories"][theme]["confidence"]
                change = recent_conf - older_conf
                
                if abs(change) > 0.1:  # Significant change
                    evolution.append({
                        "type": "evolved",
                        "theme": theme,
                        "change": change,
                        "recent_confidence": recent_conf,
                        "older_confidence": older_conf
                    })
            
            return {
                "evolution": evolution,
                "trends": await self._identify_theme_trends(evolution)
            }
            
        except Exception as e:
            logger.error(f"Theme evolution analysis failed: {e}")
            return {"evolution": [], "trends": []}
    
    async def _analyze_single_text(self, text: str) -> Dict:
        """Analyze themes in a single text"""
        try:
            # Extract categories
            categories = await self._extract_category_themes([text])
            
            # Extract triggers
            triggers = await self._extract_triggers(text, [text])
            
            # Extract key phrases
            key_phrases = await self._extract_key_phrases(text)
            
            return {
                "categories": categories.get("categories", {}),
                "triggers": triggers.get("current_triggers", []),
                "key_phrases": key_phrases,
                "word_count": len(text.split()),
                "sentiment_indicators": await self._extract_sentiment_indicators(text)
            }
            
        except Exception as e:
            logger.error(f"Single text analysis failed: {e}")
            return {"categories": {}, "triggers": [], "key_phrases": [], "word_count": 0, "sentiment_indicators": []}
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for LDA analysis"""
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove special characters and digits
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stopwords and lemmatize
            processed_tokens = []
            for token in tokens:
                if token not in self.stop_words and len(token) > 2:
                    lemmatized = self.lemmatizer.lemmatize(token)
                    processed_tokens.append(lemmatized)
            
            return " ".join(processed_tokens)
            
        except Exception as e:
            logger.error(f"Text preprocessing failed: {e}")
            return text.lower()
    
    def _extract_trigger_context(self, text: str, keyword: str) -> str:
        """Extract context around a trigger keyword"""
        try:
            # Find keyword position
            keyword_pos = text.lower().find(keyword.lower())
            if keyword_pos == -1:
                return ""
            
            # Extract context (50 characters before and after)
            start = max(0, keyword_pos - 50)
            end = min(len(text), keyword_pos + len(keyword) + 50)
            
            context = text[start:end]
            return context.strip()
            
        except Exception as e:
            logger.error(f"Context extraction failed: {e}")
            return ""
    
    async def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        try:
            # Simple key phrase extraction using word frequency
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            # Remove stopwords
            words = [word for word in words if word not in self.stop_words]
            
            # Count frequency
            word_freq = Counter(words)
            
            # Get top phrases
            top_words = word_freq.most_common(10)
            
            return [word for word, freq in top_words if freq > 1]
            
        except Exception as e:
            logger.error(f"Key phrase extraction failed: {e}")
            return []
    
    async def _extract_sentiment_indicators(self, text: str) -> List[str]:
        """Extract sentiment indicators from text"""
        try:
            sentiment_words = {
                'positive': ['good', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic', 'happy', 'joy', 'love'],
                'negative': ['bad', 'terrible', 'awful', 'horrible', 'sad', 'angry', 'frustrated', 'disappointed'],
                'intensity': ['very', 'extremely', 'incredibly', 'absolutely', 'completely', 'totally']
            }
            
            indicators = []
            text_lower = text.lower()
            
            for category, words in sentiment_words.items():
                for word in words:
                    if word in text_lower:
                        indicators.append(f"{category}: {word}")
            
            return indicators[:10]  # Limit to top 10
            
        except Exception as e:
            logger.error(f"Sentiment indicator extraction failed: {e}")
            return []
    
    async def _generate_theme_summary(self, lda_themes: Dict, category_themes: Dict, triggers: Dict, evolution: Dict) -> str:
        """Generate a human-readable theme summary"""
        summary_parts = []
        
        # Add category themes
        if category_themes.get("categories"):
            top_category = max(category_themes["categories"].items(), key=lambda x: x[1]["score"])
            summary_parts.append(f"Your entries often focus on {top_category[0]} topics")
        
        # Add triggers
        if triggers.get("current_triggers"):
            trigger_types = set(t["type"] for t in triggers["current_triggers"])
            summary_parts.append(f"Current emotional triggers: {', '.join(trigger_types)}")
        
        # Add evolution
        if evolution.get("evolution"):
            new_themes = [e for e in evolution["evolution"] if e["type"] == "new"]
            if new_themes:
                summary_parts.append(f"New themes emerging: {', '.join([t['theme'] for t in new_themes])}")
        
        return ". ".join(summary_parts) if summary_parts else "No clear themes identified in your recent entries."
    
    async def _calculate_theme_confidence(self, lda_themes: Dict, category_themes: Dict) -> float:
        """Calculate confidence in theme analysis"""
        confidence = 0.0
        
        # LDA confidence
        if lda_themes.get("confidence"):
            confidence += lda_themes["confidence"] * 0.4
        
        # Category confidence
        if category_themes.get("categories"):
            avg_category_conf = np.mean([cat["confidence"] for cat in category_themes["categories"].values()])
            confidence += avg_category_conf * 0.6
        
        return min(1.0, confidence)
    
    async def _identify_theme_trends(self, evolution: List[Dict]) -> List[str]:
        """Identify trends from theme evolution"""
        trends = []
        
        new_count = len([e for e in evolution if e["type"] == "new"])
        disappeared_count = len([e for e in evolution if e["type"] == "disappeared"])
        
        if new_count > disappeared_count:
            trends.append("Themes are expanding and diversifying")
        elif disappeared_count > new_count:
            trends.append("Themes are becoming more focused")
        
        evolved_count = len([e for e in evolution if e["type"] == "evolved"])
        if evolved_count > 0:
            trends.append("Existing themes are evolving in intensity")
        
        return trends
    
    async def _get_fallback_themes(self, current_text: str) -> Dict:
        """Provide fallback theme analysis when extraction fails"""
        return {
            "user_id": "unknown",
            "current_text_themes": await self._analyze_single_text(current_text),
            "lda_themes": {"themes": [], "topics": [], "confidence": 0.0},
            "category_themes": {"categories": {}, "total_categories": 0},
            "triggers": {"current_triggers": [], "historical_triggers": [], "trigger_summary": ""},
            "theme_evolution": {"evolution": [], "trends": []},
            "theme_summary": "Theme analysis unavailable",
            "analysis_confidence": 0.0
        }

# Global theme extractor instance
theme_extractor = ThemeExtractor()

async def extract_user_themes(user_id: str, current_text: str, db: Session) -> Dict:
    """Public function for theme extraction"""
    return await theme_extractor.extract_themes(user_id, current_text, db)
