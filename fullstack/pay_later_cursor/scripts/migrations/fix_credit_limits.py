#!/usr/bin/env python3
"""
Quick script to fix credit limits to 2000 for all users.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
import structlog

logger = structlog.get_logger(__name__)

async def fix_credit_limits():
    """Fix all credit limits to 2000."""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.mongodb_uri)
        database = client[settings.mongodb_db]
        
        # Test connection
        await client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Update all credit limits to 2000
        result = await database.user_balances.update_many(
            {"credit_limit": {"$ne": 2000.0}},
            {
                "$set": {
                    "credit_limit": 2000.0,
                    "available_credit": 2000.0,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"Updated {result.modified_count} user balance records")
        
        # Verify the fix
        incorrect_limits = await database.user_balances.find({
            "credit_limit": {"$ne": 2000.0}
        }).to_list(None)
        
        if incorrect_limits:
            logger.warning(f"Still found {len(incorrect_limits)} users with incorrect credit limits")
        else:
            logger.info("✅ All credit limits are now set to 2000!")
        
        # Close connection
        client.close()
        
    except Exception as e:
        logger.error(f"Failed to fix credit limits: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(fix_credit_limits())
