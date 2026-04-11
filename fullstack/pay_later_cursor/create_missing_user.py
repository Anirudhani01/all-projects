#!/usr/bin/env python3

import asyncio
from bson import ObjectId
from datetime import datetime
from app.db.mongo import connect_to_mongo, get_database

async def create_missing_user():
    await connect_to_mongo()
    db = await get_database()
    
    # User details
    user_id = "68a401a3376cabb24d058b78"
    email = "nani@gmail.com"
    name = "nani"
    
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": email})
        if existing_user:
            print(f"User already exists with custom ID: {existing_user.get('user_id')}")
            return existing_user.get('user_id')
        
        # Get the next custom user ID
        counter = await db.counters.find_one_and_update(
            {"_id": "user_id"},
            {"$inc": {"sequence_value": 1}},
            return_document=True
        )
        
        if not counter:
            # Initialize counter if it doesn't exist
            await db.counters.insert_one({"_id": "user_id", "sequence_value": 1})
            custom_user_id = 1
        else:
            custom_user_id = counter["sequence_value"]
        
        # Create user profile
        user_doc = {
            "_id": ObjectId(user_id),
            "user_id": custom_user_id,
            "name": name,
            "email": email,
            "phone": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(user_doc)
        print(f"✅ Created user profile with custom ID: {custom_user_id}")
        
        # Create user bank record
        user_bank_doc = {
            "user_id": custom_user_id,
            "balance": 2000.0,  # Default balance
            "total_deposited": 2000.0,
            "total_withdrawn": 0.0,
            "last_transaction_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.user_bank.insert_one(user_bank_doc)
        print(f"✅ Created user bank record with balance: ₹2000.0")
        
        # Create user balance record
        user_balance_doc = {
            "user_id": custom_user_id,
            "credit_limit": 2000.0,
            "available_credit": 2000.0,
            "outstanding_amount": 0.0,
            "total_merchant_usage": 0.0,
            "reached_limit": False,
            "version": 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.user_balances.insert_one(user_balance_doc)
        print(f"✅ Created user balance record with credit limit: ₹2000.0")
        
        return custom_user_id
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(create_missing_user())
