"""
ZenQuotes API Integration Service
Provides inspirational quotes and wisdom
"""

import logging
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.config import settings
import json

logger = logging.getLogger(__name__)

class ZenQuotesService:
    """
    ZenQuotes API service for inspirational quotes and wisdom
    """
    
    def __init__(self):
        self.base_url = "https://zenquotes.io/api"
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = None
        
        # Mood-based quote categories and themes
        self.mood_categories = {
            'happy': [
                'happiness', 'joy', 'success', 'gratitude', 'positivity',
                'celebration', 'achievement', 'love', 'friendship'
            ],
            'sad': [
                'healing', 'hope', 'comfort', 'strength', 'courage',
                'resilience', 'support', 'understanding', 'compassion'
            ],
            'angry': [
                'peace', 'calm', 'forgiveness', 'patience', 'wisdom',
                'letting-go', 'acceptance', 'mindfulness', 'serenity'
            ],
            'stressed': [
                'relaxation', 'peace', 'mindfulness', 'balance', 'calm',
                'meditation', 'breathing', 'tranquility', 'zen'
            ],
            'neutral': [
                'wisdom', 'reflection', 'growth', 'learning', 'insight',
                'perspective', 'life', 'philosophy', 'contemplation'
            ]
        }
        
        # Quote types for different moods
        self.quote_types = {
            'happy': ['motivational', 'inspirational', 'success'],
            'sad': ['healing', 'comforting', 'hopeful'],
            'angry': ['calming', 'wise', 'peaceful'],
            'stressed': ['relaxing', 'mindful', 'zen'],
            'neutral': ['philosophical', 'thoughtful', 'wise']
        }
        
        # Fallback quotes for when API is unavailable
        self.fallback_quotes = {
            'happy': [
                {"text": "Happiness is not something ready made. It comes from your own actions.", "author": "Dalai Lama", "category": "wisdom"},
                {"text": "The purpose of our lives is to be happy.", "author": "Dalai Lama", "category": "purpose"},
                {"text": "Joy is the simplest form of gratitude.", "author": "Karl Barth", "category": "gratitude"},
                {"text": "Happiness is when what you think, what you say, and what you do are in harmony.", "author": "Mahatma Gandhi", "category": "harmony"}
            ],
            'sad': [
                {"text": "The way sadness works is one of the strange riddles of the world. If you are stricken with a great sadness, you may feel as if you have been set aflame, not only because of the enormous pain but also because your sadness may spread over your life, like smoke from an enormous fire.", "author": "Lemony Snicket", "category": "understanding"},
                {"text": "The sun will rise and we will try again.", "author": "Twenty One Pilots", "category": "hope"},
                {"text": "You are not alone in this. You are not alone in the world.", "author": "Unknown", "category": "support"},
                {"text": "This too shall pass.", "author": "Persian Proverb", "category": "temporary"}
            ],
            'angry': [
                {"text": "For every minute you remain angry, you give up sixty seconds of peace of mind.", "author": "Ralph Waldo Emerson", "category": "peace"},
                {"text": "Anger is an acid that can do more harm to the vessel in which it is stored than to anything on which it is poured.", "author": "Mark Twain", "category": "wisdom"},
                {"text": "Holding onto anger is like grasping a hot coal with the intent of throwing it at someone else; you are the one who gets burned.", "author": "Buddha", "category": "letting_go"},
                {"text": "The best fighter is never angry.", "author": "Lao Tzu", "category": "strength"}
            ],
            'stressed': [
                {"text": "You have been assigned this mountain to show others it can be moved.", "author": "Mel Robbins", "category": "strength"},
                {"text": "Don't let yesterday take up too much of today.", "author": "Will Rogers", "category": "present"},
                {"text": "The present moment is the only time over which we have dominion.", "author": "Thích Nhất Hạnh", "category": "mindfulness"},
                {"text": "You are braver than you believe, stronger than you seem, and smarter than you think.", "author": "A.A. Milne", "category": "confidence"}
            ],
            'neutral': [
                {"text": "The journey of a thousand miles begins with one step.", "author": "Lao Tzu", "category": "progress"},
                {"text": "Be yourself; everyone else is already taken.", "author": "Oscar Wilde", "category": "authenticity"},
                {"text": "Life is what happens to you while you're busy making other plans.", "author": "John Lennon", "category": "life"},
                {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "category": "passion"}
            ]
        }
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make request to ZenQuotes API with rate limiting"""
        # Check rate limits
        if self.rate_limit_remaining <= 10:  # Low threshold
            if self.rate_limit_reset and datetime.now() < self.rate_limit_reset:
                logger.warning("ZenQuotes rate limit approaching, waiting...")
                await asyncio.sleep(1)
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params or {})
                
                # Update rate limit info (ZenQuotes doesn't provide rate limit headers)
                self.rate_limit_remaining = max(0, self.rate_limit_remaining - 1)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"ZenQuotes rate limited, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(endpoint, params)  # Retry
                else:
                    logger.error(f"ZenQuotes API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"ZenQuotes API request failed: {e}")
            return None
    
    async def get_random_quotes(self, count: int = 1) -> List[Dict]:
        """Get random quotes from ZenQuotes API"""
        try:
            data = await self._make_request("/random")
            if data and isinstance(data, list):
                quotes = []
                for quote_data in data[:count]:
                    formatted_quote = self._format_quote(quote_data)
                    if formatted_quote:
                        quotes.append(formatted_quote)
                return quotes
            return []
            
        except Exception as e:
            logger.error(f"Random quotes failed: {e}")
            return []
    
    async def get_quotes_by_author(self, author: str, count: int = 5) -> List[Dict]:
        """Get quotes by specific author"""
        try:
            params = {"author": author}
            data = await self._make_request("/quotes", params)
            
            if data and isinstance(data, list):
                quotes = []
                for quote_data in data[:count]:
                    formatted_quote = self._format_quote(quote_data)
                    if formatted_quote:
                        quotes.append(formatted_quote)
                return quotes
            return []
            
        except Exception as e:
            logger.error(f"Quotes by author failed: {e}")
            return []
    
    async def get_today_quote(self) -> Optional[Dict]:
        """Get today's featured quote"""
        try:
            data = await self._make_request("/today")
            if data and isinstance(data, list) and len(data) > 0:
                return self._format_quote(data[0])
            return None
            
        except Exception as e:
            logger.error(f"Today's quote failed: {e}")
            return None
    
    async def get_mood_quotes(
        self, 
        mood: str, 
        count: int = 3,
        use_fallback: bool = True
    ) -> List[Dict]:
        """Get quotes tailored to specific mood"""
        try:
            # Try to get quotes from API first
            quotes = await self.get_random_quotes(count * 2)  # Get more to filter
            
            if quotes:
                # Filter quotes based on mood keywords
                mood_keywords = self.mood_categories.get(mood, [])
                filtered_quotes = []
                
                for quote in quotes:
                    if self._matches_mood(quote, mood_keywords):
                        filtered_quotes.append(quote)
                        if len(filtered_quotes) >= count:
                            break
                
                # If we have enough filtered quotes, return them
                if len(filtered_quotes) >= count:
                    return filtered_quotes[:count]
            
            # Fallback to our internal quotes if API fails or doesn't have enough
            if use_fallback:
                fallback_quotes = self.fallback_quotes.get(mood, self.fallback_quotes['neutral'])
                return fallback_quotes[:count]
            
            return quotes[:count] if quotes else []
            
        except Exception as e:
            logger.error(f"Mood quotes failed: {e}")
            if use_fallback:
                return self.fallback_quotes.get(mood, self.fallback_quotes['neutral'])[:count]
            return []
    
    async def search_quotes(self, query: str, count: int = 5) -> List[Dict]:
        """Search for quotes containing specific keywords"""
        try:
            # ZenQuotes doesn't have a search endpoint, so we'll get random quotes
            # and filter them based on the query
            quotes = await self.get_random_quotes(count * 3)  # Get more to filter
            
            if quotes:
                filtered_quotes = []
                query_lower = query.lower()
                
                for quote in quotes:
                    if (query_lower in quote.get('text', '').lower() or 
                        query_lower in quote.get('author', '').lower()):
                        filtered_quotes.append(quote)
                        if len(filtered_quotes) >= count:
                            break
                
                return filtered_quotes[:count]
            
            return []
            
        except Exception as e:
            logger.error(f"Quote search failed: {e}")
            return []
    
    def _format_quote(self, quote_data: Dict) -> Dict:
        """Format quote data for our application"""
        try:
            return {
                "text": quote_data.get("q", ""),
                "author": quote_data.get("a", "Unknown"),
                "category": self._categorize_quote(quote_data.get("q", "")),
                "source": "zenquotes",
                "mood_affinity": 0.8,  # Default, will be calculated based on content
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Quote formatting failed: {e}")
            return {}
    
    def _categorize_quote(self, text: str) -> str:
        """Categorize quote based on content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['happy', 'joy', 'smile', 'laugh', 'celebrate']):
            return 'happiness'
        elif any(word in text_lower for word in ['sad', 'pain', 'hurt', 'cry', 'tears']):
            return 'sadness'
        elif any(word in text_lower for word in ['angry', 'mad', 'rage', 'fury', 'hate']):
            return 'anger'
        elif any(word in text_lower for word in ['stress', 'worry', 'anxiety', 'fear', 'nervous']):
            return 'stress'
        elif any(word in text_lower for word in ['peace', 'calm', 'quiet', 'serene', 'tranquil']):
            return 'peace'
        elif any(word in text_lower for word in ['love', 'heart', 'care', 'kindness', 'compassion']):
            return 'love'
        elif any(word in text_lower for word in ['success', 'achieve', 'win', 'victory', 'triumph']):
            return 'success'
        elif any(word in text_lower for word in ['wisdom', 'learn', 'know', 'understand', 'truth']):
            return 'wisdom'
        else:
            return 'general'
    
    def _matches_mood(self, quote: Dict, mood_keywords: List[str]) -> bool:
        """Check if quote matches mood based on keywords"""
        text = quote.get('text', '').lower()
        author = quote.get('author', '').lower()
        
        # Check if any mood keywords appear in the quote text or author
        for keyword in mood_keywords:
            if keyword in text or keyword in author:
                return True
        
        return False
    
    async def get_quote_categories(self) -> List[str]:
        """Get available quote categories"""
        return list(set([
            category for categories in self.mood_categories.values() 
            for category in categories
        ]))
    
    async def get_quote_authors(self) -> List[str]:
        """Get popular quote authors (from fallback data)"""
        authors = set()
        for mood_quotes in self.fallback_quotes.values():
            for quote in mood_quotes:
                authors.add(quote.get('author', ''))
        return list(authors)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check ZenQuotes API health"""
        try:
            # Try to get a random quote
            data = await self._make_request("/random")
            
            if data and isinstance(data, list) and len(data) > 0:
                return {
                    "status": "healthy",
                    "message": "ZenQuotes API is working",
                    "configured": True,
                    "rate_limit_remaining": self.rate_limit_remaining,
                    "sample_quote": data[0].get("q", "")[:50] + "..." if data[0].get("q") else None
                }
            else:
                return {
                    "status": "error",
                    "message": "API returned no data",
                    "configured": True
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Health check failed: {e}",
                "configured": True
            }
    
    async def get_fallback_quotes(self, mood: str, count: int = 3) -> List[Dict]:
        """Get fallback quotes for a specific mood"""
        try:
            fallback_quotes = self.fallback_quotes.get(mood, self.fallback_quotes['neutral'])
            return fallback_quotes[:count]
        except Exception as e:
            logger.error(f"Fallback quotes failed: {e}")
            return []

# Global ZenQuotes service instance
zenquotes_service = ZenQuotesService()

async def get_zenquotes(mood: str, count: int = 3) -> List[Dict]:
    """Public function for getting ZenQuotes recommendations"""
    return await zenquotes_service.get_mood_quotes(mood, count)

async def get_random_zenquotes(count: int = 1) -> List[Dict]:
    """Public function for getting random ZenQuotes"""
    return await zenquotes_service.get_random_quotes(count)

async def get_zenquotes_health() -> Dict[str, Any]:
    """Public function for ZenQuotes health check"""
    return await zenquotes_service.health_check()
