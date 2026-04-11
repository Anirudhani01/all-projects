"""
YouTube API Integration Service
Provides video recommendations and content for mood boosting
"""

import logging
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.config import settings
import json

logger = logging.getLogger(__name__)

class YouTubeService:
    """
    YouTube API service for video recommendations and content
    """
    
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = getattr(settings, 'youtube_api_key', None)
        self.rate_limit_remaining = 10000
        self.rate_limit_reset = None
        
        # Mood-based search queries and categories
        self.mood_queries = {
            'happy': [
                'funny videos', 'uplifting stories', 'positive news',
                'dance videos', 'comedy', 'cute animals', 'success stories'
            ],
            'sad': [
                'inspirational videos', 'healing music', 'comforting stories',
                'motivational speeches', 'beautiful nature', 'kindness stories'
            ],
            'angry': [
                'calming videos', 'meditation', 'peaceful music',
                'nature sounds', 'breathing exercises', 'zen videos'
            ],
            'stressed': [
                'relaxing videos', 'meditation', 'nature sounds',
                'spa music', 'breathing exercises', 'mindfulness'
            ],
            'neutral': [
                'educational videos', 'documentaries', 'interesting facts',
                'art videos', 'music videos', 'travel videos'
            ]
        }
        
        # Video categories for better filtering
        self.category_mappings = {
            'happy': ['10', '23', '24'],  # Music, Comedy, Entertainment
            'sad': ['10', '22', '26'],    # Music, People & Blogs, Howto & Style
            'angry': ['10', '28'],        # Music, Science & Technology
            'stressed': ['10', '28'],     # Music, Science & Technology
            'neutral': ['27', '28', '25'] # Education, Science & Technology, News & Politics
        }
        
        # Video duration preferences by mood
        self.duration_preferences = {
            'happy': 'short',      # Short, energetic videos
            'sad': 'medium',       # Medium, thoughtful videos
            'angry': 'short',      # Short, calming videos
            'stressed': 'long',    # Long, relaxing videos
            'neutral': 'any'       # Any duration
        }
    
    async def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make authenticated request to YouTube API with rate limiting"""
        if not self.api_key:
            logger.warning("YouTube API key not configured")
            return None
        
        # Check rate limits
        if self.rate_limit_remaining <= 100:  # Low threshold
            if self.rate_limit_reset and datetime.now() < self.rate_limit_reset:
                logger.warning("YouTube rate limit approaching, waiting...")
                await asyncio.sleep(1)
        
        try:
            params['key'] = self.api_key
            url = f"{self.base_url}{endpoint}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                # Update rate limit info
                self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 10000))
                reset_timestamp = response.headers.get('X-RateLimit-Reset')
                if reset_timestamp:
                    self.rate_limit_reset = datetime.fromtimestamp(int(reset_timestamp))
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 1))
                    logger.warning(f"YouTube rate limited, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(endpoint, params)  # Retry
                else:
                    logger.error(f"YouTube API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"YouTube API request failed: {e}")
            return None
    
    async def search_videos(
        self, 
        query: str, 
        max_results: int = 10,
        duration: str = "any",
        category_id: str = None
    ) -> List[Dict]:
        """Search for videos based on query and filters"""
        try:
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": min(max_results, 50),  # YouTube max is 50
                "order": "relevance",
                "safeSearch": "moderate"
            }
            
            # Add duration filter
            if duration == "short":
                params["videoDuration"] = "short"  # < 4 minutes
            elif duration == "medium":
                params["videoDuration"] = "medium"  # 4-20 minutes
            elif duration == "long":
                params["videoDuration"] = "long"    # > 20 minutes
            
            # Add category filter
            if category_id:
                params["videoCategoryId"] = category_id
            
            data = await self._make_request("/search", params)
            if data and "items" in data:
                videos = data["items"]
                return [self._format_video(video) for video in videos]
            
            return []
            
        except Exception as e:
            logger.error(f"Video search failed: {e}")
            return []
    
    async def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """Get detailed information for specific videos"""
        try:
            if not video_ids:
                return []
            
            # YouTube API allows up to 50 video IDs per request
            video_ids = video_ids[:50]
            params = {
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(video_ids)
            }
            
            data = await self._make_request("/videos", params)
            if data and "items" in data:
                videos = data["items"]
                return [self._format_detailed_video(video) for video in videos]
            
            return []
            
        except Exception as e:
            logger.error(f"Video details failed: {e}")
            return []
    
    async def get_playlist_videos(self, playlist_id: str, max_results: int = 20) -> List[Dict]:
        """Get videos from a specific playlist"""
        try:
            params = {
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": min(max_results, 50)
            }
            
            data = await self._make_request("/playlistItems", params)
            if data and "items" in data:
                videos = []
                for item in data["items"]:
                    if "snippet" in item:
                        video = self._format_playlist_video(item)
                        if video:
                            videos.append(video)
                return videos
            
            return []
        except Exception as e:
            logger.error(f"Playlist videos failed: {e}")
            return []
    
    async def search_playlists(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for playlists"""
        try:
            params = {
                "part": "snippet",
                "q": query,
                "type": "playlist",
                "maxResults": min(max_results, 50)
            }
            
            data = await self._make_request("/search", params)
            if data and "items" in data:
                playlists = data["items"]
                return [self._format_playlist(playlist) for playlist in playlists]
            
            return []
        except Exception as e:
            logger.error(f"Playlist search failed: {e}")
            return []
    
    async def get_mood_videos(
        self, 
        mood: str, 
        max_results: int = 5,
        include_playlists: bool = True
    ) -> Dict[str, Any]:
        """Get comprehensive video recommendations for a mood"""
        try:
            results = {
                "videos": [],
                "playlists": [],
                "mood": mood,
                "source": "youtube",
                "timestamp": datetime.now().isoformat()
            }
            
            # Get video recommendations
            mood_queries = self.mood_queries.get(mood, ["motivational videos"])
            duration = self.duration_preferences.get(mood, "any")
            categories = self.category_mappings.get(mood, [])
            
            for query in mood_queries[:3]:  # Limit to 3 queries
                videos = await self.search_videos(
                    query, 
                    max_results // len(mood_queries[:3]) + 1,
                    duration,
                    categories[0] if categories else None
                )
                results["videos"].extend(videos)
                if len(results["videos"]) >= max_results:
                    break
            
            # Get playlist recommendations if requested
            if include_playlists:
                for query in mood_queries[:2]:  # Limit to 2 playlist queries
                    playlists = await self.search_playlists(f"{query} playlist", 3)
                    results["playlists"].extend(playlists)
                    if len(results["playlists"]) >= 5:  # Limit total playlists
                        break
            
            # Remove duplicates
            seen_ids = set()
            results["videos"] = [video for video in results["videos"] if video.get("id") and video["id"] not in seen_ids and not seen_ids.add(video["id"])]
            results["playlists"] = [playlist for playlist in results["playlists"] if playlist.get("id") and playlist["id"] not in seen_ids and not seen_ids.add(playlist["id"])]
            
            # Limit results
            results["videos"] = results["videos"][:max_results]
            results["playlists"] = results["playlists"][:5]
            
            return results
            
        except Exception as e:
            logger.error(f"Mood video generation failed: {e}")
            return {
                "videos": [],
                "playlists": [],
                "mood": mood,
                "source": "fallback",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _format_video(self, video: Dict) -> Dict:
        """Format video data for our application"""
        try:
            snippet = video.get("snippet", {})
            video_id = video.get("id", {}).get("videoId", "")
            
            return {
                "id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "embed_url": f"https://www.youtube.com/embed/{video_id}",
                "duration": "Unknown",
                "view_count": 0,
                "like_count": 0,
                "mood_affinity": 0.8  # Default, will be calculated based on content
            }
        except Exception as e:
            logger.error(f"Video formatting failed: {e}")
            return {}
    
    def _format_detailed_video(self, video: Dict) -> Dict:
        """Format detailed video data for our application"""
        try:
            snippet = video.get("snippet", {})
            statistics = video.get("statistics", {})
            content_details = video.get("contentDetails", {})
            video_id = video.get("id", "")
            
            return {
                "id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "embed_url": f"https://www.youtube.com/embed/{video_id}",
                "duration": self._parse_duration(content_details.get("duration", "")),
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
                "category_id": snippet.get("categoryId", ""),
                "tags": snippet.get("tags", []),
                "mood_affinity": 0.8
            }
        except Exception as e:
            logger.error(f"Detailed video formatting failed: {e}")
            return {}
    
    def _format_playlist_video(self, item: Dict) -> Optional[Dict]:
        """Format video from playlist item"""
        try:
            snippet = item.get("snippet", {})
            video_id = snippet.get("resourceId", {}).get("videoId", "")
            
            if not video_id:
                return None
            
            return {
                "id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "embed_url": f"https://www.youtube.com/embed/{video_id}",
                "duration": "Unknown",
                "mood_affinity": 0.8
            }
        except Exception as e:
            logger.error(f"Playlist video formatting failed: {e}")
            return None
    
    def _format_playlist(self, playlist: Dict) -> Dict:
        """Format playlist data for our application"""
        try:
            snippet = playlist.get("snippet", {})
            playlist_id = playlist.get("id", {}).get("playlistId", "")
            
            return {
                "id": playlist_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://www.youtube.com/playlist?list={playlist_id}",
                "item_count": snippet.get("itemCount", 0),
                "mood_affinity": 0.8
            }
        except Exception as e:
            logger.error(f"Playlist formatting failed: {e}")
            return {}
    
    def _parse_duration(self, duration: str) -> str:
        """Parse ISO 8601 duration to readable format"""
        try:
            if not duration:
                return "Unknown"
            
            # Remove PT prefix
            duration = duration.replace("PT", "")
            
            # Parse hours, minutes, seconds
            hours = 0
            minutes = 0
            seconds = 0
            
            if "H" in duration:
                hours = int(duration.split("H")[0].split("M")[0].split("S")[0])
                duration = duration.split("H")[1]
            
            if "M" in duration:
                minutes = int(duration.split("M")[0].split("S")[0])
                duration = duration.split("M")[1]
            
            if "S" in duration:
                seconds = int(duration.split("S")[0])
            
            # Format as MM:SS or HH:MM:SS
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
                
        except Exception as e:
            logger.error(f"Duration parsing failed: {e}")
            return "Unknown"
    
    async def health_check(self) -> Dict[str, Any]:
        """Check YouTube API health and credentials"""
        try:
            if not self.api_key:
                return {
                    "status": "error",
                    "message": "YouTube API key not configured",
                    "configured": False
                }
            
            # Try a simple API call
            data = await self._make_request("/search", {
                "part": "snippet",
                "q": "test",
                "type": "video",
                "maxResults": 1
            })
            
            if data:
                return {
                    "status": "healthy",
                    "message": "YouTube API is working",
                    "configured": True,
                    "rate_limit_remaining": self.rate_limit_remaining
                }
            else:
                return {
                    "status": "error",
                    "message": "API call failed",
                    "configured": True
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Health check failed: {e}",
                "configured": bool(self.api_key)
            }

# Global YouTube service instance
youtube_service = YouTubeService()

async def get_youtube_videos(mood: str, max_results: int = 5) -> Dict[str, Any]:
    """Public function for getting YouTube video recommendations"""
    return await youtube_service.get_mood_videos(mood, max_results)

async def search_youtube_videos(query: str, max_results: int = 10) -> List[Dict]:
    """Public function for searching YouTube videos"""
    return await youtube_service.search_videos(query, max_results)

async def get_youtube_health() -> Dict[str, Any]:
    """Public function for YouTube health check"""
    return await youtube_service.health_check()
