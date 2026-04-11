#!/usr/bin/env python3
"""
Test script to verify wallet API endpoints functionality.
"""

import asyncio
import sys
import os
import httpx
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import structlog

logger = structlog.get_logger(__name__)

# API base URL
BASE_URL = "http://localhost:8000/api/v1"


async def test_wallet_api_endpoints():
    """Test wallet API endpoints."""
    try:
        logger.info("🧪 Starting wallet API endpoint tests...")
        
        async with httpx.AsyncClient() as client:
            # Test 1: Health check
            logger.info("\n--- Test 1: Wallet Health Check ---")
            response = await client.get(f"{BASE_URL}/wallet/health")
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Health check passed: {health_data}")
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return
            
            # Test 2: Get wallet summary (should work without auth for testing)
            logger.info("\n--- Test 2: Wallet System Summary ---")
            response = await client.get(f"{BASE_URL}/wallet/summary")
            if response.status_code == 200:
                summary_data = response.json()
                logger.info(f"✅ Wallet summary: {summary_data}")
            else:
                logger.warning(f"⚠️ Wallet summary failed (expected without auth): {response.status_code}")
            
            # Test 3: Test API documentation
            logger.info("\n--- Test 3: API Documentation ---")
            response = await client.get("http://localhost:8000/docs")
            if response.status_code == 200:
                logger.info("✅ API documentation accessible")
            else:
                logger.warning(f"⚠️ API documentation not accessible: {response.status_code}")
            
            # Test 4: Test OpenAPI schema
            logger.info("\n--- Test 4: OpenAPI Schema ---")
            response = await client.get("http://localhost:8000/openapi.json")
            if response.status_code == 200:
                schema = response.json()
                # Check if wallet endpoints are in the schema
                wallet_paths = [path for path in schema.get("paths", {}).keys() if "wallet" in path]
                logger.info(f"✅ OpenAPI schema contains {len(wallet_paths)} wallet endpoints")
                for path in wallet_paths:
                    logger.info(f"   - {path}")
            else:
                logger.warning(f"⚠️ OpenAPI schema not accessible: {response.status_code}")
            
            logger.info("\n🎉 Wallet API endpoint tests completed!")
            
    except Exception as e:
        logger.error(f"❌ API test failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_server_running():
    """Check if the server is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code == 200:
                logger.info("✅ Server is running")
                return True
            else:
                logger.error(f"❌ Server health check failed: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Server not running: {str(e)}")
        return False


async def main():
    """Main test function."""
    logger.info("🚀 Starting wallet API tests...")
    
    # Check if server is running
    if not await test_server_running():
        logger.error("❌ Server is not running. Please start the server first:")
        logger.error("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Run API tests
    await test_wallet_api_endpoints()


if __name__ == "__main__":
    asyncio.run(main())
