"""
Database connection and configuration using Motor for async MongoDB operations.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging
from .config import DATABASE_CONFIG

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Connect to MongoDB database."""
        try:
            # Create Motor client
            self.client = AsyncIOMotorClient(
                DATABASE_CONFIG["url"],
                maxPoolSize=DATABASE_CONFIG["max_pool_size"],
                minPoolSize=DATABASE_CONFIG["min_pool_size"],
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
            )
            
            # Get database instance
            self.database = self.client[DATABASE_CONFIG["database"]]
            
            # Test connection
            await self.client.admin.command('ping')
            
            logger.info(f"Connected to MongoDB database: {DATABASE_CONFIG['database']}")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB database."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance."""
        try:
            # Users collection indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("phone")
            await self.database.users.create_index("created_at")
            await self.database.users.create_index("role")
            
            # Credit limits collection indexes
            await self.database.credit_limits.create_index("user_id")
            await self.database.credit_limits.create_index("approval_status")
            await self.database.credit_limits.create_index([("user_id", 1), ("created_at", -1)])
            
            # Transactions collection indexes
            await self.database.transactions.create_index("user_id")
            await self.database.transactions.create_index("merchant_id")
            await self.database.transactions.create_index("status")
            await self.database.transactions.create_index("transaction_type")
            await self.database.transactions.create_index([("user_id", 1), ("created_at", -1)])
            await self.database.transactions.create_index([("merchant_id", 1), ("created_at", -1)])
            
            # Merchants collection indexes
            await self.database.merchants.create_index("email", unique=True)
            await self.database.merchants.create_index("is_active")
            await self.database.merchants.create_index("business_type")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database."""
        if not self.database:
            raise RuntimeError("Database not connected")
        return self.database[collection_name]


# Create database instance
database = Database()


# Dependency to get database instance
async def get_database() -> Database:
    """Get database instance for dependency injection."""
    return database


# Dependency to get specific collection
async def get_collection(collection_name: str):
    """Get a specific collection for dependency injection."""
    return database.get_collection(collection_name)
