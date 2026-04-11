#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService

async def debug_users():
    await connect_to_mongo()
    db = await get_database()
    
    try:
        # Test repository directly
        print("Testing UserRepository...")
        user_repo = UserRepository(db)
        
        # Test get_all_users
        print("Calling get_all_users...")
        users = await user_repo.get_all_users(skip=0, limit=10)
        print(f"Found {len(users)} users")
        
        for user in users[:3]:  # Show first 3 users
            print(f"  User: {user.name} (ID: {user.user_id}, Email: {user.email})")
        
        # Test service
        print("\nTesting UserService...")
        user_service = UserService(user_repo)
        
        # Test get_all_users through service
        print("Calling service.get_all_users...")
        service_users = await user_service.get_all_users(skip=0, limit=10)
        print(f"Service found {len(service_users)} users")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_users())
