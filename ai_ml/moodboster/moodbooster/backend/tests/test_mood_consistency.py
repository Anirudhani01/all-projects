#!/usr/bin/env python3
"""
Test script to verify mood analysis consistency
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.mood_analysis import analyze_mood

def test_consistency():
    """Test mood analysis consistency with the same inputs"""
    
    test_cases = [
        "I'm so happy today! Everything is going great!",
        "I feel really sad and lonely right now.",
        "I'm absolutely furious about what happened!",
        "I'm so stressed and overwhelmed with work.",
        "Today was just okay, nothing special.",
        "I'm not happy at all, this is terrible!",
        "I'm very excited about my new job!",
        "I feel completely devastated and broken.",
        "I'm extremely frustrated with this situation!",
        "I'm incredibly anxious about the future."
    ]
    
    print("🧪 Testing Mood Analysis Consistency")
    print("=" * 50)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: '{text}'")
        print("-" * 40)
        
        # Run analysis multiple times to check consistency
        results = []
        for run in range(5):
            result = analyze_mood(text)
            results.append((result.mood, result.confidence))
        
        # Check if all results are the same
        moods = [r[0] for r in results]
        confidences = [r[1] for r in results]
        
        mood_consistent = len(set(moods)) == 1
        confidence_consistent = all(abs(c - confidences[0]) < 0.01 for c in confidences)
        
        print(f"Results: {results}")
        print(f"Mood consistent: {'✅' if mood_consistent else '❌'}")
        print(f"Confidence consistent: {'✅' if confidence_consistent else '❌'}")
        
        if mood_consistent and confidence_consistent:
            print(f"✅ PASS - Mood: {moods[0]}, Confidence: {confidences[0]:.3f}")
        else:
            print(f"❌ FAIL - Inconsistent results detected!")
    
    print("\n" + "=" * 50)
    print("🎯 Consistency Test Complete!")

if __name__ == "__main__":
    test_consistency()
