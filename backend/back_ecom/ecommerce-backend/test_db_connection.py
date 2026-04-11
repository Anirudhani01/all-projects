#!/usr/bin/env python3
"""
Script to test database connection
"""

import asyncio
import motor.motor_asyncio
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

async def test_database_connection():
    """Test if we can connect to MongoDB."""
    
    print("🔍 Testing database connection...")
    print("=" * 40)
    
    try:
        # Try to connect to MongoDB
        print("📡 Attempting to connect to MongoDB...")
        client = motor.motor_asyncio.AsyncIOMotorClient(
            "mongodb://localhost:27017",
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000
        )
        
        # Test the connection
        print("🔄 Testing connection...")
        await client.admin.command('ping')
        
        print("✅ MongoDB connection successful!")
        
        # List available databases
        print("\n📚 Available databases:")
        databases = await client.list_database_names()
        for db_name in databases:
            print(f"   - {db_name}")
        
        # Check if our target database exists
        target_db = "ecommerce_dev"
        if target_db in databases:
            print(f"\n🎯 Target database '{target_db}' found!")
            
            # Check collections in the database
            db = client[target_db]
            collections = await db.list_collection_names()
            print(f"📁 Collections in {target_db}:")
            for collection in collections:
                print(f"   - {collection}")
                
            # Check if users collection exists and has data
            if "users" in collections:
                users_count = await db.users.count_documents({})
                print(f"\n👥 Users collection has {users_count} documents")
            else:
                print(f"\n❌ Users collection not found in {target_db}")
        else:
            print(f"\n⚠️  Target database '{target_db}' not found")
            print("💡 The database will be created automatically when you first use it")
        
        client.close()
        
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure MongoDB is running on localhost:27017")
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ Server selection timeout: {e}")
        print("💡 MongoDB might not be running or accessible")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"💡 Error type: {type(e).__name__}")

if __name__ == "__main__":
    print("🚀 Database Connection Test")
    print("=" * 40)
    asyncio.run(test_database_connection())
