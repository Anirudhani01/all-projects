#!/usr/bin/env python3
"""
Test improved mood analyzer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.mood_analysis import analyze_mood

def test_improved_analyzer():
    """Test the improved mood analyzer"""
    
    test_cases = [
        "I'm very excited about my new job!",
        "I'm so happy today!",
        "I feel really sad and lonely right now.",
        "I'm absolutely furious about what happened!",
        "I'm so stressed and overwhelmed with work.",
        "Today was just okay, nothing special.",
        "I'm not happy at all, this is terrible!",
        "I feel completely devastated and broken.",
        "I'm extremely frustrated with this situation!",
        "I'm incredibly anxious about the future."
    ]
    
    print("🧪 Testing Improved Mood Analyzer")
    print("=" * 50)
    
    for i, text in enumerate(test_cases, 1):
        result = analyze_mood(text)
        print(f"{i:2d}. '{text}'")
        print(f"    Mood: {result.mood} | Confidence: {result.confidence:.3f} | Keywords: {result.keywords[:3]}")
        print()

if __name__ == "__main__":
    test_improved_analyzer()
