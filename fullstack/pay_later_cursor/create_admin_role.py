#!/usr/bin/env python3
"""
Script to create admin role and assign it to admin user
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from app.rbac.repository import RBACRepository
from app.auth.repository import AuthRepository
from app.rbac.models import Role, Permission, UserRole

async def create_admin_role():
    """Create admin role and assign to admin user"""
    try:
        print("🔧 Creating admin role and assigning to admin user...")
        
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
        
        # Create admin permissions
        admin_permissions = [
            {"name": "users_read", "resource": "users", "action": "read", "description": "Read users", "is_active": True},
            {"name": "users_write", "resource": "users", "action": "write", "description": "Write users", "is_active": True},
            {"name": "users_delete", "resource": "users", "action": "delete", "description": "Delete users", "is_active": True},
            {"name": "merchants_read", "resource": "merchants", "action": "read", "description": "Read merchants", "is_active": True},
            {"name": "merchants_write", "resource": "merchants", "action": "write", "description": "Write merchants", "is_active": True},
            {"name": "merchants_delete", "resource": "merchants", "action": "delete", "description": "Delete merchants", "is_active": True},
            {"name": "transactions_read", "resource": "transactions", "action": "read", "description": "Read transactions", "is_active": True},
            {"name": "transactions_write", "resource": "transactions", "action": "write", "description": "Write transactions", "is_active": True},
            {"name": "transactions_approve", "resource": "transactions", "action": "approve", "description": "Approve transactions", "is_active": True},
            {"name": "reports_read", "resource": "reports", "action": "read", "description": "Read reports", "is_active": True},
            {"name": "reports_export", "resource": "reports", "action": "export", "description": "Export reports", "is_active": True}
        ]
        
        # Create permissions
        permission_ids = []
        for perm_data in admin_permissions:
            existing_perm = await rbac_repo.get_permission_by_name(perm_data["name"])
            if existing_perm:
                permission_ids.append(existing_perm.id)
                print(f"  ✅ Permission already exists: {perm_data['name']}")
            else:
                perm = Permission(**perm_data)
                perm_id = await rbac_repo.create_permission(perm)
                permission_ids.append(perm_id)
                print(f"  ✅ Created permission: {perm_data['name']}")
        
        # Create admin role
        admin_role_data = {
            "name": "admin",
            "description": "Administrator role with full system access",
            "permissions": permission_ids,
            "is_active": True
        }
        
        admin_role = await rbac_repo.get_role_by_name("admin")
        if admin_role:
            print(f"  ✅ Admin role already exists: {admin_role.id}")
            role_id = admin_role.id
        else:
            role = Role(**admin_role_data)
            role_id = await rbac_repo.create_role(role)
            print(f"  ✅ Created admin role: {role_id}")
        
        # Assign admin role to admin user
        existing_user_role = await rbac_repo.get_user_roles(str(admin_user.user_id))
        has_admin_role = any(ur.role_id == role_id for ur in existing_user_role)
        
        if has_admin_role:
            print("  ✅ Admin user already has admin role assigned")
        else:
            user_role = UserRole(
                user_id=str(admin_user.user_id),
                role_id=role_id,
                assigned_by="system"
            )
            await rbac_repo.assign_role_to_user(user_role)
            print("  ✅ Assigned admin role to admin user")
        
        print("\n🎉 Success! Admin role is now created and assigned.")
        print("Now try logging in with admin@admin.com and accessing the admin pages!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_admin_role())
