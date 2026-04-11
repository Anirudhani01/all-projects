import asyncio
import motor.motor_asyncio
from app.common.counters import CounterService, USER_ID_COUNTER, MERCHANT_ID_COUNTER

async def reset_counters_and_update_records():
    """Reset counters to 0 and update existing records to have sequential IDs starting from 1."""
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
        database = client.lazypay
        
        # Create counter service
        counter_service = CounterService(database)
        
        print("🔄 Resetting counters and updating existing records...")
        
        # Reset counters to 0
        print("\n📊 Resetting Counters:")
        await counter_service.reset_counter(USER_ID_COUNTER, 0)
        await counter_service.reset_counter(MERCHANT_ID_COUNTER, 0)
        print("   User counter reset to 0")
        print("   Merchant counter reset to 0")
        
        # Update existing users to have sequential IDs starting from 1
        print("\n👥 Updating Users:")
        users_collection = database.users
        users = await users_collection.find({}).sort("created_at", 1).to_list(None)  # Sort by creation date
        
        for i, user in enumerate(users, 1):
            await users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"custom_user_id": i}}
            )
            print(f"   User {user['name']} ({user['email']}) -> custom_user_id: {i}")
        
        # Update existing merchants to have sequential IDs starting from 1
        print("\n🏪 Updating Merchants:")
        merchants_collection = database.merchants
        merchants = await merchants_collection.find({}).sort("created_at", 1).to_list(None)  # Sort by creation date
        
        for i, merchant in enumerate(merchants, 1):
            await merchants_collection.update_one(
                {"_id": merchant["_id"]},
                {"$set": {"custom_merchant_id": i}}
            )
            print(f"   Merchant {merchant['name']} -> custom_merchant_id: {i}")
        
        # Update counters to reflect the current count
        print("\n📊 Updating Counters:")
        await counter_service.reset_counter(USER_ID_COUNTER, len(users))
        await counter_service.reset_counter(MERCHANT_ID_COUNTER, len(merchants))
        print(f"   User counter set to {len(users)}")
        print(f"   Merchant counter set to {len(merchants)}")
        
        # Verify the changes
        print("\n✅ Verification:")
        updated_users = await users_collection.find({}).sort("custom_user_id", 1).to_list(None)
        updated_merchants = await merchants_collection.find({}).sort("custom_merchant_id", 1).to_list(None)
        
        print("   Updated Users:")
        for user in updated_users:
            print(f"     {user['custom_user_id']}: {user['name']} ({user['email']})")
        
        print("   Updated Merchants:")
        for merchant in updated_merchants:
            print(f"     {merchant['custom_merchant_id']}: {merchant['name']}")
        
        print("\n✅ Reset and update completed successfully!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error during reset: {e}")

if __name__ == "__main__":
    asyncio.run(reset_counters_and_update_records())
