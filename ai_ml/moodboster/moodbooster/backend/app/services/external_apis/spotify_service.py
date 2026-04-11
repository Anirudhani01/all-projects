"""
Spotify API Integration Service
Provides music recommendations and track information
"""

import logging
import asyncio
import httpx
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.config import settings
import json

logger = logging.getLogger(__name__)

class SpotifyService:
    """
    Spotify API service for music recommendations and track information
    """
    
    def __init__(self):
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.client_id = getattr(settings, 'spotify_client_id', None)
        self.client_secret = getattr(settings, 'spotify_client_secret', None)
        self.access_token = None
        self.token_expires_at = None
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = None
        
        # Mood-based search queries
        self.mood_queries = {
            'happy': [
                'upbeat pop', 'feel good music', 'positive energy',
                'dance music', 'summer hits', 'party music'
            ],
            'sad': [
                'melancholy', 'emotional', 'healing music',
                'indie folk', 'acoustic', 'comforting'
            ],
            'angry': [
                'calming music', 'ambient', 'peaceful',
                'meditation music', 'nature sounds', 'zen'
            ],
            'stressed': [
                'relaxing music', 'ambient', 'meditation',
                'nature sounds', 'spa music', 'chill'
            ],
            'neutral': [
                'indie', 'alternative', 'contemplative',
                'mellow', 'thoughtful', 'balanced'
            ]
        }
        
        # Genre mappings for better recommendations
        self.genre_mappings = {
            'happy': ['pop', 'dance', 'funk', 'disco', 'reggae'],
            'sad': ['indie', 'folk', 'blues', 'soul', 'alternative'],
            'angry': ['ambient', 'classical', 'new-age', 'meditation'],
            'stressed': ['ambient', 'chill', 'lounge', 'jazz', 'classical'],
            'neutral': ['indie', 'alternative', 'rock', 'electronic', 'jazz']
        }
    
    async def get_access_token(self) -> bool:
        """Get Spotify access token using client credentials flow"""
        if not self.client_id or not self.client_secret:
            logger.warning("Spotify credentials not configured")
            return False
        
        try:
            # Check if token is still valid
            if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
                return True
            
            # Prepare credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            # Request token
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.auth_url,
                    headers={
                        "Authorization": f"Basic {encoded_credentials}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={"grant_type": "client_credentials"}
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # 1 minute buffer
                    
                    logger.info("✅ Spotify access token obtained successfully")
                    return True
                else:
                    logger.error(f"❌ Failed to get Spotify token: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Spotify token request failed: {e}")
            return False
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Spotify API with rate limiting"""
        if not await self.get_access_token():
            return None
        
        # Check rate limits
        if self.rate_limit_remaining <= 10:  # Low threshold
            if self.rate_limit_reset and datetime.now() < self.rate_limit_reset:
                logger.warning("Rate limit approaching, waiting...")
                await asyncio.sleep(1)
        
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                
                # Update rate limit info
                self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 1000))
                reset_timestamp = response.headers.get('X-RateLimit-Reset')
                if reset_timestamp:
                    self.rate_limit_reset = datetime.fromtimestamp(int(reset_timestamp))
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 1))
                    logger.warning(f"Rate limited, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(endpoint, params)  # Retry
                else:
                    logger.error(f"Spotify API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Spotify API request failed: {e}")
            return None
    
    async def search_tracks(self, query: str, limit: int = 10, market: str = "US") -> List[Dict]:
        """Search for tracks based on query"""
        try:
            params = {
                "q": query,
                "type": "track",
                "limit": min(limit, 50),  # Spotify max is 50
                "market": market
            }
            
            data = await self._make_request("/search", params)
            if data and "tracks" in data:
                tracks = data["tracks"]["items"]
                return [self._format_track(track) for track in tracks]
            
            return []
            
        except Exception as e:
            logger.error(f"Track search failed: {e}")
            return []
    
    async def get_recommendations(
        self, 
        mood: str, 
        limit: int = 5,
        seed_genres: List[str] = None,
        target_energy: float = None,
        target_valence: float = None
    ) -> List[Dict]:
        """Get track recommendations based on mood and audio features"""
        try:
            # Set default parameters based on mood
            mood_params = self._get_mood_parameters(mood)
            
            params = {
                "limit": min(limit, 100),  # Spotify max is 100
                "market": "US"
            }
            
            # Add seed genres
            if seed_genres:
                params["seed_genres"] = ",".join(seed_genres[:5])  # Max 5 seed genres
            else:
                params["seed_genres"] = ",".join(self.genre_mappings.get(mood, ['pop'])[:5])
            
            # Add audio features
            if target_energy is not None:
                params["target_energy"] = target_energy
            else:
                params["target_energy"] = mood_params["energy"]
            
            if target_valence is not None:
                params["target_valence"] = target_valence
            else:
                params["target_valence"] = mood_params["valence"]
            
            # Add other audio features
            params.update({
                "target_danceability": mood_params["danceability"],
                "target_acousticness": mood_params["acousticness"],
                "target_instrumentalness": mood_params["instrumentalness"],
                "target_liveness": mood_params["liveness"],
                "target_speechiness": mood_params["speechiness"]
            })
            
            data = await self._make_request("/recommendations", params)
            if data and "tracks" in data:
                tracks = data["tracks"]
                return [self._format_track(track) for track in tracks]
            
            return []
            
        except Exception as e:
            logger.error(f"Recommendations failed: {e}")
            return []
    
    async def get_track_features(self, track_id: str) -> Optional[Dict]:
        """Get audio features for a specific track"""
        try:
            data = await self._make_request(f"/audio-features/{track_id}")
            return data
        except Exception as e:
            logger.error(f"Track features failed: {e}")
            return None
    
    async def get_playlist_tracks(self, playlist_id: str, limit: int = 20) -> List[Dict]:
        """Get tracks from a specific playlist"""
        try:
            params = {"limit": min(limit, 100)}
            data = await self._make_request(f"/playlists/{playlist_id}/tracks", params)
            
            if data and "items" in data:
                tracks = []
                for item in data["items"]:
                    if "track" in item and item["track"]:
                        tracks.append(self._format_track(item["track"]))
                return tracks
            
            return []
        except Exception as e:
            logger.error(f"Playlist tracks failed: {e}")
            return []
    
    async def search_playlists(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for playlists"""
        try:
            params = {
                "q": query,
                "type": "playlist",
                "limit": min(limit, 50)
            }
            
            data = await self._make_request("/search", params)
            if data and "playlists" in data:
                playlists = data["playlists"]["items"]
                return [self._format_playlist(playlist) for playlist in playlists]
            
            return []
        except Exception as e:
            logger.error(f"Playlist search failed: {e}")
            return []
    
    def _get_mood_parameters(self, mood: str) -> Dict[str, float]:
        """Get audio feature parameters for specific mood"""
        mood_params = {
            'happy': {
                'energy': 0.8,
                'valence': 0.8,
                'danceability': 0.7,
                'acousticness': 0.3,
                'instrumentalness': 0.1,
                'liveness': 0.2,
                'speechiness': 0.1
            },
            'sad': {
                'energy': 0.3,
                'valence': 0.2,
                'danceability': 0.4,
                'acousticness': 0.7,
                'instrumentalness': 0.3,
                'liveness': 0.1,
                'speechiness': 0.1
            },
            'angry': {
                'energy': 0.2,
                'valence': 0.3,
                'danceability': 0.2,
                'acousticness': 0.8,
                'instrumentalness': 0.6,
                'liveness': 0.1,
                'speechiness': 0.05
            },
            'stressed': {
                'energy': 0.2,
                'valence': 0.4,
                'danceability': 0.3,
                'acousticness': 0.8,
                'instrumentalness': 0.7,
                'liveness': 0.1,
                'speechiness': 0.05
            },
            'neutral': {
                'energy': 0.5,
                'valence': 0.5,
                'danceability': 0.5,
                'acousticness': 0.5,
                'instrumentalness': 0.3,
                'liveness': 0.2,
                'speechiness': 0.1
            }
        }
        
        return mood_params.get(mood, mood_params['neutral'])
    
    def _format_track(self, track: Dict) -> Dict:
        """Format track data for our application"""
        try:
            artists = [artist["name"] for artist in track.get("artists", [])]
            album = track.get("album", {})
            
            return {
                "id": track.get("id"),
                "name": track.get("name"),
                "artists": artists,
                "artist": ", ".join(artists),
                "album": album.get("name"),
                "album_image": album.get("images", [{}])[0].get("url") if album.get("images") else None,
                "duration_ms": track.get("duration_ms"),
                "duration": self._format_duration(track.get("duration_ms", 0)),
                "preview_url": track.get("preview_url"),
                "external_urls": track.get("external_urls", {}),
                "spotify_url": track.get("external_urls", {}).get("spotify"),
                "popularity": track.get("popularity", 0),
                "explicit": track.get("explicit", False),
                "mood_affinity": 0.8  # Default, will be calculated based on audio features
            }
        except Exception as e:
            logger.error(f"Track formatting failed: {e}")
            return {}
    
    def _format_playlist(self, playlist: Dict) -> Dict:
        """Format playlist data for our application"""
        try:
            return {
                "id": playlist.get("id"),
                "name": playlist.get("name"),
                "description": playlist.get("description"),
                "owner": playlist.get("owner", {}).get("display_name"),
                "tracks_total": playlist.get("tracks", {}).get("total", 0),
                "image": playlist.get("images", [{}])[0].get("url") if playlist.get("images") else None,
                "external_urls": playlist.get("external_urls", {}),
                "spotify_url": playlist.get("external_urls", {}).get("spotify"),
                "public": playlist.get("public", False)
            }
        except Exception as e:
            logger.error(f"Playlist formatting failed: {e}")
            return {}
    
    def _format_duration(self, duration_ms: int) -> str:
        """Convert milliseconds to MM:SS format"""
        try:
            seconds = duration_ms // 1000
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes}:{seconds:02d}"
        except:
            return "0:00"
    
    async def get_mood_music(
        self, 
        mood: str, 
        limit: int = 5,
        include_playlists: bool = True
    ) -> Dict[str, Any]:
        """Get comprehensive music recommendations for a mood"""
        try:
            results = {
                "tracks": [],
                "playlists": [],
                "mood": mood,
                "source": "spotify",
                "timestamp": datetime.now().isoformat()
            }
            
            # Get track recommendations
            tracks = await self.get_recommendations(mood, limit)
            results["tracks"] = tracks
            
            # Get playlist recommendations if requested
            if include_playlists:
                mood_queries = self.mood_queries.get(mood, ["music"])
                for query in mood_queries[:2]:  # Limit to 2 queries
                    playlists = await self.search_playlists(f"{query} {mood}", 3)
                    results["playlists"].extend(playlists)
                    if len(results["playlists"]) >= 5:  # Limit total playlists
                        break
            
            # Remove duplicates
            seen_ids = set()
            results["tracks"] = [track for track in results["tracks"] if track.get("id") and track["id"] not in seen_ids and not seen_ids.add(track["id"])]
            results["playlists"] = [playlist for playlist in results["playlists"] if playlist.get("id") and playlist["id"] not in seen_ids and not seen_ids.add(playlist["id"])]
            
            return results
            
        except Exception as e:
            logger.error(f"Mood music generation failed: {e}")
            return {
                "tracks": [],
                "playlists": [],
                "mood": mood,
                "source": "fallback",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Spotify API health and credentials"""
        try:
            if not self.client_id or not self.client_secret:
                return {
                    "status": "error",
                    "message": "Spotify credentials not configured",
                    "configured": False
                }
            
            # Try to get access token
            token_success = await self.get_access_token()
            if not token_success:
                return {
                    "status": "error",
                    "message": "Failed to get access token",
                    "configured": True,
                    "authenticated": False
                }
            
            # Try a simple API call
            data = await self._make_request("/search", {"q": "test", "type": "track", "limit": 1})
            if data:
                return {
                    "status": "healthy",
                    "message": "Spotify API is working",
                    "configured": True,
                    "authenticated": True,
                    "rate_limit_remaining": self.rate_limit_remaining
                }
            else:
                return {
                    "status": "error",
                    "message": "API call failed",
                    "configured": True,
                    "authenticated": True
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Health check failed: {e}",
                "configured": bool(self.client_id and self.client_secret),
                "authenticated": False
            }

# Global Spotify service instance
spotify_service = SpotifyService()

async def get_spotify_music(mood: str, limit: int = 5) -> Dict[str, Any]:
    """Public function for getting Spotify music recommendations"""
    return await spotify_service.get_mood_music(mood, limit)

async def search_spotify_tracks(query: str, limit: int = 10) -> List[Dict]:
    """Public function for searching Spotify tracks"""
    return await spotify_service.search_tracks(query, limit)

async def get_spotify_health() -> Dict[str, Any]:
    """Public function for Spotify health check"""
    return await spotify_service.health_check()
