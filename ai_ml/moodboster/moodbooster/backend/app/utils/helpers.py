# Helper utility functions

from datetime import datetime
from typing import Dict, Any
import json

def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.utcnow()

def format_mood_confidence(confidence: float) -> str:
    """Format mood confidence as percentage"""
    return f"{round(confidence * 100, 1)}%"

def calculate_word_count(text: str) -> int:
    """Calculate word count in text"""
    return len(text.split())

def sanitize_text(text: str) -> str:
    """Basic text sanitization"""
    return text.strip()

def create_response_data(data: Dict[str, Any], message: str = "Success") -> Dict[str, Any]:
    """Create standardized API response"""
    return {
        "message": message,
        "data": data,
        "timestamp": get_current_timestamp().isoformat()
    }

def parse_json_safely(json_str: str) -> Dict[str, Any]:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str) if json_str else {}
    except json.JSONDecodeError:
        return {}
