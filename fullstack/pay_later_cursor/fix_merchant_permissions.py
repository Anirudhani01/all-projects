#!/usr/bin/env python3
"""
Script to add missing permissions to the merchant role
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from app.rbac.repository import RBACRepository

async def fix_merchant_permissions():
    """Add missing permissions to merchant role"""
    try:
        print("🔧 Adding missing permissions to merchant role...")
        
        # Connect to database first
        await mongodb.connect()
        
        # Get database connection
        database = mongodb.get_database()
        
        # Get repository
        rbac_repo = RBACRepository(database)
        
        # Get merchant role
        merchant_role = await rbac_repo.get_role_by_name("merchant")
        if not merchant_role:
            print("❌ Merchant role not found")
            return
        
        print(f"✅ Found merchant role: {merchant_role.id}")
        print(f"📋 Current permissions: {merchant_role.permissions}")
        
        # Create missing permissions
        missing_permissions = [
            {
                "name": "merchants_read",
                "resource": "merchants",
                "action": "read",
                "description": "Read merchant data",
                "is_active": True
            },
            {
                "name": "merchants_write",
                "resource": "merchants", 
                "action": "write",
                "description": "Write merchant data",
                "is_active": True
            }
        ]
        
        # Add missing permissions
        new_permission_ids = []
        for perm_data in missing_permissions:
            # Check if permission already exists
            existing_perm = await rbac_repo.get_permission_by_name(perm_data["name"])
            if existing_perm:
                print(f"✅ Permission already exists: {perm_data['name']}")
                new_permission_ids.append(existing_perm.id)
            else:
                from app.rbac.models import Permission
                perm = Permission(**perm_data)
                perm_id = await rbac_repo.create_permission(perm)
                new_permission_ids.append(perm_id)
                print(f"✅ Created permission: {perm_data['name']}")
        
        # Update merchant role with new permissions
        if new_permission_ids:
            current_permissions = merchant_role.permissions.copy()
            current_permissions.extend(new_permission_ids)
            
            # Remove duplicates
            unique_permissions = list(set(current_permissions))
            
            await rbac_repo.update_role(merchant_role.id, {
                "permissions": unique_permissions
            })
            
            print(f"✅ Updated merchant role with {len(unique_permissions)} permissions")
            print(f"📋 New permissions: {unique_permissions}")
        else:
            print("✅ No new permissions needed")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_merchant_permissions())
