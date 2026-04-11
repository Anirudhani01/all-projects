#!/usr/bin/env python3
"""
Script to directly add missing permissions to the merchant role
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from bson import ObjectId

async def fix_merchant_permissions_direct():
    """Add missing permissions to merchant role directly"""
    try:
        print("🔧 Adding missing permissions to merchant role directly...")
        
        # Connect to database first
        await mongodb.connect()
        
        # Get database connection
        database = mongodb.get_database()
        
        # Get collections
        roles_collection = database.get_collection("roles")
        permissions_collection = database.get_collection("permissions")
        
        # Get merchant role
        merchant_role = await roles_collection.find_one({"name": "merchant"})
        if not merchant_role:
            print("❌ Merchant role not found")
            return
        
        print(f"✅ Found merchant role: {merchant_role['_id']}")
        print(f"📋 Current permissions: {merchant_role.get('permissions', [])}")
        
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
            existing_perm = await permissions_collection.find_one({"name": perm_data["name"]})
            if existing_perm:
                print(f"✅ Permission already exists: {perm_data['name']}")
                new_permission_ids.append(str(existing_perm["_id"]))
            else:
                result = await permissions_collection.insert_one(perm_data)
                new_permission_ids.append(str(result.inserted_id))
                print(f"✅ Created permission: {perm_data['name']}")
        
        # Update merchant role with new permissions
        if new_permission_ids:
            current_permissions = merchant_role.get("permissions", []).copy()
            current_permissions.extend(new_permission_ids)
            
            # Remove duplicates
            unique_permissions = list(set(current_permissions))
            
            await roles_collection.update_one(
                {"_id": merchant_role["_id"]},
                {"$set": {"permissions": unique_permissions}}
            )
            
            print(f"✅ Updated merchant role with {len(unique_permissions)} permissions")
            print(f"📋 New permissions: {unique_permissions}")
        else:
            print("✅ No new permissions needed")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_merchant_permissions_direct())
