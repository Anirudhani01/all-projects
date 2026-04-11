#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database

async def list_all_users():
    await connect_to_mongo()
    db = await get_database()
    
    # List all users
    users = await db.users.find({}).to_list(20)
    
    print(f"Found {len(users)} users:")
    for i, user in enumerate(users, 1):
        print(f"{i}. Name: {user.get('name')} | Email: {user.get('email')} | Custom ID: {user.get('user_id')} | MongoDB ID: {user.get('_id')}")

if __name__ == "__main__":
    asyncio.run(list_all_users())
