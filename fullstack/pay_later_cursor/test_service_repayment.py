#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService

async def test_service_repayment():
    await connect_to_mongo()
    db = await get_database()
    
    custom_user_id = 60
    repayment_amount = 200.0  # Smaller amount for testing
    
    try:
        # Test service directly
        user_repo = UserRepository(db)
        user_service = UserService(user_repo)
        
        print(f"Testing service repayment of ₹{repayment_amount} for user {custom_user_id}")
        
        # Test the service repayment method
        result = await user_service.process_repayment(custom_user_id, repayment_amount)
        
        print(f"Service result: {result}")
        
        if result["success"]:
            print(f"✅ Service repayment successful!")
            print(f"   Repayment Amount: ₹{result.get('repayment_amount')}")
            print(f"   New Outstanding Amount: ₹{result.get('new_outstanding_amount')}")
            print(f"   New Bank Balance: ₹{result.get('new_bank_balance')}")
        else:
            print(f"❌ Service repayment failed: {result.get('message')}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service_repayment())
