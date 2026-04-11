#!/usr/bin/env python3
"""
Script to test merchant permissions and debug the 403 error
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from app.rbac.repository import RBACRepository
from app.auth.repository import AuthRepository

async def test_merchant_permissions():
    """Test merchant permissions and debug 403 error"""
    try:
        print("🔍 Testing merchant permissions...")
        
        # Connect to database first
        await mongodb.connect()
        
        # Get database connection
        database = mongodb.get_database()
        
        # Get repositories
        rbac_repo = RBACRepository(database)
        auth_repo = AuthRepository(database)
        
        # Get user
        user = await auth_repo.get_user_by_email("ajio@gmail.com")
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.user_id})")
        
        # Test RBAC check
        has_merchant_role = await rbac_repo.check_user_role(str(user.user_id), "merchant")
        print(f"✅ Has merchant role: {has_merchant_role}")
        
        # Get user permissions
        user_permissions = await rbac_repo.get_user_permissions(str(user.user_id))
        print(f"📋 User permissions: {user_permissions}")
        
        # Check specific permissions that might be needed
        merchants_read = await rbac_repo.check_user_permission(str(user.user_id), "merchants", "read")
        merchants_write = await rbac_repo.check_user_permission(str(user.user_id), "merchants", "write")
        transactions_read = await rbac_repo.check_user_permission(str(user.user_id), "transactions", "read")
        
        print(f"✅ merchants:read permission: {merchants_read}")
        print(f"✅ merchants:write permission: {merchants_write}")
        print(f"✅ transactions:read permission: {transactions_read}")
        
        # Check what the merchant endpoint actually requires
        print("\n🔍 Checking what the /merchants/me endpoint requires...")
        print("The endpoint uses require_merchant_role which calls require_role('merchant')")
        print("This should work if the user has the merchant role.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_merchant_permissions())
