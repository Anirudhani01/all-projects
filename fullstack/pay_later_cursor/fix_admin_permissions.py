#!/usr/bin/env python3
"""
Script to check and fix admin permissions
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from app.rbac.repository import RBACRepository
from app.auth.repository import AuthRepository

async def fix_admin_permissions():
    """Check and fix admin permissions"""
    try:
        print("🔍 Checking admin permissions...")
        
        # Connect to database first
        await mongodb.connect()
        
        # Get database connection
        database = mongodb.get_database()
        
        # Get repositories
        rbac_repo = RBACRepository(database)
        auth_repo = AuthRepository(database)
        
        # Get admin user
        admin_user = await auth_repo.get_user_by_email("admin@admin.com")
        if not admin_user:
            print("❌ Admin user not found")
            return
        
        print(f"✅ Found admin user: {admin_user.email} (ID: {admin_user.user_id})")
        
        # Check if admin role exists
        admin_role = await rbac_repo.get_role_by_name("admin")
        if not admin_role:
            print("❌ Admin role not found in RBAC system")
            return
        
        print(f"✅ Found admin role: {admin_role.id}")
        print(f"📋 Current permissions: {admin_role.permissions}")
        
        # Check if admin user has admin role assigned
        has_admin_role = await rbac_repo.check_user_role(str(admin_user.user_id), "admin")
        print(f"✅ Admin user has admin role: {has_admin_role}")
        
        # Get admin user permissions
        admin_permissions = await rbac_repo.get_user_permissions(str(admin_user.user_id))
        print(f"📋 Admin user permissions: {admin_permissions}")
        
        # Check specific permissions that admin should have
        required_permissions = [
            ("users", "read"), ("users", "write"), ("users", "delete"),
            ("merchants", "read"), ("merchants", "write"), ("merchants", "delete"),
            ("transactions", "read"), ("transactions", "write"), ("transactions", "approve"),
            ("reports", "read"), ("reports", "export")
        ]
        
        print("\n🔍 Checking required permissions:")
        missing_permissions = []
        for resource, action in required_permissions:
            has_perm = await rbac_repo.check_user_permission(str(admin_user.user_id), resource, action)
            print(f"  {resource}:{action} - {'✅' if has_perm else '❌'}")
            if not has_perm:
                missing_permissions.append((resource, action))
        
        if missing_permissions:
            print(f"\n❌ Missing permissions: {missing_permissions}")
            print("🔧 Adding missing permissions to admin role...")
            
            # Get collections
            roles_collection = database.get_collection("roles")
            permissions_collection = database.get_collection("permissions")
            
            # Create missing permissions
            new_permission_ids = []
            for resource, action in missing_permissions:
                perm_name = f"{resource}_{action}"
                existing_perm = await permissions_collection.find_one({"name": perm_name})
                if existing_perm:
                    print(f"  ✅ Permission already exists: {perm_name}")
                    new_permission_ids.append(str(existing_perm["_id"]))
                else:
                    perm_data = {
                        "name": perm_name,
                        "resource": resource,
                        "action": action,
                        "description": f"{action.title()} {resource}",
                        "is_active": True
                    }
                    result = await permissions_collection.insert_one(perm_data)
                    new_permission_ids.append(str(result.inserted_id))
                    print(f"  ✅ Created permission: {perm_name}")
            
            # Update admin role with new permissions
            if new_permission_ids:
                current_permissions = admin_role.permissions.copy()
                current_permissions.extend(new_permission_ids)
                unique_permissions = list(set(current_permissions))
                
                await roles_collection.update_one(
                    {"_id": admin_role.id},
                    {"$set": {"permissions": unique_permissions}}
                )
                
                print(f"✅ Updated admin role with {len(unique_permissions)} permissions")
        else:
            print("\n✅ All required permissions are present!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_admin_permissions())
