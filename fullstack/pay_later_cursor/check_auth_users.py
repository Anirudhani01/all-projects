#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database

async def check_auth_users():
    await connect_to_mongo()
    db = await get_database()
    
    # Check auth_users collection
    auth_users = await db.auth_users.find({}).to_list(20)
    
    print(f"Found {len(auth_users)} auth users:")
    for i, user in enumerate(auth_users, 1):
        print(f"{i}. Email: {user.get('email')} | Role: {user.get('role')} | User ID: {user.get('user_id')}")

if __name__ == "__main__":
    asyncio.run(check_auth_users())
