#!/usr/bin/env python3
"""
Script to check RBAC state and manually create merchant role
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from app.rbac.repository import RBACRepository
from app.rbac.models import Role, Permission, UserRole
from app.auth.repository import AuthRepository

async def check_and_fix_rbac():
    """Check RBAC state and fix if needed"""
    try:
        print("🔍 Checking RBAC system state...")
        
        # Connect to database first
        await mongodb.connect()
        
        # Get database connection
        database = mongodb.get_database()
        
        # Get repositories
        rbac_repo = RBACRepository(database)
        auth_repo = AuthRepository(database)
        
        # Check what roles exist
        print("\n📋 Checking existing roles...")
        roles_collection = database.get_collection("roles")
        roles = await roles_collection.find().to_list(length=None)
        print(f"Found {len(roles)} roles:")
        for role in roles:
            print(f"  - {role.get('name')}: {role.get('_id')}")
        
        # Check what permissions exist
        print("\n📋 Checking existing permissions...")
        permissions_collection = database.get_collection("permissions")
        permissions = await permissions_collection.find().to_list(length=None)
        print(f"Found {len(permissions)} permissions:")
        for perm in permissions:
            print(f"  - {perm.get('resource')}:{perm.get('action')}: {perm.get('_id')}")
        
        # If no roles exist, create them manually
        if not roles:
            print("\n🚀 Creating roles manually...")
            
            # Create permissions first
            merchant_permissions = [
                Permission(resource="transactions", action="read", description="Read transactions"),
                Permission(resource="transactions", action="write", description="Write transactions"),
                Permission(resource="reports", action="read", description="Read reports")
            ]
            
            created_permissions = []
            for perm in merchant_permissions:
                perm_id = await rbac_repo.create_permission(perm)
                created_permissions.append(perm_id)
                print(f"  ✅ Created permission: {perm.resource}:{perm.action}")
            
            # Create merchant role
            merchant_role = Role(
                name="merchant",
                description="Merchant role with transaction and report permissions",
                permissions=created_permissions
            )
            
            role_id = await rbac_repo.create_role(merchant_role)
            print(f"  ✅ Created merchant role: {role_id}")
        
        # Now assign the merchant role to ajio@gmail.com
        print("\n🔧 Assigning merchant role to ajio@gmail.com...")
        
        # Get the user
        user = await auth_repo.get_user_by_email("ajio@gmail.com")
        if not user:
            print("❌ User ajio@gmail.com not found in auth_users")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.user_id})")
        
        # Get merchant role
        merchant_role = await rbac_repo.get_role_by_name("merchant")
        if not merchant_role:
            print("❌ Merchant role not found - creating it...")
            # Create merchant role with basic permissions
            merchant_role = Role(
                name="merchant",
                description="Merchant role",
                permissions=[]
            )
            role_id = await rbac_repo.create_role(merchant_role)
            merchant_role.id = role_id
            print(f"✅ Created merchant role: {role_id}")
        
        print(f"✅ Found merchant role: {merchant_role.name} (ID: {merchant_role.id})")
        
        # Check if user already has the role
        existing_role = await rbac_repo.get_user_role(user.user_id, merchant_role.id)
        if existing_role:
            print("✅ User already has merchant role assigned")
        else:
            # Assign the role
            user_role = UserRole(
                user_id=user.user_id,
                role_id=merchant_role.id,
                assigned_by="system"
            )
            
            await rbac_repo.assign_role_to_user(user_role)
            print("✅ Merchant role assigned successfully!")
        
        # Verify the assignment
        assigned_roles = await rbac_repo.get_user_roles(user.user_id)
        print(f"📋 User roles: {[role.role_id for role in assigned_roles]}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_and_fix_rbac())
