from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings
import structlog

logger = structlog.get_logger(__name__)

# Global database instance
_database: AsyncIOMotorDatabase = None

async def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance."""
    global _database
    if _database is None:
        await connect_to_mongo()
    return _database

async def connect_to_mongo():
    """Connect to MongoDB and set up indexes."""
    global _database
    
    client = AsyncIOMotorClient(settings.mongodb_uri)
    _database = client[settings.mongodb_db]
    
    # Test the connection
    try:
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error("Failed to connect to MongoDB", error=str(e))
        raise
    
    # Set up indexes
    await setup_indexes()
    
    return _database

async def setup_indexes():
    """Set up database indexes for optimal performance."""
    try:
        # Users collection indexes
        await _database.users.create_index("email", unique=True)
        await _database.users.create_index("user_id", unique=True)
        await _database.users.create_index("is_active")
        await _database.users.create_index("created_at")
        
        # User balances collection indexes
        await _database.user_balances.create_index("user_id", unique=True)
        await _database.user_balances.create_index("outstanding_amount")
        await _database.user_balances.create_index("available_credit")
        await _database.user_balances.create_index("credit_limit")
        
        # User bank collection indexes
        await _database.user_bank.create_index("user_id", unique=True)
        await _database.user_bank.create_index("balance")
        await _database.user_bank.create_index("last_transaction_at")
        
        # Merchants collection indexes
        await _database.merchants.create_index("email", unique=True)
        await _database.merchants.create_index("merchant_id", unique=True)
        await _database.merchants.create_index("is_active")
        await _database.merchants.create_index("current_fee_pct")
        await _database.merchants.create_index("wallet_balance")
        
        # Transactions collection indexes
        await _database.transactions.create_index("transaction_id", unique=True)
        await _database.transactions.create_index("user_id")
        await _database.transactions.create_index("merchant_id")
        await _database.transactions.create_index("type")
        await _database.transactions.create_index("created_at")
        await _database.transactions.create_index([("user_id", 1), ("type", 1)])
        await _database.transactions.create_index([("merchant_id", 1), ("type", 1)])
        
        # Auth users collection indexes
        await _database.auth_users.create_index("email", unique=True)
        await _database.auth_users.create_index("role")
        await _database.auth_users.create_index("is_active")
        await _database.auth_users.create_index("last_login")
        
        # Merchant wallets collection indexes
        await _database.merchant_wallets.create_index("merchant_id", unique=True)
        await _database.merchant_wallets.create_index("balance")
        await _database.merchant_wallets.create_index("last_transaction_at")
        
        # Credit limits collection indexes
        await _database.credit_limits.create_index("user_id", unique=True)
        await _database.credit_limits.create_index("available_credit")
        await _database.credit_limits.create_index("credit_limit")
        
        # Counters collection indexes
        await _database.counters.create_index("name", unique=True)
        
        # Idempotency keys collection indexes
        await _database.idempotency_keys.create_index("key", unique=True)
        await _database.idempotency_keys.create_index("expires_at")
        
        # Token blacklist collection indexes
        await _database.token_blacklist.create_index("token", unique=True)
        await _database.token_blacklist.create_index("expires_at")
        
        # Merchant fee history collection indexes
        await _database.merchant_fee_history.create_index("merchant_id")
        await _database.merchant_fee_history.create_index("created_at")
        
        # RBAC collections indexes
        await _database.roles.create_index("name", unique=True)
        await _database.permissions.create_index("name", unique=True)
        
        # Create user_roles index with explicit name to avoid conflicts
        try:
            await _database.user_roles.create_index(
                [("user_id", 1), ("role_id", 1)], 
                unique=True, 
                name="user_id_role_id_unique"
            )
        except Exception as e:
            if "already exists" not in str(e) and "IndexKeySpecsConflict" not in str(e):
                raise
        
        # Create role_permissions index with explicit name to avoid conflicts
        try:
            await _database.role_permissions.create_index(
                [("role_id", 1), ("permission_id", 1)], 
                unique=True, 
                name="role_id_permission_id_unique"
            )
        except Exception as e:
            if "already exists" not in str(e) and "IndexKeySpecsConflict" not in str(e):
                raise
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error("Failed to create database indexes", error=str(e))
        raise

async def close_mongo_connection():
    """Close the MongoDB connection."""
    global _database
    if _database is not None:
        client = _database.client
        client.close()
        _database = None
        logger.info("MongoDB connection closed")
