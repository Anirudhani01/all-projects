#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database

async def search_nani():
    await connect_to_mongo()
    db = await get_database()
    
    # Search in users collection
    users = await db.users.find({"email": {"$regex": "nani", "$options": "i"}}).to_list(10)
    print(f"Found {len(users)} users with 'nani' in email:")
    for user in users:
        print(f"  Name: {user.get('name')} | Email: {user.get('email')} | Custom ID: {user.get('user_id')}")
    
    # Search in auth_users collection
    auth_users = await db.auth_users.find({"email": {"$regex": "nani", "$options": "i"}}).to_list(10)
    print(f"\nFound {len(auth_users)} auth users with 'nani' in email:")
    for user in auth_users:
        print(f"  Email: {user.get('email')} | Role: {user.get('role')} | User ID: {user.get('user_id')}")

if __name__ == "__main__":
    asyncio.run(search_nani())
