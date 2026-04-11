#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database
from app.modules.users.repository import UserRepository

async def test_user_balance():
    await connect_to_mongo()
    db = await get_database()
    
    custom_user_id = 60
    
    try:
        # Test repository directly
        user_repo = UserRepository(db)
        
        print(f"Testing user balance retrieval for user {custom_user_id}")
        
        # Test get_user_balance
        user_balance = await user_repo.get_user_balance(custom_user_id)
        if user_balance:
            print(f"✅ User balance found:")
            print(f"   Credit Limit: ₹{user_balance.credit_limit}")
            print(f"   Available Credit: ₹{user_balance.available_credit}")
            print(f"   Outstanding Amount: ₹{user_balance.outstanding_amount}")
        else:
            print("❌ User balance not found")
        
        # Test get_user_bank
        user_bank = await user_repo.get_user_bank(custom_user_id)
        if user_bank:
            print(f"\n✅ User bank found:")
            print(f"   Balance: ₹{user_bank.balance}")
            print(f"   Total Deposited: ₹{user_bank.total_deposited}")
            print(f"   Total Withdrawn: ₹{user_bank.total_withdrawn}")
        else:
            print("\n❌ User bank not found")
        
        # Test get_user_by_id
        user = await user_repo.get_user_by_id(custom_user_id)
        if user:
            print(f"\n✅ User found:")
            print(f"   Name: {user.name}")
            print(f"   Email: {user.email}")
            print(f"   Custom ID: {user.user_id}")
        else:
            print("\n❌ User not found")
        
        # Test get_user_financial_summary
        try:
            financial_summary = await user_repo.get_user_financial_summary(custom_user_id)
            print(f"\n✅ Financial summary found:")
            print(f"   User: {financial_summary['user']['name']}")
            print(f"   Credit Limit: ₹{financial_summary['credit']['credit_limit']}")
            print(f"   Bank Balance: ₹{financial_summary['bank']['balance']}")
        except Exception as e:
            print(f"\n❌ Financial summary error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_balance())
