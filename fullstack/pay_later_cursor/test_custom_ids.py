import asyncio
import motor.motor_asyncio
from app.common.counters import CounterService, USER_ID_COUNTER, MERCHANT_ID_COUNTER

async def test_custom_ids():
    """Test the custom auto-increment ID functionality."""
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
        database = client.lazypay
        
        # Create counter service
        counter_service = CounterService(database)
        
        print("🧪 Testing Custom Auto-Increment IDs...")
        
        # Test user ID counter
        print("\n📝 Testing User ID Counter:")
        for i in range(3):
            user_id = await counter_service.get_next_id(USER_ID_COUNTER)
            print(f"   Generated User ID: {user_id}")
        
        # Test merchant ID counter
        print("\n🏪 Testing Merchant ID Counter:")
        for i in range(3):
            merchant_id = await counter_service.get_next_id(MERCHANT_ID_COUNTER)
            print(f"   Generated Merchant ID: {merchant_id}")
        
        # Check current values
        print("\n📊 Current Counter Values:")
        current_user_id = await counter_service.get_current_id(USER_ID_COUNTER)
        current_merchant_id = await counter_service.get_current_id(MERCHANT_ID_COUNTER)
        print(f"   Current User ID: {current_user_id}")
        print(f"   Current Merchant ID: {current_merchant_id}")
        
        print("\n✅ Custom ID test completed successfully!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error testing custom IDs: {e}")

if __name__ == "__main__":
    asyncio.run(test_custom_ids())
