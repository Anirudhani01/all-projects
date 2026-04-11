#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database
from app.modules.transactions.repository import TransactionRepository
from app.modules.transactions.service import TransactionService
from app.modules.users.service import UserService
from app.modules.users.repository import UserRepository
from app.modules.merchants.service import MerchantService
from app.modules.merchants.repository import MerchantRepository

async def debug_transactions():
    await connect_to_mongo()
    db = await get_database()
    
    try:
        # Test repositories
        print("Testing repositories...")
        transaction_repo = TransactionRepository(db)
        user_repo = UserRepository(db)
        merchant_repo = MerchantRepository(db)
        
        # Test services
        print("Testing services...")
        user_service = UserService(user_repo)
        merchant_service = MerchantService(merchant_repo)
        transaction_service = TransactionService(transaction_repo, user_service, merchant_service)
        
        # Test get_transactions_with_filters
        print("Testing get_transactions_with_filters...")
        
        # Create a simple filter
        from app.modules.transactions.schemas import TransactionFilter
        filters = TransactionFilter(page=1, size=10)
        
        result = await transaction_service.get_transactions_with_filters(filters)
        print(f"Found {len(result.transactions)} transactions")
        print(f"Total: {result.total}")
        
        for tx in result.transactions[:3]:  # Show first 3 transactions
            print(f"  Transaction: {tx.id} - Type: {tx.type} - Amount: {tx.amount}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_transactions())
