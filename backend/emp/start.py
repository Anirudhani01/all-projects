#!/usr/bin/env python3
"""
Startup script for Employee Management System
"""

import subprocess
import sys
import os
from test_connection import main as test_connection


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def main():
    """Main startup function"""
    print("🚀 Employee Management System Startup")
    print("=" * 50)
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Exiting.")
        sys.exit(1)
    
    # Test database connection
    print("\n🔍 Testing database connection...")
    try:
        test_connection()
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        print("Please ensure MySQL is running and the database is properly configured.")
        sys.exit(1)
    
    # Start the application
    print("\n🚀 Starting Employee Management System...")
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")


if __name__ == "__main__":
    main()
