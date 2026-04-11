#!/usr/bin/env python3
"""
Script to check existing users in the database
"""

import asyncio
import motor.motor_asyncio

async def check_existing_users():
    """Check what users already exist in the database."""
    
    print("🔍 Checking existing users...")
    print("=" * 40)
    
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.ecommerce_dev
        users_collection = db.users
        
        # Get all users
        users = await users_collection.find({}).to_list(length=None)
        
        if users:
            print(f"👥 Found {len(users)} user(s):")
            print("-" * 40)
            
            for i, user in enumerate(users, 1):
                print(f"\n👤 User {i}:")
                print(f"   🆔 ID: {user.get('id', 'N/A')}")
                print(f"   📧 Email: {user.get('email', 'N/A')}")
                print(f"   👤 First Name: {user.get('first_name', 'N/A')}")
                print(f"   👤 Last Name: {user.get('last_name', 'N/A')}")
                print(f"   🎭 Role: {user.get('role', 'N/A')}")
                print(f"   👑 Admin: {user.get('isAdmin', False)}")
                print(f"   ✅ Active: {user.get('isActive', True)}")
                print(f"   📅 Created: {user.get('createdAt', 'N/A')}")
                
        else:
            print("❌ No users found in the database")
            
        client.close()
        
    except Exception as e:
        print(f"❌ Error checking users: {e}")

if __name__ == "__main__":
    print("🚀 User Check Script")
    print("=" * 40)
    asyncio.run(check_existing_users())
