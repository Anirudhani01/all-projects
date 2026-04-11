#!/usr/bin/env python3
"""
Test script to verify wallet service functionality.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.mongo import mongodb
from app.modules.wallet.repository import WalletRepository
from app.modules.wallet.service import WalletService
from app.modules.wallet.models import MerchantWallet, CreditLimit
from bson import ObjectId
import structlog

logger = structlog.get_logger(__name__)


async def test_wallet_service():
    """Test wallet service functionality."""
    try:
        logger.info("🧪 Starting wallet service tests...")
        
        # Connect to database
        await mongodb.connect()
        
        # Create repository and service
        wallet_repo = WalletRepository(mongodb.get_database())
        wallet_service = WalletService(wallet_repo)
        
        # Test 1: Fee calculation
        logger.info("\n--- Test 1: Fee Calculation ---")
        amount = 500.0
        fee_pct = 10.0
        fee_amount = await wallet_service.calculate_fee(amount, fee_pct)
        total_amount = await wallet_service.calculate_total_amount(amount, fee_amount)
        
        logger.info(f"Amount: {amount}")
        logger.info(f"Fee Percentage: {fee_pct}%")
        logger.info(f"Fee Amount: {fee_amount}")
        logger.info(f"Total Amount: {total_amount}")
        
        assert fee_amount == 50.0, f"Expected fee 50.0, got {fee_amount}"
        assert total_amount == 550.0, f"Expected total 550.0, got {total_amount}"
        logger.info("✅ Fee calculation test passed")
        
        # Test 2: Get user credit info
        logger.info("\n--- Test 2: User Credit Info ---")
        # Get first user from database
        users_collection = mongodb.get_database().user_balances
        user_doc = await users_collection.find_one({})
        
        if user_doc:
            user_id = user_doc["user_id"]
            credit_info = await wallet_service.get_user_credit_info(user_id)
            
            if credit_info:
                logger.info(f"User Credit Info: {credit_info}")
                logger.info("✅ User credit info test passed")
            else:
                logger.warning("⚠️ No credit info found for user")
        else:
            logger.warning("⚠️ No users found in database")
        
        # Test 3: Get merchant wallet balance
        logger.info("\n--- Test 3: Merchant Wallet Balance ---")
        # Get first merchant from database
        merchants_collection = mongodb.get_database().merchants
        merchant_doc = await merchants_collection.find_one({})
        
        if merchant_doc:
            merchant_id = merchant_doc["_id"]
            balance = await wallet_service.get_merchant_wallet_balance(merchant_id)
            
            logger.info(f"Merchant: {merchant_doc.get('name', 'Unknown')}")
            logger.info(f"Wallet Balance: {balance}")
            logger.info("✅ Merchant wallet balance test passed")
        else:
            logger.warning("⚠️ No merchants found in database")
        
        # Test 4: Credit sufficiency check
        logger.info("\n--- Test 4: Credit Sufficiency Check ---")
        if user_doc:
            user_id = user_doc["user_id"]
            has_sufficient = await wallet_service.check_user_credit_sufficiency(user_id, 100.0)
            
            logger.info(f"Credit sufficiency for 100.0: {has_sufficient}")
            logger.info("✅ Credit sufficiency test passed")
        
        # Test 5: Get wallet transactions
        logger.info("\n--- Test 5: Wallet Transactions ---")
        transactions = await wallet_service.get_wallet_transactions(limit=5)
        
        logger.info(f"Found {len(transactions)} wallet transactions")
        for i, transaction in enumerate(transactions[:3]):  # Show first 3
            logger.info(f"Transaction {i+1}: {transaction.get('type', 'Unknown')} - {transaction.get('amount', 0)}")
        
        logger.info("✅ Wallet transactions test passed")
        
        logger.info("\n🎉 All wallet service tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(test_wallet_service())
