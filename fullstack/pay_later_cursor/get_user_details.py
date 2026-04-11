#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database

async def get_user_details():
    await connect_to_mongo()
    db = await get_database()
    
    # Find user with email nani@gmail.com
    user = await db.users.find_one({"email": "nani@gmail.com"})
    
    if user:
        print(f"User found:")
        print(f"  Name: {user.get('name')}")
        print(f"  Email: {user.get('email')}")
        print(f"  MongoDB ID: {user.get('_id')}")
        print(f"  Custom User ID: {user.get('user_id')}")
        
        # Also check user_bank
        user_bank = await db.user_bank.find_one({"user_id": user.get('user_id')})
        if user_bank:
            print(f"  Bank Balance: ₹{user_bank.get('balance')}")
        
        # Check user_balances
        user_balance = await db.user_balances.find_one({"user_id": user.get('user_id')})
        if user_balance:
            print(f"  Credit Limit: ₹{user_balance.get('credit_limit')}")
            print(f"  Available Credit: ₹{user_balance.get('available_credit')}")
            print(f"  Outstanding Amount: ₹{user_balance.get('outstanding_amount')}")
    else:
        print("User not found")

if __name__ == "__main__":
    asyncio.run(get_user_details())
