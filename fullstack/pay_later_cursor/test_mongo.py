import asyncio
import motor.motor_asyncio

async def test_mongodb():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
        await client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mongodb())
