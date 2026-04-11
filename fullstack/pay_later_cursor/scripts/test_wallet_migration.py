#!/usr/bin/env python3
"""
Test script to verify wallet migration was successful.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.mongo import mongodb
from app.rbac.repository import RBACRepository
import structlog

logger = structlog.get_logger(__name__)


async def test_user_balances_migration():
    """Test if user_balances have wallet fields."""
    try:
        logger.info("Testing user_balances migration...")
        
        database = mongodb.get_database()
        collection = database.user_balances
        
        # Check a few documents
        cursor = collection.find({}).limit(5)
        test_count = 0
        
        async for doc in cursor:
            test_count += 1
            required_fields = ["credit_limit", "available_credit", "total_merchant_usage"]
            
            missing_fields = [field for field in required_fields if field not in doc]
            if missing_fields:
                logger.error(f"❌ User balance missing fields: {missing_fields}")
                return False
            else:
                logger.info(f"✅ User balance {doc['_id']} has all wallet fields")
        
        if test_count == 0:
            logger.warning("⚠️ No user balances found to test")
        else:
            logger.info(f"✅ Tested {test_count} user balances - all have wallet fields")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing user_balances: {str(e)}")
        return False


async def test_merchants_migration():
    """Test if merchants have wallet fields."""
    try:
        logger.info("Testing merchants migration...")
        
        database = mongodb.get_database()
        collection = database.merchants
        
        # Check a few documents
        cursor = collection.find({}).limit(5)
        test_count = 0
        
        async for doc in cursor:
            test_count += 1
            required_fields = ["wallet_balance", "total_received"]
            
            missing_fields = [field for field in required_fields if field not in doc]
            if missing_fields:
                logger.error(f"❌ Merchant missing fields: {missing_fields}")
                return False
            else:
                logger.info(f"✅ Merchant {doc.get('name', 'Unknown')} has all wallet fields")
        
        if test_count == 0:
            logger.warning("⚠️ No merchants found to test")
        else:
            logger.info(f"✅ Tested {test_count} merchants - all have wallet fields")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing merchants: {str(e)}")
        return False


async def test_transactions_migration():
    """Test if transactions have wallet fields."""
    try:
        logger.info("Testing transactions migration...")
        
        database = mongodb.get_database()
        collection = database.transactions
        
        # Check a few documents
        cursor = collection.find({}).limit(5)
        test_count = 0
        
        async for doc in cursor:
            test_count += 1
            required_fields = [
                "total_amount", "merchant_wallet_balance_before", 
                "merchant_wallet_balance_after", "user_credit_before", "user_credit_after"
            ]
            
            missing_fields = [field for field in required_fields if field not in doc]
            if missing_fields:
                logger.error(f"❌ Transaction missing fields: {missing_fields}")
                return False
            else:
                logger.info(f"✅ Transaction {doc['_id']} has all wallet fields")
        
        if test_count == 0:
            logger.warning("⚠️ No transactions found to test")
        else:
            logger.info(f"✅ Tested {test_count} transactions - all have wallet fields")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing transactions: {str(e)}")
        return False


async def test_wallet_permissions():
    """Test if wallet permissions were created."""
    try:
        logger.info("Testing wallet permissions...")
        
        database = mongodb.get_database()
        rbac_repo = RBACRepository(database)
        
        required_permissions = [
            "wallet_read", "wallet_write",
            "credit_read", "credit_write",
            "wallet_transactions_read", "wallet_transactions_write"
        ]
        
        missing_permissions = []
        for perm_name in required_permissions:
            perm = await rbac_repo.get_permission_by_name(perm_name)
            if not perm:
                missing_permissions.append(perm_name)
            else:
                logger.info(f"✅ Permission exists: {perm_name}")
        
        if missing_permissions:
            logger.error(f"❌ Missing permissions: {missing_permissions}")
            return False
        else:
            logger.info("✅ All wallet permissions exist")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing permissions: {str(e)}")
        return False


async def test_role_updates():
    """Test if roles have wallet permissions."""
    try:
        logger.info("Testing role updates...")
        
        database = mongodb.get_database()
        rbac_repo = RBACRepository(database)
        
        # Test admin role
        admin_role = await rbac_repo.get_role_by_name("admin")
        if admin_role:
            logger.info(f"✅ Admin role has {len(admin_role.permissions)} permissions")
        else:
            logger.warning("⚠️ Admin role not found")
        
        # Test merchant role
        merchant_role = await rbac_repo.get_role_by_name("merchant")
        if merchant_role:
            logger.info(f"✅ Merchant role has {len(merchant_role.permissions)} permissions")
        else:
            logger.warning("⚠️ Merchant role not found")
        
        # Test user role
        user_role = await rbac_repo.get_role_by_name("user")
        if user_role:
            logger.info(f"✅ User role has {len(user_role.permissions)} permissions")
        else:
            logger.warning("⚠️ User role not found")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing roles: {str(e)}")
        return False


async def run_tests():
    """Run all migration tests."""
    try:
        logger.info("🧪 Starting wallet migration tests...")
        
        # Connect to database
        await mongodb.connect()
        
        # Run tests
        tests = [
            ("User Balances", test_user_balances_migration),
            ("Merchants", test_merchants_migration),
            ("Transactions", test_transactions_migration),
            ("Wallet Permissions", test_wallet_permissions),
            ("Role Updates", test_role_updates)
        ]
        
        results = []
        for test_name, test_func in tests:
            logger.info(f"\n--- Testing {test_name} ---")
            result = await test_func()
            results.append((test_name, result))
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("📊 MIGRATION TEST RESULTS")
        logger.info("="*50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test_name}: {status}")
            if result:
                passed += 1
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! Migration was successful.")
        else:
            logger.error("❌ Some tests failed. Please check the migration.")
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        raise
    finally:
        await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(run_tests())
