# Validation utilities

import re
from typing import List, Optional

def validate_mood_type(mood: str) -> bool:
    """Validate if mood type is valid"""
    valid_moods = ['happy', 'sad', 'angry', 'stressed', 'neutral']
    return mood.lower() in valid_moods

def validate_text_length(text: str, min_length: int = 1, max_length: int = 2000) -> bool:
    """Validate text length"""
    return min_length <= len(text.strip()) <= max_length

def validate_confidence_score(confidence: float) -> bool:
    """Validate confidence score is between 0 and 1"""
    return 0.0 <= confidence <= 1.0

def validate_session_id(session_id: str) -> bool:
    """Validate session ID format"""
    # UUID format validation
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, session_id, re.IGNORECASE))

def validate_rating(rating: int) -> bool:
    """Validate rating is between 1 and 5"""
    return 1 <= rating <= 5

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', text)
    return sanitized.strip()
