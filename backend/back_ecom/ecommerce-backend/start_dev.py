#!/usr/bin/env python3
"""
Development startup script for the E-commerce Backend
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 Starting E-commerce Backend in Development Mode...")
    print("=" * 50)
    
    try:
        # Test import
        print("📦 Testing imports...")
        from app.main import app
        print("✅ All imports successful")
        
        # Show app info
        print(f"📍 FastAPI app created with {len(app.routes)} routes")
        print(f"📚 API Documentation will be available at /docs")
        print(f"🔍 Health Check will be available at /health")
        
        # Test basic functionality
        print("\n🧪 Testing basic functionality...")
        from app.config.settings import settings
        print(f"✅ Configuration loaded: {settings.host}:{settings.port}")
        
        print("\n🎯 Ready to start server!")
        print("=" * 50)
        
        # Start the server
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Check the error message above for details")
        sys.exit(1)

if __name__ == "__main__":
    main()
