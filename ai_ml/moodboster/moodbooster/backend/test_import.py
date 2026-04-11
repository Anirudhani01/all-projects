#!/usr/bin/env python3
"""
Test script to verify backend imports work correctly.
"""

try:
    import app.main
    print("✅ Backend imports successfully!")
except Exception as e:
    print(f"❌ Backend import failed: {e}")
    import traceback
    traceback.print_exc()
