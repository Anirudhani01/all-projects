#!/usr/bin/env python3
"""
Migration script to fix existing users and add user bank system.

This script:
1. Assigns user_id to existing users that don't have one
2. Creates user_bank collection for all users with default 2000 balance
3. Updates user_balances to have fixed 2000 credit limit
4. Ensures all users have proper financial records
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.modules.users.models import UserBank, UserBalance
from app.common.counters import CounterService, USER_ID_COUNTER
import structlog

logger = structlog.get_logger(__name__)

class UserBankMigration:
    """Migration class for adding user bank system."""
    
    def __init__(self, database):
        self.database = database
        self.users_collection = database.users
        self.user_balances_collection = database.user_balances
        self.user_bank_collection = database.user_bank
        self.counters_collection = database.counters
        self.counter_service = CounterService(database)
        
    async def assign_user_ids_to_existing_users(self):
        """Assign user_id to existing users that don't have one."""
        logger.info("Assigning user IDs to existing users...")
        
        # Find users without user_id
        users_without_id = await self.users_collection.find({"user_id": {"$exists": False}}).to_list(None)
        logger.info(f"Found {len(users_without_id)} users without user_id")
        
        assigned_count = 0
        for user_data in users_without_id:
            try:
                # Generate new user ID
                new_user_id = await self.counter_service.get_next_id(USER_ID_COUNTER)
                
                # Update user with new user_id
                await self.users_collection.update_one(
                    {"_id": user_data["_id"]},
                    {"$set": {"user_id": new_user_id}}
                )
                
                assigned_count += 1
                logger.info(f"Assigned user_id {new_user_id} to user {user_data['_id']}")
                
            except Exception as e:
                logger.error(f"Failed to assign user_id to user {user_data['_id']}: {str(e)}")
        
        logger.info(f"Assigned user_id to {assigned_count} users")
        return assigned_count
        
    async def migrate_existing_users(self):
        """Migrate existing users to have bank accounts."""
        logger.info("Starting user bank system migration...")
        
        # First assign user IDs to users that don't have them
        await self.assign_user_ids_to_existing_users()
        
        # Get all existing users
        users = await self.users_collection.find({}).to_list(None)
        logger.info(f"Found {len(users)} total users to migrate")
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        for user_data in users:
            try:
                user_id = user_data.get("user_id")
                if not user_id:
                    logger.warning(f"User {user_data.get('_id')} still has no user_id, skipping")
                    skipped_count += 1
                    continue
                
                # Check if user already has a bank account
                existing_bank = await self.user_bank_collection.find_one({"user_id": user_id})
                if existing_bank:
                    logger.info(f"User {user_id} already has bank account, skipping")
                    skipped_count += 1
                    continue
                
                # Create user bank account
                user_bank = UserBank(
                    user_id=user_id,
                    balance=2000.0,  # Default balance
                    total_deposited=2000.0,  # Initial deposit
                    total_withdrawn=0.0,
                    last_transaction_at=datetime.now(timezone.utc)
                )
                
                bank_dict = user_bank.to_dict()
                await self.user_bank_collection.insert_one(bank_dict)
                
                # Update user balance to have fixed 2000 credit limit
                existing_balance = await self.user_balances_collection.find_one({"user_id": user_id})
                if existing_balance:
                    # Update existing balance
                    update_data = {
                        "credit_limit": 2000.0,
                        "available_credit": 2000.0 - existing_balance.get("outstanding_amount", 0.0),
                        "updated_at": datetime.now(timezone.utc)
                    }
                    await self.user_balances_collection.update_one(
                        {"user_id": user_id},
                        {"$set": update_data}
                    )
                else:
                    # Create new balance record
                    user_balance = UserBalance(
                        user_id=user_id,
                        credit_limit=2000.0,
                        outstanding_amount=0.0,
                        available_credit=2000.0,
                        total_merchant_usage=0.0,
                        total_purchases=0.0,
                        total_payments=0.0
                    )
                    balance_dict = user_balance.to_dict()
                    await self.user_balances_collection.insert_one(balance_dict)
                
                migrated_count += 1
                logger.info(f"Successfully migrated user {user_id}")
                
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to migrate user {user_data.get('_id')}: {str(e)}")
        
        logger.info(f"Migration completed: {migrated_count} migrated, {skipped_count} skipped, {error_count} errors")
        return migrated_count, skipped_count, error_count
    
    async def verify_migration(self):
        """Verify that all users have proper bank accounts and balances."""
        logger.info("Verifying migration...")
        
        # Check all users have user_id
        users_without_user_id = await self.users_collection.find({"user_id": {"$exists": False}}).to_list(None)
        if users_without_user_id:
            logger.warning(f"Found {len(users_without_user_id)} users without user_id:")
            for user in users_without_user_id:
                logger.warning(f"  - User {user['_id']}: {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
        else:
            logger.info("All users have user_id ✓")
        
        # Check all users have bank accounts
        users_without_banks = await self.users_collection.aggregate([
            {
                "$lookup": {
                    "from": "user_bank",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "bank"
                }
            },
            {
                "$match": {
                    "bank": {"$size": 0}
                }
            },
            {
                "$project": {
                    "user_id": 1,
                    "name": 1,
                    "email": 1
                }
            }
        ]).to_list(None)
        
        if users_without_banks:
            logger.warning(f"Found {len(users_without_banks)} users without bank accounts:")
            for user in users_without_banks:
                logger.warning(f"  - User {user.get('user_id', 'No ID')}: {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
        else:
            logger.info("All users have bank accounts ✓")
        
        # Check all users have proper balances
        users_without_balances = await self.users_collection.aggregate([
            {
                "$lookup": {
                    "from": "user_balances",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "balance"
                }
            },
            {
                "$match": {
                    "balance": {"$size": 0}
                }
            },
            {
                "$project": {
                    "user_id": 1,
                    "name": 1,
                    "email": 1
                }
            }
        ]).to_list(None)
        
        if users_without_balances:
            logger.warning(f"Found {len(users_without_balances)} users without balance records:")
            for user in users_without_balances:
                logger.warning(f"  - User {user.get('user_id', 'No ID')}: {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
        else:
            logger.info("All users have balance records ✓")
        
        # Check credit limits are set to 2000
        incorrect_limits = await self.user_balances_collection.find({
            "credit_limit": {"$ne": 2000.0}
        }).to_list(None)
        
        if incorrect_limits:
            logger.warning(f"Found {len(incorrect_limits)} users with incorrect credit limits:")
            for balance in incorrect_limits:
                logger.warning(f"  - User {balance.get('user_id', 'No ID')}: credit_limit = {balance.get('credit_limit', 'No limit')}")
        else:
            logger.info("All users have correct credit limits (2000) ✓")
        
        # Summary
        total_users = await self.users_collection.count_documents({})
        total_banks = await self.user_bank_collection.count_documents({})
        total_balances = await self.user_balances_collection.count_documents({})
        
        logger.info(f"Verification summary:")
        logger.info(f"  - Total users: {total_users}")
        logger.info(f"  - Users with bank accounts: {total_banks}")
        logger.info(f"  - Users with balance records: {total_balances}")
        
        return (len(users_without_user_id) == 0 and 
                len(users_without_banks) == 0 and 
                len(users_without_balances) == 0 and 
                len(incorrect_limits) == 0)

async def main():
    """Main migration function."""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.mongodb_uri)
        database = client[settings.mongodb_db]
        
        # Test connection
        await client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Run migration
        migration = UserBankMigration(database)
        
        # Migrate existing users
        migrated, skipped, errors = await migration.migrate_existing_users()
        
        # Verify migration
        verification_passed = await migration.verify_migration()
        
        if verification_passed:
            logger.info("✅ Migration completed successfully!")
        else:
            logger.warning("⚠️ Migration completed with warnings")
        
        # Close connection
        client.close()
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
