#!/usr/bin/env python3
"""
Simple script to create merchant role and assign it to ajio@gmail.com
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb

async def fix_merchant_role():
    """Create merchant role and assign to ajio@gmail.com"""
    try:
        print("🔧 Creating merchant role and assigning to ajio@gmail.com...")
        
        # Connect to database first
        await mongodb.connect()
        
        # Get database connection
        database = mongodb.get_database()
        
        # Check if merchant role already exists
        roles_collection = database.get_collection("roles")
        existing_role = await roles_collection.find_one({"name": "merchant"})
        
        if existing_role:
            role_id = str(existing_role["_id"])
            print(f"  ✅ Merchant role already exists: {role_id}")
        else:
            # Create permissions directly in database
            permissions_collection = database.get_collection("permissions")
            
            # Create merchant permissions (check if they exist first)
            merchant_permissions = [
                {
                    "name": "transactions_read",
                    "resource": "transactions",
                    "action": "read",
                    "description": "Read transactions",
                    "is_active": True
                },
                {
                    "name": "transactions_write", 
                    "resource": "transactions",
                    "action": "write",
                    "description": "Write transactions",
                    "is_active": True
                },
                {
                    "name": "reports_read",
                    "resource": "reports", 
                    "action": "read",
                    "description": "Read reports",
                    "is_active": True
                }
            ]
            
            # Insert permissions (use upsert to avoid duplicates)
            permission_ids = []
            for perm in merchant_permissions:
                # Check if permission exists
                existing_perm = await permissions_collection.find_one({"name": perm["name"]})
                if existing_perm:
                    permission_ids.append(str(existing_perm["_id"]))
                    print(f"  ✅ Permission already exists: {perm['name']}")
                else:
                    result = await permissions_collection.insert_one(perm)
                    permission_ids.append(str(result.inserted_id))
                    print(f"  ✅ Created permission: {perm['name']}")
            
            # Create merchant role
            merchant_role = {
                "name": "merchant",
                "description": "Merchant role with transaction and report permissions",
                "permissions": permission_ids,
                "is_active": True
            }
            
            role_result = await roles_collection.insert_one(merchant_role)
            role_id = str(role_result.inserted_id)
            print(f"  ✅ Created merchant role: {role_id}")
        
        # Get user ID for ajio@gmail.com
        auth_users_collection = database.get_collection("auth_users")
        user = await auth_users_collection.find_one({"email": "ajio@gmail.com"})
        if not user:
            print("❌ User ajio@gmail.com not found")
            return
        
        user_id = str(user["_id"])
        print(f"  ✅ Found user: {user['email']} (ID: {user_id})")
        
        # Check if user already has the role
        user_roles_collection = database.get_collection("user_roles")
        existing_user_role = await user_roles_collection.find_one({
            "user_id": user_id,
            "role_id": role_id
        })
        
        if existing_user_role:
            print("  ✅ User already has merchant role assigned")
        else:
            # Assign role to user
            user_role = {
                "user_id": user_id,
                "role_id": role_id,
                "assigned_by": "system",
                "is_active": True
            }
            
            await user_roles_collection.insert_one(user_role)
            print("  ✅ Assigned merchant role to user")
        
        print("\n🎉 Success! Merchant role is now assigned.")
        print("Now try logging in with ajio@gmail.com and accessing /merchants")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_merchant_role())
