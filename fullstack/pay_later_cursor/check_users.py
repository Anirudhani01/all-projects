#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database

async def check_users():
    await connect_to_mongo()
    db = await get_database()
    
    # Search for users with "ani" in email
    users = await db.auth_users.find({"email": {"$regex": "ani", "$options": "i"}}).to_list(10)
    print('Users with "ani" in email:')
    for u in users:
        print(f'  {u.get("email", "N/A")} - {u.get("name", "N/A")}')
    
    # Also show first 10 users
    print('\nFirst 10 users:')
    users = await db.auth_users.find({}).limit(10).to_list(10)
    for u in users:
        print(f'  {u.get("email", "N/A")} - {u.get("name", "N/A")}')

if __name__ == "__main__":
    asyncio.run(check_users())
