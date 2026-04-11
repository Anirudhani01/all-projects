from motor.motor_asyncio import AsyncIOMotorClient
from .settings import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    database = None


async def connect_to_mongo():
    """Create database connection."""
    try:
        Database.client = AsyncIOMotorClient(settings.mongodb_url)
        Database.database = Database.client[settings.database_name]
        
        # Test the connection
        await Database.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection."""
    if Database.client:
        Database.client.close()
        logger.info("MongoDB connection closed")


async def create_indexes():
    """Create database indexes for optimal performance."""
    try:
        # Products collection indexes
        await Database.database.products.create_index([("name", "text"), ("description", "text"), ("tags", "text")])
        await Database.database.products.create_index([("category", 1)])
        await Database.database.products.create_index([("material", 1)])
        await Database.database.products.create_index([("price", 1)])
        await Database.database.products.create_index([("rating", 1)])
        await Database.database.products.create_index([("isFeatured", 1)])
        
        # Users collection indexes
        await Database.database.users.create_index([("email", 1)], unique=True)
        
        # Reviews collection indexes
        await Database.database.reviews.create_index([("productId", 1)])
        await Database.database.reviews.create_index([("userId", 1)])
        
        # Wishlist collection indexes
        await Database.database.wishlist.create_index([("userId", 1), ("productId", 1)], unique=True)
        
        # Categories collection indexes
        await Database.database.categories.create_index([("slug", 1)], unique=True)
        await Database.database.categories.create_index([("name", "text")])
        await Database.database.categories.create_index([("isActive", 1)])
        await Database.database.categories.create_index([("isFeatured", 1)])
        await Database.database.categories.create_index([("sortOrder", 1)])
        
        # Subcategories collection indexes
        await Database.database.subcategories.create_index([("slug", 1), ("categoryId", 1)], unique=True)
        await Database.database.subcategories.create_index([("categoryId", 1)])
        await Database.database.subcategories.create_index([("isActive", 1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        raise


def get_database():
    """Get database instance."""
    return Database.database


def get_collection(collection_name: str):
    """Get collection instance."""
    if Database.database is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return Database.database[collection_name]
