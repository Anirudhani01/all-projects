#!/usr/bin/env python3
"""
Quick start script for Employee Management System with SQLite
"""

import os
import sys

def main():
    """Run the SQLite version of the application"""
    print("🚀 Employee Management System - SQLite Version")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        "main_sqlite.py",
        "config_sqlite.py",
        "database.py",
        "models.py",
        "schemas.py",
        "crud.py",
        "logger.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        sys.exit(1)
    
    print("✅ All required files found")
    print("📁 Database: SQLite (employee_db.sqlite)")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("🔗 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    # Import and run the SQLite application
    try:
        from main_sqlite import app
        import uvicorn
        
        print("🚀 Starting server...")
        uvicorn.run(
            "main_sqlite:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
