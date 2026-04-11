#!/usr/bin/env python3

import asyncio
from bson import ObjectId
from app.db.mongo import connect_to_mongo, get_database

async def fix_user_data():
    await connect_to_mongo()
    db = await get_database()
    
    try:
        # Check for users with null custom_user_id
        null_users = await db.users.find({"custom_user_id": None}).to_list(10)
        print(f"Found {len(null_users)} users with null custom_user_id")
        
        # Remove users with null custom_user_id
        if null_users:
            result = await db.users.delete_many({"custom_user_id": None})
            print(f"Deleted {result.deleted_count} users with null custom_user_id")
        
        # Check for users with null user_id
        null_user_id_users = await db.users.find({"user_id": None}).to_list(10)
        print(f"Found {len(null_user_id_users)} users with null user_id")
        
        # Remove users with null user_id
        if null_user_id_users:
            result = await db.users.delete_many({"user_id": None})
            print(f"Deleted {result.deleted_count} users with null user_id")
        
        # List current users
        users = await db.users.find({}).to_list(10)
        print(f"\nCurrent users:")
        for user in users:
            print(f"  {user.get('_id')} - {user.get('name')} - {user.get('email')} - Custom ID: {user.get('user_id')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_user_data())
