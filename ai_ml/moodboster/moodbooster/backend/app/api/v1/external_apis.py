"""
External APIs API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.database import get_db
from app.services.external_apis import (
    get_spotify_music, get_youtube_videos, get_zenquotes,
    get_external_content, check_all_apis_health, get_apis_status
)
from app.services.enhanced_content_generators import (
    generate_enhanced_content, get_enhanced_api_stats, check_enhanced_api_health
)

router = APIRouter()

@router.get("/health")
async def check_external_apis_health():
    """
    Check health of all external APIs
    """
    try:
        health_data = await check_all_apis_health()
        return health_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/status")
async def get_external_apis_status():
    """
    Get detailed status of all external APIs
    """
    try:
        status_data = await get_apis_status()
        return status_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.get("/stats")
async def get_external_apis_stats():
    """
    Get usage statistics for external APIs
    """
    try:
        stats_data = await get_enhanced_api_stats()
        return stats_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@router.post("/content/music")
async def get_music_recommendations(
    mood: str,
    limit: int = 5,
    include_playlists: bool = True
):
    """
    Get music recommendations from Spotify
    """
    try:
        music_data = await get_spotify_music(mood, limit)
        return {
            "mood": mood,
            "music": music_data,
            "source": "spotify"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Music recommendations failed: {str(e)}")

@router.post("/content/videos")
async def get_video_recommendations(
    mood: str,
    max_results: int = 5,
    include_playlists: bool = True
):
    """
    Get video recommendations from YouTube
    """
    try:
        video_data = await get_youtube_videos(mood, max_results)
        return {
            "mood": mood,
            "videos": video_data,
            "source": "youtube"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video recommendations failed: {str(e)}")

@router.post("/content/quotes")
async def get_quote_recommendations(
    mood: str,
    count: int = 3
):
    """
    Get inspirational quotes from ZenQuotes
    """
    try:
        quotes_data = await get_zenquotes(mood, count)
        return {
            "mood": mood,
            "quotes": quotes_data,
            "source": "zenquotes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quote recommendations failed: {str(e)}")

@router.post("/content/unified")
async def get_unified_content(
    mood: str,
    content_types: List[str],
    max_results_per_type: int = 3
):
    """
    Get content from all available external APIs
    """
    try:
        content_data = await get_external_content(mood, content_types, max_results_per_type)
        return content_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unified content failed: {str(e)}")

@router.post("/content/enhanced")
async def get_enhanced_content(
    content_type: str,
    mood: str,
    context: Optional[Dict] = None,
    themes: Optional[Dict] = None,
    user_preferences: Optional[Dict] = None
):
    """
    Get enhanced content using external APIs with fallback
    """
    try:
        content = await generate_enhanced_content(
            content_type, mood, context, themes, user_preferences
        )
        return content.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced content failed: {str(e)}")

@router.get("/spotify/health")
async def check_spotify_health():
    """
    Check Spotify API health specifically
    """
    try:
        from app.services.external_apis.spotify_service import get_spotify_health
        health_data = await get_spotify_health()
        return health_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spotify health check failed: {str(e)}")

@router.get("/youtube/health")
async def check_youtube_health():
    """
    Check YouTube API health specifically
    """
    try:
        from app.services.external_apis.youtube_service import get_youtube_health
        health_data = await get_youtube_health()
        return health_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube health check failed: {str(e)}")

@router.get("/zenquotes/health")
async def check_zenquotes_health():
    """
    Check ZenQuotes API health specifically
    """
    try:
        from app.services.external_apis.zenquotes_service import get_zenquotes_health
        health_data = await get_zenquotes_health()
        return health_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ZenQuotes health check failed: {str(e)}")

@router.get("/content-types")
async def get_available_content_types():
    """
    Get available content types and their external API support
    """
    return {
        "content_types": [
            {
                "type": "quote",
                "external_apis": ["zenquotes"],
                "fallback_available": True,
                "description": "Inspirational quotes and wisdom"
            },
            {
                "type": "music",
                "external_apis": ["spotify", "youtube"],
                "fallback_available": True,
                "description": "Music recommendations and playlists"
            },
            {
                "type": "video",
                "external_apis": ["youtube"],
                "fallback_available": True,
                "description": "Video content and recommendations"
            },
            {
                "type": "story",
                "external_apis": ["youtube"],
                "fallback_available": True,
                "description": "Story content and narratives"
            },
            {
                "type": "meditation",
                "external_apis": ["youtube", "spotify"],
                "fallback_available": True,
                "description": "Meditation and mindfulness content"
            },
            {
                "type": "game",
                "external_apis": ["youtube"],
                "fallback_available": True,
                "description": "Interactive games and puzzles"
            },
            {
                "type": "activity",
                "external_apis": ["youtube"],
                "fallback_available": True,
                "description": "Physical and creative activities"
            }
        ],
        "external_apis": [
            {
                "name": "spotify",
                "description": "Music streaming and recommendations",
                "free_tier": True,
                "rate_limits": "1000 requests per hour",
                "content_types": ["music"]
            },
            {
                "name": "youtube",
                "description": "Video content and recommendations",
                "free_tier": True,
                "rate_limits": "10000 requests per day",
                "content_types": ["video", "story", "meditation", "game", "activity"]
            },
            {
                "name": "zenquotes",
                "description": "Inspirational quotes and wisdom",
                "free_tier": True,
                "rate_limits": "1000 requests per hour",
                "content_types": ["quote"]
            }
        ]
    }

@router.get("/configuration")
async def get_api_configuration():
    """
    Get current API configuration status
    """
    try:
        from app.config import settings
        
        return {
            "external_apis_enabled": getattr(settings, 'use_external_apis', True),
            "fallback_enabled": getattr(settings, 'api_fallback_enabled', True),
            "rate_limit_buffer": getattr(settings, 'api_rate_limit_buffer', 10),
            "spotify_configured": bool(getattr(settings, 'spotify_client_id', None) and getattr(settings, 'spotify_client_secret', None)),
            "youtube_configured": bool(getattr(settings, 'youtube_api_key', None)),
            "zenquotes_enabled": getattr(settings, 'zenquotes_enabled', True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration retrieval failed: {str(e)}")

@router.post("/test/{api_name}")
async def test_external_api(api_name: str, mood: str = "happy"):
    """
    Test a specific external API with sample data
    """
    try:
        if api_name == "spotify":
            result = await get_spotify_music(mood, 2)
        elif api_name == "youtube":
            result = await get_youtube_videos(mood, 2)
        elif api_name == "zenquotes":
            result = await get_zenquotes(mood, 2)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown API: {api_name}")
        
        return {
            "api_name": api_name,
            "mood": mood,
            "test_result": result,
            "success": bool(result and (result.get('tracks') or result.get('videos') or result))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API test failed: {str(e)}")
