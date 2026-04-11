"""
Unified API Service for External Integrations
Manages Spotify, YouTube, and ZenQuotes APIs with fallback handling
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.services.external_apis.spotify_service import spotify_service
from app.services.external_apis.youtube_service import youtube_service
from app.services.external_apis.zenquotes_service import zenquotes_service

logger = logging.getLogger(__name__)

class UnifiedAPIService:
    """
    Unified service for managing all external API integrations
    Provides fallback handling and intelligent content selection
    """
    
    def __init__(self):
        self.services = {
            'spotify': spotify_service,
            'youtube': youtube_service,
            'zenquotes': zenquotes_service
        }
        
        # Service priorities for different content types
        self.content_priorities = {
            'music': ['spotify', 'youtube'],
            'video': ['youtube', 'spotify'],
            'quote': ['zenquotes', 'spotify'],
            'story': ['youtube', 'zenquotes'],
            'meditation': ['youtube', 'spotify'],
            'game': ['youtube'],
            'activity': ['youtube', 'zenquotes']
        }
        
        # Fallback content for when all APIs fail
        self.fallback_content = {
            'music': {
                'title': 'Calming Music',
                'artist': 'Nature Sounds',
                'genre': 'ambient',
                'url': 'https://example.com/fallback-music',
                'source': 'fallback'
            },
            'video': {
                'title': 'Relaxing Video',
                'channel': 'Wellness Channel',
                'url': 'https://example.com/fallback-video',
                'source': 'fallback'
            },
            'quote': {
                'text': 'This too shall pass.',
                'author': 'Persian Proverb',
                'category': 'wisdom',
                'source': 'fallback'
            }
        }
    
    async def get_content_for_mood(
        self, 
        mood: str, 
        content_types: List[str],
        max_results_per_type: int = 3
    ) -> Dict[str, Any]:
        """
        Get content from all available APIs for a specific mood
        
        Args:
            mood: Target mood (happy, sad, angry, stressed, neutral)
            content_types: List of content types to fetch
            max_results_per_type: Maximum results per content type
            
        Returns:
            Dict containing content from all services
        """
        try:
            logger.info(f"🎵 Getting content for mood: {mood}")
            
            results = {
                'mood': mood,
                'content': {},
                'services_used': [],
                'services_failed': [],
                'timestamp': datetime.now().isoformat(),
                'success_rate': 0.0
            }
            
            # Track successful and failed services
            successful_services = 0
            total_services = 0
            
            # Get content for each type
            for content_type in content_types:
                logger.info(f"🔍 Fetching {content_type} content...")
                
                content_results = await self._get_content_by_type(
                    mood, content_type, max_results_per_type
                )
                
                results['content'][content_type] = content_results
                
                if content_results.get('success', False):
                    successful_services += 1
                    results['services_used'].extend(content_results.get('services_used', []))
                else:
                    results['services_failed'].extend(content_results.get('services_failed', []))
                
                total_services += 1
            
            # Calculate success rate
            if total_services > 0:
                results['success_rate'] = successful_services / total_services
            
            logger.info(f"✅ Content fetch completed (success rate: {results['success_rate']:.2f})")
            return results
            
        except Exception as e:
            logger.error(f"❌ Content fetch failed: {e}")
            return await self._get_fallback_content(mood, content_types)
    
    async def _get_content_by_type(
        self, 
        mood: str, 
        content_type: str, 
        max_results: int
    ) -> Dict[str, Any]:
        """Get content for a specific type using prioritized services"""
        try:
            # Get service priorities for this content type
            service_priorities = self.content_priorities.get(content_type, [])
            
            results = {
                'content_type': content_type,
                'mood': mood,
                'items': [],
                'services_used': [],
                'services_failed': [],
                'success': False,
                'source': 'mixed'
            }
            
            # Try each service in priority order
            for service_name in service_priorities:
                try:
                    service = self.services.get(service_name)
                    if not service:
                        continue
                    
                    # Get content from this service
                    content = await self._get_content_from_service(
                        service, service_name, mood, content_type, max_results
                    )
                    
                    if content and content.get('items'):
                        results['items'].extend(content['items'])
                        results['services_used'].append(service_name)
                        results['success'] = True
                        
                        # If we have enough content, break
                        if len(results['items']) >= max_results:
                            break
                    
                except Exception as e:
                    logger.warning(f"Service {service_name} failed: {e}")
                    results['services_failed'].append(service_name)
                    continue
            
            # If no services worked, use fallback
            if not results['success'] or not results['items']:
                fallback_content = self._get_fallback_content_for_type(content_type, mood)
                if fallback_content:
                    results['items'] = [fallback_content]
                    results['success'] = True
                    results['source'] = 'fallback'
            
            # Limit results
            results['items'] = results['items'][:max_results]
            
            return results
            
        except Exception as e:
            logger.error(f"Content type fetch failed: {e}")
            return {
                'content_type': content_type,
                'mood': mood,
                'items': [],
                'services_used': [],
                'services_failed': [],
                'success': False,
                'error': str(e)
            }
    
    async def _get_content_from_service(
        self, 
        service, 
        service_name: str, 
        mood: str, 
        content_type: str, 
        max_results: int
    ) -> Optional[Dict]:
        """Get content from a specific service"""
        try:
            if service_name == 'spotify':
                if content_type in ['music', 'meditation']:
                    return await service.get_mood_music(mood, max_results)
                elif content_type == 'quote':
                    # Spotify doesn't have quotes, skip
                    return None
            
            elif service_name == 'youtube':
                if content_type in ['video', 'story', 'meditation', 'game', 'activity']:
                    return await service.get_mood_videos(mood, max_results)
                elif content_type == 'music':
                    # YouTube can provide music videos
                    return await service.get_mood_videos(f"{mood} music", max_results)
            
            elif service_name == 'zenquotes':
                if content_type == 'quote':
                    quotes = await service.get_mood_quotes(mood, max_results)
                    return {
                        'items': quotes,
                        'source': 'zenquotes'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Service {service_name} content fetch failed: {e}")
            return None
    
    def _get_fallback_content_for_type(self, content_type: str, mood: str) -> Optional[Dict]:
        """Get fallback content for a specific type"""
        try:
            fallback = self.fallback_content.get(content_type, {})
            if not fallback:
                return None
            
            # Customize fallback content based on mood
            if content_type == 'quote':
                mood_quotes = {
                    'happy': {"text": "Happiness is not something ready made. It comes from your own actions.", "author": "Dalai Lama"},
                    'sad': {"text": "This too shall pass.", "author": "Persian Proverb"},
                    'angry': {"text": "For every minute you remain angry, you give up sixty seconds of peace of mind.", "author": "Ralph Waldo Emerson"},
                    'stressed': {"text": "The present moment is the only time over which we have dominion.", "author": "Thích Nhất Hạnh"},
                    'neutral': {"text": "The journey of a thousand miles begins with one step.", "author": "Lao Tzu"}
                }
                return mood_quotes.get(mood, fallback)
            
            return fallback
            
        except Exception as e:
            logger.error(f"Fallback content generation failed: {e}")
            return None
    
    async def _get_fallback_content(self, mood: str, content_types: List[str]) -> Dict[str, Any]:
        """Get complete fallback content when all APIs fail"""
        try:
            results = {
                'mood': mood,
                'content': {},
                'services_used': [],
                'services_failed': ['spotify', 'youtube', 'zenquotes'],
                'timestamp': datetime.now().isoformat(),
                'success_rate': 0.0,
                'fallback_mode': True
            }
            
            for content_type in content_types:
                fallback_content = self._get_fallback_content_for_type(content_type, mood)
                results['content'][content_type] = {
                    'content_type': content_type,
                    'mood': mood,
                    'items': [fallback_content] if fallback_content else [],
                    'services_used': [],
                    'services_failed': ['spotify', 'youtube', 'zenquotes'],
                    'success': bool(fallback_content),
                    'source': 'fallback'
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Complete fallback failed: {e}")
            return {
                'mood': mood,
                'content': {},
                'services_used': [],
                'services_failed': ['spotify', 'youtube', 'zenquotes'],
                'timestamp': datetime.now().isoformat(),
                'success_rate': 0.0,
                'fallback_mode': True,
                'error': str(e)
            }
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Check health of all external APIs"""
        try:
            health_results = {
                'timestamp': datetime.now().isoformat(),
                'services': {},
                'overall_status': 'healthy',
                'healthy_services': 0,
                'total_services': 0
            }
            
            # Check each service
            for service_name, service in self.services.items():
                try:
                    health = await service.health_check()
                    health_results['services'][service_name] = health
                    health_results['total_services'] += 1
                    
                    if health.get('status') == 'healthy':
                        health_results['healthy_services'] += 1
                    
                except Exception as e:
                    health_results['services'][service_name] = {
                        'status': 'error',
                        'message': str(e),
                        'configured': False
                    }
                    health_results['total_services'] += 1
            
            # Determine overall status
            if health_results['healthy_services'] == 0:
                health_results['overall_status'] = 'error'
            elif health_results['healthy_services'] < health_results['total_services']:
                health_results['overall_status'] = 'degraded'
            
            return health_results
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'services': {},
                'overall_status': 'error',
                'healthy_services': 0,
                'total_services': 0,
                'error': str(e)
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get detailed status of all services"""
        try:
            status = {
                'spotify': {
                    'configured': bool(spotify_service.client_id and spotify_service.client_secret),
                    'authenticated': spotify_service.access_token is not None,
                    'rate_limit_remaining': spotify_service.rate_limit_remaining
                },
                'youtube': {
                    'configured': bool(youtube_service.api_key),
                    'rate_limit_remaining': youtube_service.rate_limit_remaining
                },
                'zenquotes': {
                    'configured': True,  # No API key required
                    'rate_limit_remaining': zenquotes_service.rate_limit_remaining
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Service status check failed: {e}")
            return {}
    
    async def get_content_summary(self, mood: str) -> Dict[str, Any]:
        """Get a summary of available content for a mood"""
        try:
            # Get sample content from each service
            content_types = ['music', 'video', 'quote']
            content = await self.get_content_for_mood(mood, content_types, 1)
            
            summary = {
                'mood': mood,
                'available_content': {},
                'services_available': len(content.get('services_used', [])),
                'success_rate': content.get('success_rate', 0.0)
            }
            
            for content_type, content_data in content.get('content', {}).items():
                items = content_data.get('items', [])
                summary['available_content'][content_type] = {
                    'count': len(items),
                    'sources': content_data.get('services_used', []),
                    'success': content_data.get('success', False)
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Content summary failed: {e}")
            return {
                'mood': mood,
                'available_content': {},
                'services_available': 0,
                'success_rate': 0.0,
                'error': str(e)
            }

# Global unified API service instance
unified_api_service = UnifiedAPIService()

async def get_external_content(mood: str, content_types: List[str], max_results: int = 3) -> Dict[str, Any]:
    """Public function for getting external content"""
    return await unified_api_service.get_content_for_mood(mood, content_types, max_results)

async def check_all_apis_health() -> Dict[str, Any]:
    """Public function for checking all APIs health"""
    return await unified_api_service.health_check_all()

async def get_apis_status() -> Dict[str, Any]:
    """Public function for getting APIs status"""
    return await unified_api_service.get_service_status()

async def get_content_summary(mood: str) -> Dict[str, Any]:
    """Public function for getting content summary"""
    return await unified_api_service.get_content_summary(mood)
