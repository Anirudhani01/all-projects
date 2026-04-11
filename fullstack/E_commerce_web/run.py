#!/usr/bin/env python3
"""
Simple script to run the E-commerce FastAPI application
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting E-Commerce API Server...")
    print("📚 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Alternative docs at: http://localhost:8000/redoc")
    print("🏥 Health check at: http://localhost:8000/health")
    print("📊 Statistics at: http://localhost:8000/api/v1/stats")
    print("\n" + "="*50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
