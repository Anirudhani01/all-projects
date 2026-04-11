"""
External APIs Package
Contains integrations for Spotify, YouTube, and ZenQuotes
"""

from .spotify_service import spotify_service, get_spotify_music, search_spotify_tracks, get_spotify_health
from .youtube_service import youtube_service, get_youtube_videos, search_youtube_videos, get_youtube_health
from .zenquotes_service import zenquotes_service, get_zenquotes, get_random_zenquotes, get_zenquotes_health
from .unified_api_service import unified_api_service, get_external_content, check_all_apis_health, get_apis_status, get_content_summary

__all__ = [
    # Spotify
    'spotify_service',
    'get_spotify_music',
    'search_spotify_tracks',
    'get_spotify_health',
    
    # YouTube
    'youtube_service',
    'get_youtube_videos',
    'search_youtube_videos',
    'get_youtube_health',
    
    # ZenQuotes
    'zenquotes_service',
    'get_zenquotes',
    'get_random_zenquotes',
    'get_zenquotes_health',
    
    # Unified
    'unified_api_service',
    'get_external_content',
    'check_all_apis_health',
    'get_apis_status',
    'get_content_summary'
]
