#!/usr/bin/env python3
"""
Test script for LLM-based mood analysis
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.llm_mood_analyzer import analyze_mood_with_llm
from app.services.mood_analysis import analyze_mood

async def test_llm_mood_analysis():
    """Test LLM-based mood analysis"""
    
    test_cases = [
        "I'm so excited about my new job! I can't wait to start tomorrow!",
        "I feel really sad and lonely right now. Nothing seems to be going right.",
        "I'm absolutely furious about what happened! This is completely unacceptable!",
        "I'm so stressed and overwhelmed with work. I don't know how I'll get everything done.",
        "Today was just okay, nothing special happened.",
        "I'm not happy at all, this is terrible! I wish things were different.",
        "I feel completely devastated and broken. I don't know how to move forward.",
        "I'm extremely frustrated with this situation! It's driving me crazy!",
        "I'm incredibly anxious about the future. I don't know what's going to happen.",
        "I'm feeling grateful and blessed today. Life is beautiful!"
    ]
    
    print("🧠 Testing LLM-based Mood Analysis")
    print("=" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i:2d}. Text: '{text}'")
        print("-" * 50)
        
        try:
            # Test LLM analysis
            result = await analyze_mood_with_llm(text)
            print(f"    LLM Result: {result.mood} (confidence: {result.confidence:.3f})")
            print(f"    Keywords: {result.keywords[:5]}")
            print(f"    Emotions: {result.emotions}")
            
        except Exception as e:
            print(f"    LLM Error: {e}")
            
            # Fallback to keyword analysis
            try:
                fallback_result = analyze_mood(text)
                print(f"    Fallback: {fallback_result.mood} (confidence: {fallback_result.confidence:.3f})")
            except Exception as e2:
                print(f"    Fallback Error: {e2}")
        
        print()

async def test_consistency():
    """Test consistency of LLM analysis"""
    print("\n🔄 Testing Consistency")
    print("=" * 30)
    
    test_text = "I'm so happy today! Everything is going great!"
    
    print(f"Testing: '{test_text}'")
    print("Running 3 times to check consistency...")
    
    results = []
    for i in range(3):
        try:
            result = await analyze_mood_with_llm(test_text)
            results.append((result.mood, result.confidence))
            print(f"  Run {i+1}: {result.mood} (confidence: {result.confidence:.3f})")
        except Exception as e:
            print(f"  Run {i+1}: Error - {e}")
            results.append(("error", 0.0))
    
    # Check consistency
    moods = [r[0] for r in results if r[0] != "error"]
    if len(set(moods)) == 1 and len(moods) > 0:
        print(f"✅ Consistent: All results show '{moods[0]}'")
    else:
        print(f"❌ Inconsistent: {set(moods)}")

async def main():
    """Main test function"""
    print("🚀 Starting LLM Mood Analysis Tests")
    print("=" * 60)
    
    await test_llm_mood_analysis()
    await test_consistency()
    
    print("\n✅ Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
