import asyncio
import motor.motor_asyncio
from app.common.counters import CounterService, USER_ID_COUNTER, MERCHANT_ID_COUNTER

async def migrate_existing_records():
    """Migrate existing users and merchants to have custom IDs."""
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
        database = client.lazypay
        
        # Create counter service
        counter_service = CounterService(database)
        
        print("🔄 Migrating existing records to add custom IDs...")
        
        # Migrate existing users
        print("\n👥 Migrating Users:")
        users_collection = database.users
        users_without_custom_id = await users_collection.find({"custom_user_id": {"$exists": False}}).to_list(None)
        
        for user in users_without_custom_id:
            custom_user_id = await counter_service.get_next_id(USER_ID_COUNTER)
            await users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"custom_user_id": custom_user_id}}
            )
            print(f"   User {user['name']} ({user['email']}) -> custom_user_id: {custom_user_id}")
        
        # Migrate existing merchants
        print("\n🏪 Migrating Merchants:")
        merchants_collection = database.merchants
        merchants_without_custom_id = await merchants_collection.find({"custom_merchant_id": {"$exists": False}}).to_list(None)
        
        for merchant in merchants_without_custom_id:
            custom_merchant_id = await counter_service.get_next_id(MERCHANT_ID_COUNTER)
            await merchants_collection.update_one(
                {"_id": merchant["_id"]},
                {"$set": {"custom_merchant_id": custom_merchant_id}}
            )
            print(f"   Merchant {merchant['name']} -> custom_merchant_id: {custom_merchant_id}")
        
        # Verify migration
        print("\n📊 Verification:")
        total_users = await users_collection.count_documents({})
        users_with_custom_id = await users_collection.count_documents({"custom_user_id": {"$exists": True}})
        total_merchants = await merchants_collection.count_documents({})
        merchants_with_custom_id = await merchants_collection.count_documents({"custom_merchant_id": {"$exists": True}})
        
        print(f"   Users: {users_with_custom_id}/{total_users} have custom_user_id")
        print(f"   Merchants: {merchants_with_custom_id}/{total_merchants} have custom_merchant_id")
        
        print("\n✅ Migration completed successfully!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")

if __name__ == "__main__":
    asyncio.run(migrate_existing_records())
