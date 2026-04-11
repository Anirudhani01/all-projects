#!/usr/bin/env python3
"""
Test the MoodBooster API
"""

import requests
import json

def test_api():
    """Test the MoodBooster API endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MoodBooster API")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return
    
    # Test diary entry endpoint
    test_entries = [
        "I'm so happy today! Everything is going great!",
        "I feel really sad and lonely right now.",
        "I'm absolutely furious about what happened!",
        "I'm so stressed and overwhelmed with work.",
        "Today was just okay, nothing special."
    ]
    
    print("\n📝 Testing Diary Entry Analysis:")
    print("-" * 40)
    
    for i, text in enumerate(test_entries, 1):
        try:
            payload = {"text": text}
            response = requests.post(
                f"{base_url}/api/v1/diary/entry",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"{i}. '{text[:30]}...'")
                print(f"   Mood: {result['mood']} | Confidence: {result['confidence']:.3f}")
                print(f"   Booster: {result['booster']['title']}")
                print()
            else:
                print(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api()
