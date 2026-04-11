import asyncio
import motor.motor_asyncio
from bson import ObjectId

async def check_database():
    """Check the actual data in the database."""
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
        database = client.lazypay
        
        print("🔍 Checking database records...")
        
        # Check users
        print("\n👥 Users in database:")
        users_collection = database.users
        users = await users_collection.find({}).to_list(None)
        
        for user in users:
            print(f"   ID: {user['_id']}")
            print(f"   Name: {user['name']}")
            print(f"   Email: {user['email']}")
            print(f"   Custom User ID: {user.get('custom_user_id', 'NOT SET')}")
            print(f"   Created: {user['created_at']}")
            print("   ---")
        
        # Check merchants
        print("\n🏪 Merchants in database:")
        merchants_collection = database.merchants
        merchants = await merchants_collection.find({}).to_list(None)
        
        for merchant in merchants:
            print(f"   ID: {merchant['_id']}")
            print(f"   Name: {merchant['name']}")
            print(f"   Custom Merchant ID: {merchant.get('custom_merchant_id', 'NOT SET')}")
            print(f"   Fee: {merchant['current_fee_pct']}%")
            print(f"   Created: {merchant['created_at']}")
            print("   ---")
        
        # Check counters
        print("\n📊 Counter values:")
        counters_collection = database.counters
        counters = await counters_collection.find({}).to_list(None)
        
        for counter in counters:
            print(f"   {counter['_id']}: {counter['sequence_value']}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    asyncio.run(check_database())
