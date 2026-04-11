#!/usr/bin/env python3
"""
Simple startup script for the E-commerce Backend
"""

import uvicorn
from app.config.settings import settings

if __name__ == "__main__":
    print("🚀 Starting E-commerce Backend...")
    print(f"📍 Server will run on http://{settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🔍 Health Check: http://{settings.host}:{settings.port}/health")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
