"""
Enhanced Content Generators with External API Integration
Combines internal content generation with external APIs (Spotify, YouTube, ZenQuotes)
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.schemas.decision import GeneratedContent
from app.services.content_generators import ContentGenerator
from app.services.external_apis import (
    get_spotify_music, get_youtube_videos, get_zenquotes,
    get_external_content, check_all_apis_health
)
from app.config import settings

logger = logging.getLogger(__name__)

class EnhancedContentGenerator(ContentGenerator):
    """
    Enhanced content generator that uses external APIs when available
    Falls back to internal content generation when APIs are unavailable
    """
    
    def __init__(self):
        super().__init__()
        self.use_external_apis = getattr(settings, 'use_external_apis', True)
        self.api_fallback_enabled = getattr(settings, 'api_fallback_enabled', True)
        
        # Track API usage for optimization
        self.api_usage_stats = {
            'spotify': {'success': 0, 'failed': 0, 'last_used': None},
            'youtube': {'success': 0, 'failed': 0, 'last_used': None},
            'zenquotes': {'success': 0, 'failed': 0, 'last_used': None}
        }
    
    async def generate_content(
        self, 
        content_type: str, 
        mood: str, 
        context: Optional[Dict] = None,
        themes: Optional[Dict] = None,
        user_preferences: Optional[Dict] = None
    ) -> GeneratedContent:
        """
        Generate content using external APIs with fallback to internal generation
        """
        try:
            # Try external APIs first if enabled
            if self.use_external_apis:
                external_content = await self._try_external_apis(
                    content_type, mood, context, themes, user_preferences
                )
                
                if external_content:
                    logger.info(f"✅ Generated {content_type} using external APIs")
                    return external_content
            
            # Fallback to internal generation
            logger.info(f"🔄 Falling back to internal {content_type} generation")
            return await super().generate_content(content_type, mood, context, themes, user_preferences)
            
        except Exception as e:
            logger.error(f"Enhanced content generation failed: {e}")
            return await self._get_fallback_content(content_type, mood)
    
    async def _try_external_apis(
        self, 
        content_type: str, 
        mood: str, 
        context: Optional[Dict],
        themes: Optional[Dict],
        user_preferences: Optional[Dict]
    ) -> Optional[GeneratedContent]:
        """Try to generate content using external APIs"""
        try:
            if content_type == 'quote':
                return await self._generate_quote_external(mood, context, themes)
            elif content_type == 'music':
                return await self._generate_music_external(mood, context, themes)
            elif content_type in ['video', 'story', 'meditation', 'game', 'activity']:
                return await self._generate_video_external(content_type, mood, context, themes)
            else:
                # For other content types, try unified API
                return await self._generate_unified_external(content_type, mood, context, themes)
                
        except Exception as e:
            logger.warning(f"External API generation failed: {e}")
            return None
    
    async def _generate_quote_external(
        self, 
        mood: str, 
        context: Optional[Dict], 
        themes: Optional[Dict]
    ) -> Optional[GeneratedContent]:
        """Generate quotes using ZenQuotes API"""
        try:
            quotes = await get_zenquotes(mood, 3)
            if quotes:
                # Select the best quote based on mood and themes
                selected_quote = self._select_best_quote(quotes, mood, themes)
                
                if selected_quote:
                    self._update_api_stats('zenquotes', True)
                    return GeneratedContent(
                        content_type="quote",
                        content=selected_quote,
                        metadata={
                            "generation_method": "zenquotes_api",
                            "mood_target": mood,
                            "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {},
                            "api_source": "zenquotes"
                        },
                        generation_confidence=0.9,
                        personalization_score=self._calculate_personalization_score(context, themes)
                    )
            
            self._update_api_stats('zenquotes', False)
            return None
            
        except Exception as e:
            logger.error(f"External quote generation failed: {e}")
            self._update_api_stats('zenquotes', False)
            return None
    
    async def _generate_music_external(
        self, 
        mood: str, 
        context: Optional[Dict], 
        themes: Optional[Dict]
    ) -> Optional[GeneratedContent]:
        """Generate music using Spotify API"""
        try:
            music_data = await get_spotify_music(mood, 3)
            if music_data and music_data.get('tracks'):
                # Select the best track
                selected_track = self._select_best_track(music_data['tracks'], mood, themes)
                
                if selected_track:
                    self._update_api_stats('spotify', True)
                    return GeneratedContent(
                        content_type="music",
                        content=selected_track,
                        metadata={
                            "generation_method": "spotify_api",
                            "mood_target": mood,
                            "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {},
                            "api_source": "spotify",
                            "playlist_title": music_data.get('playlist_title', ''),
                            "total_tracks": len(music_data.get('tracks', []))
                        },
                        generation_confidence=0.9,
                        personalization_score=self._calculate_personalization_score(context, themes)
                    )
            
            self._update_api_stats('spotify', False)
            return None
            
        except Exception as e:
            logger.error(f"External music generation failed: {e}")
            self._update_api_stats('spotify', False)
            return None
    
    async def _generate_video_external(
        self, 
        content_type: str, 
        mood: str, 
        context: Optional[Dict], 
        themes: Optional[Dict]
    ) -> Optional[GeneratedContent]:
        """Generate video content using YouTube API"""
        try:
            # Map content types to YouTube search queries
            query_mapping = {
                'video': f"{mood} videos",
                'story': f"{mood} stories",
                'meditation': f"{mood} meditation",
                'game': f"{mood} games",
                'activity': f"{mood} activities"
            }
            
            query = query_mapping.get(content_type, f"{mood} {content_type}")
            videos = await get_youtube_videos(mood, 3)
            
            if videos and videos.get('videos'):
                # Select the best video
                selected_video = self._select_best_video(videos['videos'], mood, themes)
                
                if selected_video:
                    self._update_api_stats('youtube', True)
                    return GeneratedContent(
                        content_type=content_type,
                        content=selected_video,
                        metadata={
                            "generation_method": "youtube_api",
                            "mood_target": mood,
                            "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {},
                            "api_source": "youtube",
                            "search_query": query,
                            "total_videos": len(videos.get('videos', []))
                        },
                        generation_confidence=0.8,
                        personalization_score=self._calculate_personalization_score(context, themes)
                    )
            
            self._update_api_stats('youtube', False)
            return None
            
        except Exception as e:
            logger.error(f"External video generation failed: {e}")
            self._update_api_stats('youtube', False)
            return None
    
    async def _generate_unified_external(
        self, 
        content_type: str, 
        mood: str, 
        context: Optional[Dict], 
        themes: Optional[Dict]
    ) -> Optional[GeneratedContent]:
        """Generate content using unified external API service"""
        try:
            content_data = await get_external_content(mood, [content_type], 1)
            
            if content_data and content_data.get('content', {}).get(content_type):
                content_info = content_data['content'][content_type]
                items = content_info.get('items', [])
                
                if items:
                    selected_item = items[0]  # Take the first item
                    services_used = content_info.get('services_used', [])
                    
                    return GeneratedContent(
                        content_type=content_type,
                        content=selected_item,
                        metadata={
                            "generation_method": "unified_external_api",
                            "mood_target": mood,
                            "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {},
                            "api_source": "unified",
                            "services_used": services_used,
                            "success_rate": content_data.get('success_rate', 0.0)
                        },
                        generation_confidence=0.8,
                        personalization_score=self._calculate_personalization_score(context, themes)
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Unified external generation failed: {e}")
            return None
    
    def _select_best_quote(self, quotes: List[Dict], mood: str, themes: Optional[Dict]) -> Optional[Dict]:
        """Select the best quote based on mood and themes"""
        try:
            if not quotes:
                return None
            
            # Score quotes based on mood relevance
            scored_quotes = []
            for quote in quotes:
                score = self._calculate_quote_score(quote, mood, themes)
                scored_quotes.append((quote, score))
            
            # Sort by score and return the best one
            scored_quotes.sort(key=lambda x: x[1], reverse=True)
            return scored_quotes[0][0]
            
        except Exception as e:
            logger.error(f"Quote selection failed: {e}")
            return quotes[0] if quotes else None
    
    def _select_best_track(self, tracks: List[Dict], mood: str, themes: Optional[Dict]) -> Optional[Dict]:
        """Select the best track based on mood and themes"""
        try:
            if not tracks:
                return None
            
            # Score tracks based on mood relevance
            scored_tracks = []
            for track in tracks:
                score = self._calculate_track_score(track, mood, themes)
                scored_tracks.append((track, score))
            
            # Sort by score and return the best one
            scored_tracks.sort(key=lambda x: x[1], reverse=True)
            return scored_tracks[0][0]
            
        except Exception as e:
            logger.error(f"Track selection failed: {e}")
            return tracks[0] if tracks else None
    
    def _select_best_video(self, videos: List[Dict], mood: str, themes: Optional[Dict]) -> Optional[Dict]:
        """Select the best video based on mood and themes"""
        try:
            if not videos:
                return None
            
            # Score videos based on mood relevance
            scored_videos = []
            for video in videos:
                score = self._calculate_video_score(video, mood, themes)
                scored_videos.append((video, score))
            
            # Sort by score and return the best one
            scored_videos.sort(key=lambda x: x[1], reverse=True)
            return scored_videos[0][0]
            
        except Exception as e:
            logger.error(f"Video selection failed: {e}")
            return videos[0] if videos else None
    
    def _calculate_quote_score(self, quote: Dict, mood: str, themes: Optional[Dict]) -> float:
        """Calculate relevance score for a quote"""
        try:
            score = 0.5  # Base score
            
            # Mood-based scoring
            text = quote.get('text', '').lower()
            mood_keywords = {
                'happy': ['happy', 'joy', 'smile', 'laugh', 'celebrate', 'success'],
                'sad': ['sad', 'pain', 'hurt', 'cry', 'tears', 'healing', 'hope'],
                'angry': ['angry', 'mad', 'rage', 'fury', 'peace', 'calm', 'forgive'],
                'stressed': ['stress', 'worry', 'anxiety', 'fear', 'calm', 'peace', 'relax'],
                'neutral': ['wisdom', 'learn', 'know', 'understand', 'life', 'growth']
            }
            
            mood_words = mood_keywords.get(mood, [])
            for word in mood_words:
                if word in text:
                    score += 0.1
            
            # Theme-based scoring
            if themes and themes.get('category_themes', {}).get('categories'):
                theme_categories = list(themes['category_themes']['categories'].keys())
                for category in theme_categories:
                    if category in text:
                        score += 0.05
            
            # Author reputation (simple scoring)
            author = quote.get('author', '').lower()
            famous_authors = ['dalai lama', 'buddha', 'gandhi', 'einstein', 'jobs', 'lennon']
            if any(famous in author for famous in famous_authors):
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Quote scoring failed: {e}")
            return 0.5
    
    def _calculate_track_score(self, track: Dict, mood: str, themes: Optional[Dict]) -> float:
        """Calculate relevance score for a track"""
        try:
            score = 0.5  # Base score
            
            # Genre-based scoring
            genre = track.get('genre', '').lower()
            mood_genres = {
                'happy': ['pop', 'dance', 'funk', 'disco', 'reggae'],
                'sad': ['indie', 'folk', 'blues', 'soul', 'alternative'],
                'angry': ['ambient', 'classical', 'new-age', 'meditation'],
                'stressed': ['ambient', 'chill', 'lounge', 'jazz', 'classical'],
                'neutral': ['indie', 'alternative', 'rock', 'electronic', 'jazz']
            }
            
            mood_genre_list = mood_genres.get(mood, [])
            if any(genre_match in genre for genre_match in mood_genre_list):
                score += 0.2
            
            # Popularity scoring
            popularity = track.get('popularity', 0)
            if popularity > 70:
                score += 0.1
            elif popularity > 50:
                score += 0.05
            
            # Duration scoring (prefer medium-length tracks)
            duration_ms = track.get('duration_ms', 0)
            duration_minutes = duration_ms / 60000
            if 2 <= duration_minutes <= 5:
                score += 0.1
            elif 1 <= duration_minutes <= 8:
                score += 0.05
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Track scoring failed: {e}")
            return 0.5
    
    def _calculate_video_score(self, video: Dict, mood: str, themes: Optional[Dict]) -> float:
        """Calculate relevance score for a video"""
        try:
            score = 0.5  # Base score
            
            # Title-based scoring
            title = video.get('title', '').lower()
            mood_keywords = {
                'happy': ['funny', 'uplifting', 'positive', 'dance', 'comedy', 'cute'],
                'sad': ['inspirational', 'healing', 'comforting', 'motivational', 'beautiful'],
                'angry': ['calming', 'meditation', 'peaceful', 'zen', 'breathing'],
                'stressed': ['relaxing', 'meditation', 'nature', 'spa', 'mindfulness'],
                'neutral': ['educational', 'documentary', 'interesting', 'art', 'travel']
            }
            
            mood_words = mood_keywords.get(mood, [])
            for word in mood_words:
                if word in title:
                    score += 0.1
            
            # View count scoring (prefer moderately popular videos)
            view_count = video.get('view_count', 0)
            if 1000 <= view_count <= 1000000:  # Sweet spot for engagement
                score += 0.1
            elif view_count > 1000000:  # Very popular
                score += 0.05
            
            # Duration scoring
            duration = video.get('duration', '')
            if mood in ['stressed', 'angry'] and 'long' in duration.lower():
                score += 0.1  # Prefer longer videos for calming moods
            elif mood == 'happy' and 'short' in duration.lower():
                score += 0.1  # Prefer shorter videos for energetic moods
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Video scoring failed: {e}")
            return 0.5
    
    def _update_api_stats(self, service: str, success: bool):
        """Update API usage statistics"""
        try:
            if service in self.api_usage_stats:
                if success:
                    self.api_usage_stats[service]['success'] += 1
                else:
                    self.api_usage_stats[service]['failed'] += 1
                self.api_usage_stats[service]['last_used'] = datetime.now().isoformat()
        except Exception as e:
            logger.error(f"API stats update failed: {e}")
    
    async def get_api_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            total_requests = sum(
                stats['success'] + stats['failed'] 
                for stats in self.api_usage_stats.values()
            )
            
            successful_requests = sum(
                stats['success'] for stats in self.api_usage_stats.values()
            )
            
            success_rate = (successful_requests / total_requests) if total_requests > 0 else 0.0
            
            return {
                'api_usage_stats': self.api_usage_stats,
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'success_rate': success_rate,
                'external_apis_enabled': self.use_external_apis,
                'fallback_enabled': self.api_fallback_enabled
            }
            
        except Exception as e:
            logger.error(f"API usage stats failed: {e}")
            return {}
    
    async def health_check_external_apis(self) -> Dict[str, Any]:
        """Check health of all external APIs"""
        try:
            return await check_all_apis_health()
        except Exception as e:
            logger.error(f"External API health check failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'error',
                'error': str(e)
            }

# Global enhanced content generator instance
enhanced_content_generator = EnhancedContentGenerator()

async def generate_enhanced_content(
    content_type: str,
    mood: str,
    context: Optional[Dict] = None,
    themes: Optional[Dict] = None,
    user_preferences: Optional[Dict] = None
) -> GeneratedContent:
    """Public function for enhanced content generation"""
    return await enhanced_content_generator.generate_content(
        content_type, mood, context, themes, user_preferences
    )

async def get_enhanced_api_stats() -> Dict[str, Any]:
    """Public function for getting API usage statistics"""
    return await enhanced_content_generator.get_api_usage_stats()

async def check_enhanced_api_health() -> Dict[str, Any]:
    """Public function for checking external API health"""
    return await enhanced_content_generator.health_check_external_apis()
