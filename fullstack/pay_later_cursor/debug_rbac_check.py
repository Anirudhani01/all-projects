#!/usr/bin/env python3
"""
Script to debug the RBAC check for merchant role
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from app.rbac.repository import RBACRepository
from app.auth.repository import AuthRepository

async def debug_rbac_check():
    """Debug the RBAC check for merchant role"""
    try:
        print("🔍 Debugging RBAC check for merchant role...")
        
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
        try:
            has_merchant_role = await rbac_repo.check_user_role(str(user.user_id), "merchant")
            print(f"✅ RBAC check result: has_merchant_role = {has_merchant_role}")
            
            if not has_merchant_role:
                print("❌ User doesn't have merchant role - let's debug why...")
                
                # Get user roles
                user_roles = await rbac_repo.get_user_roles(str(user.user_id))
                print(f"📋 User roles: {len(user_roles)}")
                for ur in user_roles:
                    print(f"  - Role ID: {ur.role_id}")
                
                # Get merchant role
                merchant_role = await rbac_repo.get_role_by_name("merchant")
                if merchant_role:
                    print(f"✅ Merchant role exists: {merchant_role.id}")
                    
                    # Check if user has this specific role
                    for ur in user_roles:
                        if ur.role_id == merchant_role.id:
                            print("✅ User has merchant role assigned!")
                            break
                    else:
                        print("❌ User doesn't have merchant role assigned")
                else:
                    print("❌ Merchant role not found")
            else:
                print("✅ User has merchant role - RBAC check should work")
                
        except Exception as e:
            print(f"❌ Error in RBAC check: {str(e)}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_rbac_check())
