"""
Content Generators for Decision Layer
Generates various types of content based on mood and context
"""

import logging
import random
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.schemas.decision import (
    QuoteContent, StoryContent, MeditationContent, MusicContent, 
    GameContent, ActivityContent, BreathingContent, GeneratedContent
)
import json

logger = logging.getLogger(__name__)

class ContentGenerator:
    """
    Base class for content generation
    """
    
    def __init__(self):
        self.generation_cache = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    async def generate_content(
        self, 
        content_type: str, 
        mood: str, 
        context: Optional[Dict] = None,
        themes: Optional[Dict] = None,
        user_preferences: Optional[Dict] = None
    ) -> GeneratedContent:
        """Generate content based on type and context"""
        try:
            # Check cache first
            cache_key = f"{content_type}_{mood}_{hash(str(context))}"
            if cache_key in self.generation_cache:
                cached_data = self.generation_cache[cache_key]
                if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_ttl:
                    return cached_data['content']
            
            # Generate new content
            if content_type == 'quote':
                content = await self._generate_quote(mood, context, themes)
            elif content_type == 'story':
                content = await self._generate_story(mood, context, themes)
            elif content_type == 'meditation':
                content = await self._generate_meditation(mood, context, themes)
            elif content_type == 'music':
                content = await self._generate_music(mood, context, themes)
            elif content_type == 'game':
                content = await self._generate_game(mood, context, themes)
            elif content_type == 'activity':
                content = await self._generate_activity(mood, context, themes)
            elif content_type == 'breathing':
                content = await self._generate_breathing(mood, context, themes)
            else:
                raise ValueError(f"Unknown content type: {content_type}")
            
            # Cache the result
            self.generation_cache[cache_key] = {
                'content': content,
                'timestamp': datetime.now().timestamp()
            }
            
            return content
            
        except Exception as e:
            logger.error(f"Content generation failed for {content_type}: {e}")
            return await self._get_fallback_content(content_type, mood)
    
    async def _generate_quote(self, mood: str, context: Optional[Dict], themes: Optional[Dict]) -> GeneratedContent:
        """Generate inspirational quote"""
        quotes_db = {
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
        
        mood_quotes = quotes_db.get(mood, quotes_db['neutral'])
        selected_quote = random.choice(mood_quotes)
        
        # Adjust based on themes if available
        if themes and themes.get('category_themes', {}).get('categories'):
            top_theme = max(themes['category_themes']['categories'].items(), key=lambda x: x[1]['score'])
            theme_category = top_theme[0]
            # Try to find a quote that matches the theme
            theme_quotes = [q for q in mood_quotes if theme_category in q.get('category', '')]
            if theme_quotes:
                selected_quote = random.choice(theme_quotes)
        
        quote_content = QuoteContent(
            text=selected_quote['text'],
            author=selected_quote['author'],
            category=selected_quote['category'],
            mood_affinity=self._calculate_mood_affinity(mood, selected_quote['category']),
            source="internal_database"
        )
        
        return GeneratedContent(
            content_type="quote",
            content=quote_content.dict(),
            metadata={
                "generation_method": "database_selection",
                "mood_target": mood,
                "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {}
            },
            generation_confidence=0.8,
            personalization_score=self._calculate_personalization_score(context, themes)
        )
    
    async def _generate_story(self, mood: str, context: Optional[Dict], themes: Optional[Dict]) -> GeneratedContent:
        """Generate short story"""
        story_templates = {
            'happy': {
                'title': "The Joyful Discovery",
                'genre': 'uplifting',
                'template': "Once upon a time, there was someone who discovered that {discovery}. This discovery brought them immense joy because {reason}. They shared this joy with others, and soon {outcome}. The moral of the story is that {lesson}."
            },
            'sad': {
                'title': "The Gentle Healing",
                'genre': 'healing',
                'template': "In a quiet moment, someone realized that {realization}. At first, it felt overwhelming, but then they remembered {memory}. Slowly, they began to {action}, and with each step, they felt {feeling}. This story reminds us that {lesson}."
            },
            'angry': {
                'title': "The Calm Within",
                'genre': 'calming',
                'template': "There was a moment when someone felt {emotion}. The world seemed {description}, but then they took a deep breath and {action}. They realized that {realization}, and slowly, {transformation}. This teaches us that {lesson}."
            },
            'stressed': {
                'title': "Finding Peace",
                'genre': 'mindful',
                'template': "In the midst of chaos, someone found a quiet space. They sat down and {action}. As they {process}, they noticed {observation}. Gradually, they felt {feeling}, and understood that {understanding}. This story shows that {lesson}."
            },
            'neutral': {
                'title': "A Moment of Reflection",
                'genre': 'contemplative',
                'template': "Someone paused in their day and noticed {observation}. They reflected on {reflection} and realized {realization}. This moment of {action} brought them {feeling}, and they learned that {lesson}."
            }
        }
        
        template = story_templates.get(mood, story_templates['neutral'])
        
        # Generate story content based on mood and themes
        story_content = self._fill_story_template(template, mood, themes)
        
        story_obj = StoryContent(
            title=story_content['title'],
            content=story_content['content'],
            genre=story_content['genre'],
            mood_affinity=self._calculate_mood_affinity(mood, story_content['genre']),
            estimated_reading_time=len(story_content['content'].split()) // 200 + 1,  # ~200 words per minute
            themes=self._extract_story_themes(story_content['content'])
        )
        
        return GeneratedContent(
            content_type="story",
            content=story_obj.dict(),
            metadata={
                "generation_method": "template_filling",
                "mood_target": mood,
                "word_count": len(story_content['content'].split()),
                "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {}
            },
            generation_confidence=0.7,
            personalization_score=self._calculate_personalization_score(context, themes)
        )
    
    async def _generate_meditation(self, mood: str, context: Optional[Dict], themes: Optional[Dict]) -> GeneratedContent:
        """Generate meditation content"""
        meditation_types = {
            'happy': {
                'title': "Gratitude Meditation",
                'type': 'gratitude',
                'description': "A meditation to amplify your positive feelings and cultivate gratitude",
                'instructions': [
                    "Find a comfortable seated position",
                    "Close your eyes and take three deep breaths",
                    "Think of three things you're grateful for today",
                    "Feel the warmth of gratitude in your heart",
                    "Send this positive energy to someone you care about",
                    "Take a moment to appreciate this feeling",
                    "Slowly return your awareness to the present"
                ]
            },
            'sad': {
                'title': "Compassionate Self-Care",
                'type': 'self_compassion',
                'description': "A gentle meditation to offer yourself kindness and understanding",
                'instructions': [
                    "Sit comfortably and close your eyes",
                    "Place your hand on your heart",
                    "Breathe naturally and feel your heartbeat",
                    "Repeat silently: 'May I be kind to myself'",
                    "Imagine wrapping yourself in a warm, loving light",
                    "Feel the comfort of your own compassion",
                    "When ready, gently open your eyes"
                ]
            },
            'angry': {
                'title': "Cooling Breath Meditation",
                'type': 'breathing',
                'description': "A breathing meditation to cool and calm your emotions",
                'instructions': [
                    "Sit upright with your spine straight",
                    "Close your eyes and relax your shoulders",
                    "Breathe in slowly through your nose for 4 counts",
                    "Hold your breath for 4 counts",
                    "Exhale slowly through your mouth for 6 counts",
                    "Repeat this cycle 5 times",
                    "Notice how your body feels calmer"
                ]
            },
            'stressed': {
                'title': "Body Scan Relaxation",
                'type': 'body_scan',
                'description': "A progressive relaxation to release tension and stress",
                'instructions': [
                    "Lie down or sit comfortably",
                    "Close your eyes and take a deep breath",
                    "Start at your toes and notice any tension",
                    "Breathe into that area and let it relax",
                    "Move slowly up through your body",
                    "Pay attention to your shoulders, neck, and face",
                    "Feel your entire body becoming more relaxed"
                ]
            },
            'neutral': {
                'title': "Mindful Awareness",
                'type': 'mindfulness',
                'description': "A simple meditation to cultivate present-moment awareness",
                'instructions': [
                    "Sit comfortably with your eyes closed",
                    "Notice your breath without changing it",
                    "When your mind wanders, gently return to your breath",
                    "Observe any thoughts or feelings without judgment",
                    "Stay present with whatever arises",
                    "When ready, slowly open your eyes"
                ]
            }
        }
        
        meditation = meditation_types.get(mood, meditation_types['neutral'])
        
        meditation_obj = MeditationContent(
            title=meditation['title'],
            description=meditation['description'],
            duration=len(meditation['instructions']) * 30,  # ~30 seconds per instruction
            type=meditation['type'],
            mood_affinity=self._calculate_mood_affinity(mood, meditation['type']),
            instructions=meditation['instructions']
        )
        
        return GeneratedContent(
            content_type="meditation",
            content=meditation_obj.dict(),
            metadata={
                "generation_method": "template_selection",
                "mood_target": mood,
                "duration_estimate": meditation_obj.duration,
                "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {}
            },
            generation_confidence=0.9,
            personalization_score=self._calculate_personalization_score(context, themes)
        )
    
    async def _generate_music(self, mood: str, context: Optional[Dict], themes: Optional[Dict]) -> GeneratedContent:
        """Generate music recommendations"""
        music_recommendations = {
            'happy': {
                'title': "Upbeat Playlist",
                'genre': 'pop',
                'description': "Energetic and uplifting songs to boost your mood",
                'suggestions': [
                    {"title": "Happy", "artist": "Pharrell Williams", "genre": "pop"},
                    {"title": "Good Vibrations", "artist": "The Beach Boys", "genre": "rock"},
                    {"title": "Don't Stop Me Now", "artist": "Queen", "genre": "rock"}
                ]
            },
            'sad': {
                'title': "Healing Melodies",
                'genre': 'indie',
                'description': "Gentle and comforting songs for difficult times",
                'suggestions': [
                    {"title": "Fix You", "artist": "Coldplay", "genre": "alternative"},
                    {"title": "Hallelujah", "artist": "Jeff Buckley", "genre": "folk"},
                    {"title": "Someone You Loved", "artist": "Lewis Capaldi", "genre": "pop"}
                ]
            },
            'angry': {
                'title': "Release and Relax",
                'genre': 'ambient',
                'description': "Calming instrumental music to help you process emotions",
                'suggestions': [
                    {"title": "Weightless", "artist": "Marconi Union", "genre": "ambient"},
                    {"title": "Clair de Lune", "artist": "Claude Debussy", "genre": "classical"},
                    {"title": "Spiegel im Spiegel", "artist": "Arvo Pärt", "genre": "minimalist"}
                ]
            },
            'stressed': {
                'title': "Calm and Focus",
                'genre': 'ambient',
                'description': "Peaceful music to help you relax and find center",
                'suggestions': [
                    {"title": "Rain Sounds", "artist": "Nature Sounds", "genre": "ambient"},
                    {"title": "Ocean Waves", "artist": "Relaxing Sounds", "genre": "nature"},
                    {"title": "Forest Birds", "artist": "Nature Sounds", "genre": "ambient"}
                ]
            },
            'neutral': {
                'title': "Balanced Vibes",
                'genre': 'indie',
                'description': "Thoughtful and balanced music for reflection",
                'suggestions': [
                    {"title": "The Scientist", "artist": "Coldplay", "genre": "alternative"},
                    {"title": "Mad World", "artist": "Gary Jules", "genre": "indie"},
                    {"title": "Breathe Me", "artist": "Sia", "genre": "pop"}
                ]
            }
        }
        
        music = music_recommendations.get(mood, music_recommendations['neutral'])
        selected_track = random.choice(music['suggestions'])
        
        music_obj = MusicContent(
            title=selected_track['title'],
            artist=selected_track['artist'],
            genre=selected_track['genre'],
            mood_affinity=self._calculate_mood_affinity(mood, selected_track['genre']),
            duration=random.randint(180, 300),  # 3-5 minutes
            preview_url=f"https://example.com/preview/{selected_track['title'].replace(' ', '_')}"
        )
        
        return GeneratedContent(
            content_type="music",
            content=music_obj.dict(),
            metadata={
                "generation_method": "database_selection",
                "mood_target": mood,
                "playlist_title": music['title'],
                "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {}
            },
            generation_confidence=0.8,
            personalization_score=self._calculate_personalization_score(context, themes)
        )
    
    async def _generate_game(self, mood: str, context: Optional[Dict], themes: Optional[Dict]) -> GeneratedContent:
        """Generate interactive game content"""
        game_types = {
            'happy': {
                'title': "Memory Celebration",
                'type': 'memory',
                'description': "A fun memory game to keep your positive energy flowing",
                'difficulty': 'easy',
                'instructions': [
                    "Look at the sequence of colors for 5 seconds",
                    "Try to repeat the sequence by clicking the colors",
                    "Each correct sequence adds a point",
                    "See how many levels you can complete!",
                    "Take breaks between levels to maintain focus"
                ]
            },
            'sad': {
                'title': "Gentle Puzzle",
                'type': 'puzzle',
                'description': "A calming puzzle to help you focus and feel accomplished",
                'difficulty': 'easy',
                'instructions': [
                    "Arrange the pieces to complete the peaceful image",
                    "Take your time - there's no rush",
                    "Focus on the beauty of each piece",
                    "Feel the satisfaction of each connection",
                    "Complete the puzzle at your own pace"
                ]
            },
            'angry': {
                'title': "Calm Focus Challenge",
                'type': 'focus',
                'description': "A concentration game to help channel your energy positively",
                'difficulty': 'medium',
                'instructions': [
                    "Follow the moving dot with your eyes",
                    "Breathe deeply as you track the movement",
                    "Count each successful tracking",
                    "Focus on the rhythm and flow",
                    "Feel your mind becoming calmer"
                ]
            },
            'stressed': {
                'title': "Mindful Matching",
                'type': 'matching',
                'description': "A relaxing matching game to help you unwind",
                'difficulty': 'easy',
                'instructions': [
                    "Find pairs of matching cards",
                    "Take deep breaths between moves",
                    "Don't worry about speed - focus on accuracy",
                    "Enjoy the peaceful images on the cards",
                    "Feel the stress melting away"
                ]
            },
            'neutral': {
                'title': "Reflection Trivia",
                'type': 'trivia',
                'description': "A thoughtful trivia game to engage your mind",
                'difficulty': 'medium',
                'instructions': [
                    "Answer questions about positive psychology",
                    "Think about each question carefully",
                    "Learn something new with each answer",
                    "Reflect on how the answers apply to your life",
                    "Enjoy the process of learning"
                ]
            }
        }
        
        game = game_types.get(mood, game_types['neutral'])
        
        game_obj = GameContent(
            title=game['title'],
            description=game['description'],
            type=game['type'],
            difficulty=game['difficulty'],
            estimated_duration=random.randint(5, 15),
            mood_affinity=self._calculate_mood_affinity(mood, game['type']),
            instructions=game['instructions'],
            interactive_elements=["click", "drag", "select", "timer"]
        )
        
        return GeneratedContent(
            content_type="game",
            content=game_obj.dict(),
            metadata={
                "generation_method": "template_selection",
                "mood_target": mood,
                "interaction_level": "high",
                "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {}
            },
            generation_confidence=0.8,
            personalization_score=self._calculate_personalization_score(context, themes)
        )
    
    async def _generate_activity(self, mood: str, context: Optional[Dict], themes: Optional[Dict]) -> GeneratedContent:
        """Generate activity suggestions"""
        activities = {
            'happy': {
                'title': "Joy Spreading Activity",
                'category': 'social',
                'description': "Share your positive energy with others",
                'materials': ["paper", "pen", "envelope", "stamp"],
                'instructions': [
                    "Write a heartfelt letter to someone you care about",
                    "Share a specific moment that made you happy today",
                    "Include a small drawing or doodle",
                    "Mail the letter or deliver it in person",
                    "Notice how sharing joy multiplies it"
                ],
                'benefits': ["connection", "gratitude", "creativity", "social_bonding"]
            },
            'sad': {
                'title': "Gentle Self-Care",
                'category': 'self_care',
                'description': "Nurture yourself with kindness and care",
                'materials': ["warm_water", "soap", "towel", "comfortable_clothes"],
                'instructions': [
                    "Prepare a warm, relaxing bath or shower",
                    "Use your favorite soap or bath products",
                    "Take your time and enjoy the warmth",
                    "Put on comfortable, cozy clothes afterward",
                    "Wrap yourself in a soft blanket and rest"
                ],
                'benefits': ["relaxation", "self_compassion", "physical_comfort", "emotional_healing"]
            },
            'angry': {
                'title': "Energy Release Exercise",
                'category': 'physical',
                'description': "Channel your energy into physical movement",
                'materials': ["comfortable_clothes", "water", "towel"],
                'instructions': [
                    "Put on comfortable workout clothes",
                    "Start with gentle stretching",
                    "Do jumping jacks or jog in place for 5 minutes",
                    "Punch a pillow or do shadow boxing",
                    "Finish with deep breathing and stretching"
                ],
                'benefits': ["stress_relief", "endorphin_release", "physical_health", "emotional_regulation"]
            },
            'stressed': {
                'title': "Mindful Organization",
                'category': 'productive',
                'description': "Create order and calm in your environment",
                'materials': ["organizing_containers", "labels", "cleaning_supplies"],
                'instructions': [
                    "Choose one small area to organize",
                    "Sort items into categories",
                    "Clean the space thoroughly",
                    "Arrange items in a pleasing way",
                    "Take a moment to appreciate the order"
                ],
                'benefits': ["control", "accomplishment", "mental_clarity", "environmental_peace"]
            },
            'neutral': {
                'title': "Creative Exploration",
                'category': 'creative',
                'description': "Engage your creativity and curiosity",
                'materials': ["art_supplies", "paper", "colored_pencils", "magazines"],
                'instructions': [
                    "Gather some art supplies",
                    "Create a collage about your current feelings",
                    "Don't worry about perfection - just express",
                    "Use colors that represent your mood",
                    "Reflect on what you've created"
                ],
                'benefits': ["creativity", "self_expression", "mindfulness", "emotional_awareness"]
            }
        }
        
        activity = activities.get(mood, activities['neutral'])
        
        activity_obj = ActivityContent(
            title=activity['title'],
            description=activity['description'],
            category=activity['category'],
            estimated_duration=random.randint(15, 45),
            mood_affinity=self._calculate_mood_affinity(mood, activity['category']),
            materials_needed=activity['materials'],
            instructions=activity['instructions'],
            benefits=activity['benefits']
        )
        
        return GeneratedContent(
            content_type="activity",
            content=activity_obj.dict(),
            metadata={
                "generation_method": "template_selection",
                "mood_target": mood,
                "category": activity['category'],
                "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {}
            },
            generation_confidence=0.9,
            personalization_score=self._calculate_personalization_score(context, themes)
        )
    
    async def _generate_breathing(self, mood: str, context: Optional[Dict], themes: Optional[Dict]) -> GeneratedContent:
        """Generate breathing exercise content"""
        breathing_exercises = {
            'happy': {
                'title': "Energy Breathing",
                'pattern': '4-4-4',
                'description': "A breathing exercise to channel your positive energy",
                'instructions': [
                    "Sit comfortably with your spine straight",
                    "Breathe in for 4 counts, feeling energy enter your body",
                    "Hold for 4 counts, letting the energy circulate",
                    "Breathe out for 4 counts, sharing energy with the world",
                    "Repeat 5 times, feeling more energized"
                ]
            },
            'sad': {
                'title': "Comforting Breath",
                'pattern': '4-7-8',
                'description': "A gentle breathing pattern to bring comfort and peace",
                'instructions': [
                    "Sit or lie down comfortably",
                    "Breathe in slowly for 4 counts",
                    "Hold your breath gently for 7 counts",
                    "Exhale slowly for 8 counts",
                    "Repeat 4 times, feeling more peaceful"
                ]
            },
            'angry': {
                'title': "Cooling Breath",
                'pattern': '4-4-6',
                'description': "A cooling breathing exercise to calm intense emotions",
                'instructions': [
                    "Sit upright and close your eyes",
                    "Inhale through your nose for 4 counts",
                    "Hold the breath for 4 counts",
                    "Exhale through your mouth for 6 counts",
                    "Repeat 6 times, feeling calmer each time"
                ]
            },
            'stressed': {
                'title': "Calming Breath",
                'pattern': '4-4-4',
                'description': "A simple breathing exercise to reduce stress and tension",
                'instructions': [
                    "Find a quiet, comfortable spot",
                    "Breathe in for 4 counts, expanding your belly",
                    "Hold for 4 counts, feeling the calm",
                    "Breathe out for 4 counts, releasing tension",
                    "Repeat 8 times, feeling more relaxed"
                ]
            },
            'neutral': {
                'title': "Mindful Breath",
                'pattern': 'natural',
                'description': "A simple mindfulness breathing exercise",
                'instructions': [
                    "Sit comfortably and close your eyes",
                    "Notice your natural breathing rhythm",
                    "Don't change it, just observe",
                    "When your mind wanders, return to your breath",
                    "Continue for 5 minutes, staying present"
                ]
            }
        }
        
        exercise = breathing_exercises.get(mood, breathing_exercises['neutral'])
        
        breathing_obj = BreathingContent(
            title=exercise['title'],
            description=exercise['description'],
            pattern=exercise['pattern'],
            duration=len(exercise['instructions']) * 30,  # ~30 seconds per instruction
            mood_affinity=self._calculate_mood_affinity(mood, exercise['pattern']),
            instructions=exercise['instructions']
        )
        
        return GeneratedContent(
            content_type="breathing",
            content=breathing_obj.dict(),
            metadata={
                "generation_method": "template_selection",
                "mood_target": mood,
                "pattern_type": exercise['pattern'],
                "theme_influence": themes.get('category_themes', {}).get('categories', {}) if themes else {}
            },
            generation_confidence=0.95,
            personalization_score=self._calculate_personalization_score(context, themes)
        )
    
    def _fill_story_template(self, template: Dict, mood: str, themes: Optional[Dict]) -> Dict:
        """Fill story template with appropriate content"""
        # This is a simplified version - in production, you'd use more sophisticated text generation
        story_elements = {
            'discovery': "something beautiful in their everyday life",
            'reason': "it reminded them of what truly matters",
            'outcome': "everyone around them felt the same joy",
            'lesson': "happiness is contagious and worth sharing",
            'realization': "they were stronger than they thought",
            'memory': "a time when they overcame a similar challenge",
            'action': "take small steps forward",
            'feeling': "a sense of hope growing within them",
            'emotion': "overwhelmed by frustration",
            'description': "unfair and chaotic",
            'transformation': "they found their inner strength",
            'observation': "the beauty in the small moments",
            'reflection': "what truly brings them peace",
            'understanding': "every challenge is an opportunity to grow"
        }
        
        content = template['template'].format(**story_elements)
        
        return {
            'title': template['title'],
            'content': content,
            'genre': template['genre']
        }
    
    def _extract_story_themes(self, content: str) -> List[str]:
        """Extract themes from story content"""
        # Simple theme extraction - in production, use NLP
        themes = []
        if 'joy' in content.lower() or 'happy' in content.lower():
            themes.append('joy')
        if 'strength' in content.lower() or 'courage' in content.lower():
            themes.append('strength')
        if 'peace' in content.lower() or 'calm' in content.lower():
            themes.append('peace')
        if 'hope' in content.lower() or 'future' in content.lower():
            themes.append('hope')
        return themes
    
    def _calculate_mood_affinity(self, mood: str, content_category: str) -> float:
        """Calculate how well content matches the target mood"""
        # Simple affinity calculation - in production, use more sophisticated matching
        base_affinity = 0.7
        
        mood_category_matches = {
            'happy': ['wisdom', 'purpose', 'gratitude', 'harmony', 'uplifting', 'pop', 'rock', 'social', 'creative'],
            'sad': ['understanding', 'hope', 'support', 'temporary', 'healing', 'indie', 'folk', 'self_care', 'healing'],
            'angry': ['peace', 'wisdom', 'letting_go', 'strength', 'calming', 'ambient', 'classical', 'physical', 'focus'],
            'stressed': ['strength', 'present', 'mindfulness', 'confidence', 'mindful', 'ambient', 'nature', 'productive', 'organization'],
            'neutral': ['progress', 'authenticity', 'life', 'passion', 'contemplative', 'indie', 'alternative', 'creative', 'exploration']
        }
        
        if content_category in mood_category_matches.get(mood, []):
            return min(1.0, base_affinity + 0.3)
        
        return base_affinity
    
    def _calculate_personalization_score(self, context: Optional[Dict], themes: Optional[Dict]) -> float:
        """Calculate how personalized the content is"""
        score = 0.0
        
        if context and context.get('enrichment_score', 0) > 0:
            score += 0.4
        
        if themes and themes.get('analysis_confidence', 0) > 0:
            score += 0.3
        
        if context and context.get('patterns', {}).get('patterns'):
            score += 0.3
        
        return min(1.0, score)
    
    async def _get_fallback_content(self, content_type: str, mood: str) -> GeneratedContent:
        """Provide fallback content when generation fails"""
        fallback_content = {
            'quote': {"text": "This too shall pass.", "author": "Persian Proverb", "category": "wisdom"},
            'story': {"title": "A Moment of Peace", "content": "In a quiet moment, you find peace within yourself.", "genre": "contemplative"},
            'meditation': {"title": "Simple Breathing", "description": "Focus on your breath and find calm.", "type": "breathing"},
            'music': {"title": "Calm Music", "artist": "Nature Sounds", "genre": "ambient"},
            'game': {"title": "Simple Focus", "description": "A gentle game to help you focus.", "type": "focus"},
            'activity': {"title": "Gentle Movement", "description": "Take a short walk or stretch gently.", "category": "physical"},
            'breathing': {"title": "Basic Breathing", "description": "Breathe in for 4, out for 4.", "pattern": "4-4"}
        }
        
        content = fallback_content.get(content_type, fallback_content['quote'])
        
        return GeneratedContent(
            content_type=content_type,
            content=content,
            metadata={"generation_method": "fallback", "mood_target": mood},
            generation_confidence=0.5,
            personalization_score=0.0
        )

# Global content generator instance
content_generator = ContentGenerator()

async def generate_content(
    content_type: str,
    mood: str,
    context: Optional[Dict] = None,
    themes: Optional[Dict] = None,
    user_preferences: Optional[Dict] = None
) -> GeneratedContent:
    """Public function for content generation"""
    return await content_generator.generate_content(content_type, mood, context, themes, user_preferences)
