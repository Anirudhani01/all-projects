#!/usr/bin/env python3
"""
Test script to verify main app import with wallet router.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
    print("✅ Main app imports successfully with wallet router")
    
    # Check if wallet router is included
    wallet_routes = [route for route in app.routes if "wallet" in str(route.path)]
    print(f"✅ Found {len(wallet_routes)} wallet routes in main app")
    
    # List wallet routes
    for route in wallet_routes:
        print(f"  - {route.methods} {route.path}")
        
except Exception as e:
    print(f"❌ Main app import failed: {e}")
    import traceback
    traceback.print_exc()
