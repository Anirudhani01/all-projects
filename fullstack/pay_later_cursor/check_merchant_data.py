#!/usr/bin/env python3
"""
Script to check merchant data and debug the /me endpoint issue
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb

async def check_merchant_data():
    """Check merchant data in database"""
    try:
        print("🔍 Checking merchant data in database...")
        
        # Connect to database first
        await mongodb.connect()
        
        # Get database connection
        database = mongodb.get_database()
        
        # Check merchant with email ajio@gmail.com
        merchants_collection = database.get_collection("merchants")
        merchant = await merchants_collection.find_one({"email": "ajio@gmail.com"})
        
        if merchant:
            print("✅ Found merchant in database:")
            print(f"  - ID: {merchant['_id']}")
            print(f"  - Name: {merchant['name']}")
            print(f"  - Email: {merchant['email']}")
            print(f"  - Custom Merchant ID: {merchant.get('custom_merchant_id')}")
            print(f"  - Fee: {merchant['current_fee_pct']}")
        else:
            print("❌ No merchant found with email ajio@gmail.com")
            
            # Check all merchants
            all_merchants = await merchants_collection.find().to_list(length=None)
            print(f"\n📋 Found {len(all_merchants)} merchants in database:")
            for m in all_merchants:
                print(f"  - {m['name']} (email: {m.get('email', 'NO EMAIL')})")
        
        # Check user roles
        print("\n🔍 Checking user roles...")
        user_roles_collection = database.get_collection("user_roles")
        user_roles = await user_roles_collection.find().to_list(length=None)
        print(f"Found {len(user_roles)} user role assignments:")
        for ur in user_roles:
            print(f"  - User ID: {ur['user_id']}, Role ID: {ur['role_id']}")
        
        # Check roles
        print("\n🔍 Checking roles...")
        roles_collection = database.get_collection("roles")
        roles = await roles_collection.find().to_list(length=None)
        print(f"Found {len(roles)} roles:")
        for role in roles:
            print(f"  - {role['name']}: {role['_id']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_merchant_data())
