#!/usr/bin/env python3
"""
Migration script to add wallet fields to existing collections.
This script enhances the existing database schema for the wallet system.
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.mongo import mongodb
from app.rbac.repository import RBACRepository
from app.rbac.models import Permission
import structlog

logger = structlog.get_logger(__name__)


async def migrate_user_balances():
    """Migrate user_balances collection to add wallet fields."""
    try:
        logger.info("Starting user_balances migration...")
        
        database = mongodb.get_database()
        collection = database.user_balances
        
        # Get all user balances
        cursor = collection.find({})
        updated_count = 0
        
        async for doc in cursor:
            # Check if wallet fields already exist
            if "credit_limit" not in doc:
                # Get user's credit limit from users collection
                user = await database.users.find_one({"_id": doc["user_id"]})
                credit_limit = user.get("credit_limit", 0.0) if user else 0.0
                
                # Calculate available credit
                outstanding_amount = doc.get("outstanding_amount", 0.0)
                available_credit = max(0.0, credit_limit - outstanding_amount)
                
                # Update document with new fields
                update_data = {
                    "credit_limit": credit_limit,
                    "available_credit": available_credit,
                    "total_merchant_usage": 0.0,
                    "updated_at": datetime.utcnow()
                }
                
                await collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": update_data}
                )
                updated_count += 1
                logger.info(f"Updated user balance for user_id: {doc['user_id']}")
        
        logger.info(f"User balances migration completed. Updated {updated_count} documents.")
        
    except Exception as e:
        logger.error(f"Error in user_balances migration: {str(e)}")
        raise


async def migrate_merchants():
    """Migrate merchants collection to add wallet fields."""
    try:
        logger.info("Starting merchants migration...")
        
        database = mongodb.get_database()
        collection = database.merchants
        
        # Get all merchants
        cursor = collection.find({})
        updated_count = 0
        
        async for doc in cursor:
            # Check if wallet fields already exist
            if "wallet_balance" not in doc:
                # Update document with new fields
                update_data = {
                    "wallet_balance": 0.0,
                    "total_received": 0.0,
                    "updated_at": datetime.utcnow()
                }
                
                await collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": update_data}
                )
                updated_count += 1
                logger.info(f"Updated merchant: {doc.get('name', 'Unknown')}")
        
        logger.info(f"Merchants migration completed. Updated {updated_count} documents.")
        
    except Exception as e:
        logger.error(f"Error in merchants migration: {str(e)}")
        raise


async def migrate_transactions():
    """Migrate transactions collection to add wallet fields."""
    try:
        logger.info("Starting transactions migration...")
        
        database = mongodb.get_database()
        collection = database.transactions
        
        # Get all transactions
        cursor = collection.find({})
        updated_count = 0
        
        async for doc in cursor:
            # Check if wallet fields already exist
            if "total_amount" not in doc:
                # Calculate total amount (amount + fee_amount)
                amount = doc.get("amount", 0.0) or 0.0
                fee_amount = doc.get("fee_amount", 0.0) or 0.0
                total_amount = amount + fee_amount
                
                # Update document with new fields
                update_data = {
                    "total_amount": total_amount,
                    "merchant_wallet_balance_before": 0.0,
                    "merchant_wallet_balance_after": 0.0,
                    "user_credit_before": 0.0,
                    "user_credit_after": 0.0
                }
                
                await collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": update_data}
                )
                updated_count += 1
                logger.info(f"Updated transaction: {doc['_id']}")
        
        logger.info(f"Transactions migration completed. Updated {updated_count} documents.")
        
    except Exception as e:
        logger.error(f"Error in transactions migration: {str(e)}")
        raise


async def create_wallet_permissions():
    """Create new wallet-related permissions."""
    try:
        logger.info("Creating wallet permissions...")
        
        database = mongodb.get_database()
        rbac_repo = RBACRepository(database)
        
        # Define new wallet permissions
        wallet_permissions = [
            {
                "name": "wallet_read",
                "resource": "wallet",
                "action": "read",
                "description": "Read wallet information"
            },
            {
                "name": "wallet_write",
                "resource": "wallet",
                "action": "write",
                "description": "Write wallet information"
            },
            {
                "name": "credit_read",
                "resource": "credit",
                "action": "read",
                "description": "Read credit information"
            },
            {
                "name": "credit_write",
                "resource": "credit",
                "action": "write",
                "description": "Write credit information"
            },
            {
                "name": "wallet_transactions_read",
                "resource": "wallet_transactions",
                "action": "read",
                "description": "Read wallet transactions"
            },
            {
                "name": "wallet_transactions_write",
                "resource": "wallet_transactions",
                "action": "write",
                "description": "Write wallet transactions"
            }
        ]
        
        created_count = 0
        for perm_data in wallet_permissions:
            # Check if permission already exists
            existing_perm = await rbac_repo.get_permission_by_name(perm_data["name"])
            if not existing_perm:
                perm = Permission(**perm_data)
                await rbac_repo.create_permission(perm)
                created_count += 1
                logger.info(f"Created permission: {perm_data['name']}")
            else:
                logger.info(f"Permission already exists: {perm_data['name']}")
        
        logger.info(f"Wallet permissions creation completed. Created {created_count} new permissions.")
        
    except Exception as e:
        logger.error(f"Error creating wallet permissions: {str(e)}")
        raise


async def update_existing_roles():
    """Update existing roles with wallet permissions."""
    try:
        logger.info("Updating existing roles with wallet permissions...")
        
        database = mongodb.get_database()
        rbac_repo = RBACRepository(database)
        
        # Get wallet permissions
        wallet_permission_names = [
            "wallet_read", "wallet_write",
            "credit_read", "credit_write",
            "wallet_transactions_read", "wallet_transactions_write"
        ]
        
        wallet_permission_ids = []
        for perm_name in wallet_permission_names:
            perm = await rbac_repo.get_permission_by_name(perm_name)
            if perm:
                wallet_permission_ids.append(perm.id)
        
        # Update admin role with all wallet permissions
        admin_role = await rbac_repo.get_role_by_name("admin")
        if admin_role:
            current_permissions = admin_role.permissions
            new_permissions = list(set(current_permissions + wallet_permission_ids))
            
            if new_permissions != current_permissions:
                await rbac_repo.update_role(admin_role.id, {"permissions": new_permissions})
                logger.info("Updated admin role with wallet permissions")
        
        # Update merchant role with wallet permissions
        merchant_role = await rbac_repo.get_role_by_name("merchant")
        if merchant_role:
            merchant_permissions = [
                "wallet_read", "credit_read", "wallet_transactions_read"
            ]
            merchant_perm_ids = []
            for perm_name in merchant_permissions:
                perm = await rbac_repo.get_permission_by_name(perm_name)
                if perm:
                    merchant_perm_ids.append(perm.id)
            
            current_permissions = merchant_role.permissions
            new_permissions = list(set(current_permissions + merchant_perm_ids))
            
            if new_permissions != current_permissions:
                await rbac_repo.update_role(merchant_role.id, {"permissions": new_permissions})
                logger.info("Updated merchant role with wallet permissions")
        
        # Update user role with wallet permissions
        user_role = await rbac_repo.get_role_by_name("user")
        if user_role:
            user_permissions = [
                "wallet_read", "credit_read", "wallet_transactions_read"
            ]
            user_perm_ids = []
            for perm_name in user_permissions:
                perm = await rbac_repo.get_permission_by_name(perm_name)
                if perm:
                    user_perm_ids.append(perm.id)
            
            current_permissions = user_role.permissions
            new_permissions = list(set(current_permissions + user_perm_ids))
            
            if new_permissions != current_permissions:
                await rbac_repo.update_role(user_role.id, {"permissions": new_permissions})
                logger.info("Updated user role with wallet permissions")
        
        logger.info("Role updates completed.")
        
    except Exception as e:
        logger.error(f"Error updating roles: {str(e)}")
        raise


async def run_migration():
    """Run the complete migration."""
    try:
        logger.info("Starting wallet system migration...")
        
        # Connect to database
        await mongodb.connect()
        
        # Run migrations in order
        await migrate_user_balances()
        await migrate_merchants()
        await migrate_transactions()
        await create_wallet_permissions()
        await update_existing_roles()
        
        logger.info("🎉 Wallet system migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(run_migration())
