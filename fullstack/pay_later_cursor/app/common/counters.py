from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

logger = structlog.get_logger(__name__)


class CounterService:
    """Service for managing auto-increment counters."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.counters_collection = database.counters
    
    async def get_next_id(self, counter_name: str) -> int:
        """Get the next auto-increment ID for a given counter."""
        try:
            # Use findOneAndUpdate for atomic increment
            result = await self.counters_collection.find_one_and_update(
                {"_id": counter_name},
                {"$inc": {"sequence_value": 1}},
                upsert=True,
                return_document=True
            )
            
            if result and "sequence_value" in result:
                next_id = result["sequence_value"]
                logger.info(f"Generated next {counter_name} ID", counter_name=counter_name, next_id=next_id)
                return next_id
            else:
                # This should not happen with upsert=True, but just in case
                await self.counters_collection.update_one(
                    {"_id": counter_name},
                    {"$set": {"sequence_value": 1}},
                    upsert=True
                )
                logger.info(f"Initialized {counter_name} counter", counter_name=counter_name, next_id=1)
                return 1
                
        except Exception as e:
            logger.error(f"Error getting next {counter_name} ID", error=str(e))
            raise
    
    async def get_current_id(self, counter_name: str) -> int:
        """Get the current ID for a given counter without incrementing."""
        try:
            result = await self.counters_collection.find_one({"_id": counter_name})
            if result and "sequence_value" in result:
                return result["sequence_value"]
            return 0
        except Exception as e:
            logger.error(f"Error getting current {counter_name} ID", error=str(e))
            return 0
    
    async def reset_counter(self, counter_name: str, value: int = 0):
        """Reset a counter to a specific value."""
        try:
            await self.counters_collection.update_one(
                {"_id": counter_name},
                {"$set": {"sequence_value": value}},
                upsert=True
            )
            logger.info(f"Reset {counter_name} counter", counter_name=counter_name, value=value)
        except Exception as e:
            logger.error(f"Error resetting {counter_name} counter", error=str(e))
            raise


# Counter names
USER_ID_COUNTER = "user_id"
MERCHANT_ID_COUNTER = "merchant_id"
