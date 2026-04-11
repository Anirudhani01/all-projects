#!/usr/bin/env python3
"""
Script to check admin collection and admin users
"""

import asyncio
import motor.motor_asyncio

async def check_admin_collection():
    """Check for admin collection and admin users."""
    
    print("🔍 Checking admin collections and users...")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.ecommerce_dev
        
        # Get all collections
        collections = await db.list_collection_names()
        print("📁 All collections in ecommerce_dev:")
        for collection in collections:
            print(f"   - {collection}")
        
        # Check if there's an admin collection
        if "admin" in collections or "admins" in collections:
            admin_collection_name = "admin" if "admin" in collections else "admins"
            print(f"\n🎯 Found admin collection: {admin_collection_name}")
            
            admin_collection = db[admin_collection_name]
            admins = await admin_collection.find({}).to_list(length=None)
            
            if admins:
                print(f"👑 Found {len(admins)} admin(s):")
                print("-" * 40)
                
                for i, admin in enumerate(admins, 1):
                    print(f"\n👤 Admin {i}:")
                    print(f"   🆔 ID: {admin.get('id', admin.get('_id', 'N/A'))}")
                    print(f"   📧 Email: {admin.get('email', 'N/A')}")
                    print(f"   👤 Name: {admin.get('first_name', 'N/A')} {admin.get('last_name', 'N/A')}")
                    print(f"   🎭 Role: {admin.get('role', 'N/A')}")
                    print(f"   📅 Created: {admin.get('createdAt', 'N/A')}")
            else:
                print(f"❌ No documents found in {admin_collection_name} collection")
        else:
            print("\n❌ No dedicated admin collection found")
        
        # Check for admin users in the users collection
        users_collection = db.users
        admin_users = await users_collection.find({
            "$or": [
                {"role": "admin"},
                {"isAdmin": True},
                {"role": {"$regex": "admin", "$options": "i"}}
            ]
        }).to_list(length=None)
        
        print(f"\n👥 Admin users in users collection:")
        if admin_users:
            print(f"👑 Found {len(admin_users)} admin user(s):")
            print("-" * 40)
            
            for i, user in enumerate(admin_users, 1):
                print(f"\n👤 Admin User {i}:")
                print(f"   🆔 ID: {user.get('id', user.get('_id', 'N/A'))}")
                print(f"   📧 Email: {user.get('email', 'N/A')}")
                print(f"   👤 Name: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
                print(f"   🎭 Role: {user.get('role', 'N/A')}")
                print(f"   👑 Admin: {user.get('isAdmin', False)}")
                print(f"   📅 Created: {user.get('createdAt', 'N/A')}")
        else:
            print("❌ No admin users found in users collection")
            print("💡 You need to create an admin user to access the admin panel")
        
        # Check regular users count
        regular_users = await users_collection.find({
            "$and": [
                {"role": {"$ne": "admin"}},
                {"isAdmin": {"$ne": True}}
            ]
        }).to_list(length=None)
        
        print(f"\n👤 Regular users: {len(regular_users)}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error checking admin collection: {e}")

if __name__ == "__main__":
    print("🚀 Admin Collection Check")
    print("=" * 50)
    asyncio.run(check_admin_collection())
