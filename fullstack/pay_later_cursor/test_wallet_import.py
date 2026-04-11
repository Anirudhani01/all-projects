#!/usr/bin/env python3
"""
Test script to check wallet router import.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.api.routers.wallet import router
    print("✅ Wallet router imports successfully")
    print(f"Router prefix: {router.prefix}")
    print(f"Router tags: {router.tags}")
    print(f"Number of routes: {len(router.routes)}")
    
    # List all routes
    for route in router.routes:
        print(f"  - {route.methods} {route.path}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
