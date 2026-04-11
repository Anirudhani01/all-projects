from app.schemas.booster import BoosterResponse
from typing import Dict, Any

def get_booster_for_mood(mood: str) -> Dict[str, Any]:
    """
    Get personalized booster content based on mood
    In production, this would fetch from database
    """
    boosters = {
        'happy': {
            'title': "Keep the Joy Going! 🎉",
            'content': "You're radiating positivity! Here's something to amplify that happiness:",
            'type': 'game',
            'action': "Play a fun memory game to keep your spirits high!",
            'booster_metadata': {
                'game_type': 'memory',
                'difficulty': 'easy',
                'duration': '5 minutes'
            }
        },
        'sad': {
            'title': "Gentle Comfort 💙",
            'content': "I understand you're going through a tough time. Here's something gentle to help:",
            'type': 'story',
            'action': "Read a comforting story about hope and healing.",
            'booster_metadata': {
                'story_type': 'healing',
                'duration': '3 minutes',
                'theme': 'hope'
            }
        },
        'angry': {
            'title': "Release & Relax 🔥",
            'content': "It's okay to feel angry. Let's channel that energy positively:",
            'type': 'meditation',
            'action': "Try this breathing exercise to help you feel calmer.",
            'booster_metadata': {
                'meditation_type': 'breathing',
                'duration': '5 minutes',
                'focus': 'release'
            }
        },
        'stressed': {
            'title': "Find Your Calm 🌸",
            'content': "Stress can be overwhelming. Let's help you find some peace:",
            'type': 'meditation',
            'action': "Practice this mindfulness exercise.",
            'booster_metadata': {
                'meditation_type': 'mindfulness',
                'duration': '10 minutes',
                'focus': 'calm'
            }
        },
        'neutral': {
            'title': "Mindful Moment 🌱",
            'content': "Sometimes a neutral mood is perfect for reflection:",
            'type': 'activity',
            'action': "Try this gratitude exercise to brighten your perspective.",
            'booster_metadata': {
                'activity_type': 'gratitude',
                'duration': '5 minutes',
                'focus': 'reflection'
            }
        }
    }
    
    return boosters.get(mood, boosters['neutral'])
