#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database

async def check_nani_state():
    await connect_to_mongo()
    db = await get_database()
    
    custom_user_id = 60
    
    try:
        # Check user profile
        user = await db.users.find_one({"user_id": custom_user_id})
        if user:
            print(f"✅ User Profile:")
            print(f"   Name: {user.get('name')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Custom ID: {user.get('user_id')}")
        else:
            print("❌ User profile not found")
        
        # Check user bank
        user_bank = await db.user_bank.find_one({"user_id": custom_user_id})
        if user_bank:
            print(f"\n✅ User Bank:")
            print(f"   Balance: ₹{user_bank.get('balance')}")
            print(f"   Total Deposited: ₹{user_bank.get('total_deposited')}")
            print(f"   Total Withdrawn: ₹{user_bank.get('total_withdrawn')}")
        else:
            print("\n❌ User bank not found")
        
        # Check user balance
        user_balance = await db.user_balances.find_one({"user_id": custom_user_id})
        if user_balance:
            print(f"\n✅ User Balance:")
            print(f"   Credit Limit: ₹{user_balance.get('credit_limit')}")
            print(f"   Available Credit: ₹{user_balance.get('available_credit')}")
            print(f"   Outstanding Amount: ₹{user_balance.get('outstanding_amount')}")
            print(f"   Total Merchant Usage: ₹{user_balance.get('total_merchant_usage')}")
        else:
            print("\n❌ User balance not found")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_nani_state())
