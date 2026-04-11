#!/usr/bin/env python3
"""
Debug script to test imports step by step.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import(module_name, description):
    """Test importing a module."""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except Exception as e:
        print(f"❌ {description}: {module_name} - {e}")
        return False

def test_from_import(module_name, import_name, description):
    """Test importing a specific item from a module."""
    try:
        module = __import__(module_name, fromlist=[import_name])
        getattr(module, import_name)
        print(f"✅ {description}: from {module_name} import {import_name}")
        return True
    except Exception as e:
        print(f"❌ {description}: from {module_name} import {import_name} - {e}")
        return False

print("🔍 Testing imports step by step...\n")

# Test basic modules
test_import("app.common.types", "Common types")
test_import("app.common.exceptions", "Common exceptions")
test_import("app.db.mongo", "MongoDB connection")

# Test wallet modules
test_import("app.modules.wallet.models", "Wallet models")
test_import("app.modules.wallet.schemas", "Wallet schemas")
test_import("app.modules.wallet.repository", "Wallet repository")
test_import("app.modules.wallet.service", "Wallet service")

# Test specific imports
test_from_import("app.common.types", "UserRole", "UserRole enum")
test_from_import("app.common.exceptions", "InsufficientBalance", "InsufficientBalance exception")
test_from_import("app.modules.wallet.schemas", "AddToWalletRequest", "AddToWalletRequest schema")

# Test auth dependencies
test_import("app.auth.dependencies", "Auth dependencies")

print("\n🔍 Testing wallet router import...")

try:
    from app.api.routers.wallet import router
    print("✅ Wallet router imports successfully")
    print(f"Router prefix: {router.prefix}")
    print(f"Router tags: {router.tags}")
    print(f"Number of routes: {len(router.routes)}")
    
    # List all routes
    for route in router.routes:
        print(f"  - {route.methods} {route.path}")
        
except Exception as e:
    print(f"❌ Wallet router import failed: {e}")
    import traceback
    traceback.print_exc()
