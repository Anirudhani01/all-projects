#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database
from app.modules.users.repository import UserRepository

async def test_repository_direct():
    await connect_to_mongo()
    db = await get_database()
    
    custom_user_id = 60
    repayment_amount = 500.0
    
    try:
        # Test repository directly
        user_repo = UserRepository(db)
        
        print(f"Testing repayment of ₹{repayment_amount} for user {custom_user_id}")
        
        # Test the repayment method
        success = await user_repo.process_repayment(custom_user_id, repayment_amount)
        
        if success:
            print(f"✅ Repository repayment successful!")
            
            # Check updated state
            user_bank = await user_repo.get_user_bank(custom_user_id)
            user_balance = await user_repo.get_user_balance(custom_user_id)
            
            if user_bank and user_balance:
                print(f"✅ Updated State:")
                print(f"   Bank Balance: ₹{user_bank.balance}")
                print(f"   Outstanding Amount: ₹{user_balance.outstanding_amount}")
                print(f"   Available Credit: ₹{user_balance.available_credit}")
        else:
            print(f"❌ Repository repayment failed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_repository_direct())
