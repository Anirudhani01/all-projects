#!/usr/bin/env python3
"""
Script to manually assign merchant role to ajio@gmail.com
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from app.rbac.repository import RBACRepository
from app.rbac.models import UserRole
from app.auth.repository import AuthRepository

async def fix_merchant_role():
    """Assign merchant role to ajio@gmail.com"""
    try:
        # Get database connection
        database = mongodb.get_database()
        
        # Get repositories
        rbac_repo = RBACRepository(database)
        auth_repo = AuthRepository(database)
        
        # Get the user
        user = await auth_repo.get_user_by_email("ajio@gmail.com")
        if not user:
            print("❌ User ajio@gmail.com not found")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.user_id})")
        
        # Get merchant role
        merchant_role = await rbac_repo.get_role_by_name("merchant")
        if not merchant_role:
            print("❌ Merchant role not found in RBAC system")
            return
        
        print(f"✅ Found merchant role: {merchant_role.name} (ID: {merchant_role.id})")
        
        # Check if user already has merchant role
        has_role = await rbac_repo.check_user_role(str(user.user_id), "merchant")
        if has_role:
            print("✅ User already has merchant role")
            return
        
        # Assign merchant role
        user_role = UserRole(
            user_id=user.user_id,
            role_id=merchant_role.id,
            assigned_by="manual_fix"
        )
        
        await rbac_repo.assign_role_to_user(user_role)
        print("✅ Merchant role assigned successfully!")
        
        # Verify the assignment
        has_role = await rbac_repo.check_user_role(str(user.user_id), "merchant")
        if has_role:
            print("✅ Verification: User now has merchant role")
        else:
            print("❌ Verification failed: User still doesn't have merchant role")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_merchant_role())
