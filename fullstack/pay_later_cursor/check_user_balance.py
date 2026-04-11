#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database
from bson import ObjectId
from datetime import datetime, timezone

async def check_and_create_user_balance():
    await connect_to_mongo()
    db = await get_database()
    
    # Check if user exists in auth_users
    user = await db.auth_users.find_one({"email": "nani@gmail.com"})
    if not user:
        print("❌ User not found in auth_users")
        return
    
    user_id = user["_id"]
    print(f"✅ Found user: {user['name']} ({user['email']}) with ID: {user_id}")
    
    # Check if user has a balance record
    balance_record = await db.user_balances.find_one({"user_id": user_id})
    if balance_record:
        print(f"✅ User balance record exists:")
        print(f"   Credit Limit: ₹{balance_record.get('credit_limit', 0)}")
        print(f"   Available Credit: ₹{balance_record.get('available_credit', 0)}")
        print(f"   Outstanding Amount: ₹{balance_record.get('outstanding_amount', 0)}")
    else:
        print("❌ No user balance record found. Creating one...")
        
        # Create user balance record
        balance_data = {
            "user_id": user_id,
            "credit_limit": 2000.0,
            "outstanding_amount": 0.0,
            "available_credit": 2000.0,
            "total_merchant_usage": 0.0,
            "total_purchases": 0.0,
            "total_payments": 0.0,
            "reached_limit": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = await db.user_balances.insert_one(balance_data)
        print(f"✅ Created user balance record with ID: {result.inserted_id}")
        
        # Also create user_bank record
        bank_data = {
            "user_id": user_id,
            "balance": 2000.0,
            "total_deposited": 2000.0,
            "total_withdrawn": 0.0,
            "last_transaction_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        bank_result = await db.user_bank.insert_one(bank_data)
        print(f"✅ Created user bank record with ID: {bank_result.inserted_id}")

if __name__ == "__main__":
    asyncio.run(check_and_create_user_balance())
