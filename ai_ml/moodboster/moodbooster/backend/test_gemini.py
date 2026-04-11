#!/usr/bin/env python3
"""
Test script to check if Gemini API key is working
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.services.llm_mood_analyzer import analyze_mood_with_llm

async def test_gemini_api():
    """Test Gemini API integration"""
    print("🔑 Testing Gemini API Integration")
    print("=" * 50)
    
    # Check configuration
    print(f"✅ API Key present: {settings.gemini_api_key is not None and settings.gemini_api_key != 'your_gemini_api_key_here'}")
    print(f"✅ API Key length: {len(settings.gemini_api_key) if settings.gemini_api_key else 0}")
    print(f"✅ Gemini enabled: {settings.use_gemini}")
    print(f"✅ Ollama enabled: {settings.use_ollama}")
    print(f"✅ Keyword fallback: {settings.use_keyword_fallback}")
    print()
    
    # Test cases
    test_cases = [
        "I'm so happy today! Everything is going great!",
        "I feel really sad and lonely right now.",
        "I'm absolutely furious about what happened!",
        "I'm so stressed and overwhelmed with work.",
        "Today was just okay, nothing special happened."
    ]
    
    print("🧠 Testing Mood Analysis with LLM Integration")
    print("=" * 50)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Text: '{text}'")
        print("-" * 40)
        
        try:
            # Test LLM analysis
            result = await analyze_mood_with_llm(text)
            
            if result:
                print(f"   ✅ LLM Result: {result.mood} (confidence: {result.confidence:.3f})")
                print(f"   📝 Keywords: {result.keywords[:3]}")
                print(f"   🎭 Emotions: {dict(list(result.emotions.items())[:2])}")
            else:
                print("   ❌ LLM analysis failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Gemini API test completed!")

if __name__ == "__main__":
    asyncio.run(test_gemini_api())
