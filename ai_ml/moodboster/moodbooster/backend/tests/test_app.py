#!/usr/bin/env python3
"""Test script to check if the app can be imported"""

try:
    from app.main import app
    print("✅ App imported successfully!")
    print("✅ Backend is ready to run!")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    import traceback
    traceback.print_exc()
