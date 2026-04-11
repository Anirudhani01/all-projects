#!/usr/bin/env python3

import asyncio
from bson import ObjectId
from app.db.mongo import connect_to_mongo, get_database

async def check_current_state():
    await connect_to_mongo()
    db = await get_database()
    
    # Check users collection
    users = await db.users.find({}).to_list(5)
    print(f"Users collection has {len(users)} records:")
    for user in users:
        print(f"  {user.get('_id')} - {user.get('name')} - {user.get('email')} - Custom ID: {user.get('user_id')}")
    
    # Check user_bank collection
    user_banks = await db.user_bank.find({}).to_list(5)
    print(f"\nUser bank collection has {len(user_banks)} records:")
    for bank in user_banks:
        print(f"  User ID: {bank.get('user_id')} - Balance: ₹{bank.get('balance')}")
    
    # Check user_balances collection
    user_balances = await db.user_balances.find({}).to_list(5)
    print(f"\nUser balances collection has {len(user_balances)} records:")
    for balance in user_balances:
        print(f"  User ID: {balance.get('user_id')} - Credit Limit: ₹{balance.get('credit_limit')} - Available: ₹{balance.get('available_credit')}")

if __name__ == "__main__":
    asyncio.run(check_current_state())
