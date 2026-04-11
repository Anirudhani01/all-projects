#!/usr/bin/env python3
"""
Script to debug the user document and authentication issue
"""

import asyncio
import motor.motor_asyncio
import json

async def debug_user():
    """Debug the user document to understand the authentication issue."""
    
    print("🔍 Debugging user document...")
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
            
            # Show all fields with their types
            print("\n📋 All fields and their types:")
            print("-" * 40)
            for key, value in admin_user.items():
                value_type = type(value).__name__
                if key == "hashedPassword":
                    # Show first 20 chars of hashed password for security
                    display_value = str(value)[:20] + "..." if len(str(value)) > 20 else str(value)
                else:
                    display_value = str(value)
                print(f"   {key}: {display_value} ({value_type})")
            
            # Check if user has all required fields for authentication
            print(f"\n🔐 Authentication field check:")
            print("-" * 40)
            
            required_fields = ["email", "hashedPassword", "isActive"]
            missing_fields = []
            
            for field in required_fields:
                if field in admin_user:
                    value = admin_user[field]
                    if field == "isActive" and not value:
                        print(f"   ❌ {field}: {value} (User is inactive)")
                    else:
                        print(f"   ✅ {field}: {value}")
                else:
                    print(f"   ❌ {field}: Missing")
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n❌ Missing required fields: {missing_fields}")
            else:
                print(f"\n✅ All required fields present")
            
            # Test password verification
            print(f"\n🔑 Testing password verification...")
            try:
                from passlib.hash import bcrypt
                test_password = "admin1pass"
                stored_hash = admin_user.get("hashedPassword")
                
                if stored_hash:
                    is_valid = bcrypt.verify(test_password, stored_hash)
                    print(f"   Password 'admin1pass' verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
                else:
                    print(f"   ❌ No hashedPassword field found")
                    
            except Exception as e:
                print(f"   ❌ Error testing password: {e}")
            
        else:
            print("❌ Admin user not found!")
            
        client.close()
        
    except Exception as e:
        print(f"❌ Error debugging user: {e}")

if __name__ == "__main__":
    print("🚀 User Debug Script")
    print("=" * 50)
    asyncio.run(debug_user())
