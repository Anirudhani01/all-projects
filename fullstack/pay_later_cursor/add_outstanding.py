#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database

async def add_outstanding():
    await connect_to_mongo()
    db = await get_database()
    
    custom_user_id = 60
    
    try:
        # Update user balance to have some outstanding amount
        result = await db.user_balances.update_one(
            {"user_id": custom_user_id},
            {
                "$set": {
                    "outstanding_amount": 1000.0,
                    "available_credit": 1000.0,  # 2000 - 1000
                    "total_merchant_usage": 1000.0,
                    "updated_at": asyncio.get_event_loop().time()
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Updated user balance:")
            print(f"   Outstanding Amount: ₹1000.0")
            print(f"   Available Credit: ₹1000.0")
            print(f"   Total Merchant Usage: ₹1000.0")
        else:
            print("❌ Failed to update user balance")
        
        # Verify the update
        user_balance = await db.user_balances.find_one({"user_id": custom_user_id})
        if user_balance:
            print(f"\n✅ Verification:")
            print(f"   Credit Limit: ₹{user_balance.get('credit_limit')}")
            print(f"   Available Credit: ₹{user_balance.get('available_credit')}")
            print(f"   Outstanding Amount: ₹{user_balance.get('outstanding_amount')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_outstanding())
