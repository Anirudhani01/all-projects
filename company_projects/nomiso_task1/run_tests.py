#!/usr/bin/env python3
"""
Simple script to run the shopping cart tests.
"""
import subprocess
import sys
import os

def main():
    """Run the test suite."""
    print("🚀 Starting Shopping Cart Backend Tests")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if requirements are installed
    try:
        import fastapi
        import pytest
        print("✅ Dependencies are installed")
    except ImportError:
        print("❌ Dependencies not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Initialize database
    print("🗄️  Initializing database...")
    try:
        from database.database import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    # Run tests
    print("🧪 Running tests...")
    print("=" * 50)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--cov=.",
        "--cov-report=term-missing"
    ])
    
    print("=" * 50)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
