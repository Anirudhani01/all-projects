#!/usr/bin/env python3

import asyncio
from bson import ObjectId
from app.db.mongo import connect_to_mongo, get_database

async def check_specific_user():
    await connect_to_mongo()
    db = await get_database()
    
    # Check the specific user ID from login response
    user_id = "68a401a3376cabb24d058b78"
    
    try:
        # Check in users collection
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            print(f"User found in users collection:")
            print(f"  Name: {user.get('name')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Custom User ID: {user.get('user_id')}")
        else:
            print("User not found in users collection")
        
        # Check in auth_users collection
        auth_user = await db.auth_users.find_one({"_id": ObjectId(user_id)})
        if auth_user:
            print(f"\nAuth user found:")
            print(f"  Email: {auth_user.get('email')}")
            print(f"  Role: {auth_user.get('role')}")
        else:
            print("\nAuth user not found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_specific_user())
