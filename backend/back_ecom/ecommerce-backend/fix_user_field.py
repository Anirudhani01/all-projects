#!/usr/bin/env python3
"""
Script to fix the hashedPassword field name mismatch
"""

import asyncio
import motor.motor_asyncio

async def fix_user_field():
    """Fix the hashedPassword field name in the database."""
    
    print("🔧 Fixing user field name mismatch...")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.ecommerce_dev
        users_collection = db.users
        
        # Find the admin user
        admin_user = await users_collection.find_one({"email": "admin1@gmail.com"})
        
        if admin_user:
            print(f"👤 Found admin user: {admin_user.get('email')}")
            
            # Check current field names
            print("\n📋 Current field names:")
            for key in admin_user.keys():
                print(f"   - {key}")
            
            # Fix the field name
            if "hashed_password" in admin_user:
                print(f"\n🔄 Fixing field name from 'hashed_password' to 'hashedPassword'...")
                
                # Update the document
                result = await users_collection.update_one(
                    {"email": "admin1@gmail.com"},
                    {
                        "$rename": {"hashed_password": "hashedPassword"},
                        "$set": {"updatedAt": admin_user.get("updatedAt")}
                    }
                )
                
                if result.modified_count > 0:
                    print("✅ Field name fixed successfully!")
                    
                    # Verify the fix
                    updated_user = await users_collection.find_one({"email": "admin1@gmail.com"})
                    print(f"\n📋 Updated field names:")
                    for key in updated_user.keys():
                        print(f"   - {key}")
                        
                    print(f"\n🎯 You can now login with:")
                    print(f"   📧 Email: admin1@gmail.com")
                    print(f"   🔑 Password: admin1pass")
                else:
                    print("❌ Failed to update field name")
            else:
                print("✅ Field name is already correct (hashedPassword)")
                
        else:
            print("❌ Admin user not found!")
            
        client.close()
        
    except Exception as e:
        print(f"❌ Error fixing user field: {e}")

if __name__ == "__main__":
    print("🚀 User Field Fix Script")
    print("=" * 50)
    asyncio.run(fix_user_field())
