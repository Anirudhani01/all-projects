#!/usr/bin/env python3
"""
Simple test to check dashboard data in database
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb

async def check_dashboard_data():
    """Check if dashboard data exists in database"""
    try:
        print("🔍 Checking Dashboard Data in Database...")
        
        # Connect to database
        await mongodb.connect()
        database = mongodb.get_database()
        
        # Check users count
        users_collection = database.get_collection("users")
        users_count = await users_collection.count_documents({})
        print(f"👥 Total Users in Database: {users_count}")
        
        # Check merchants count
        merchants_collection = database.get_collection("merchants")
        merchants_count = await merchants_collection.count_documents({})
        print(f"🏪 Total Merchants in Database: {merchants_count}")
        
        # Check transactions count
        transactions_collection = database.get_collection("transactions")
        transactions_count = await transactions_collection.count_documents({})
        print(f"💳 Total Transactions in Database: {transactions_count}")
        
        # Check user balances for total dues
        user_balances_collection = database.get_collection("user_balances")
        total_dues = 0
        async for balance in user_balances_collection.find({}):
            total_dues += balance.get("outstanding_amount", 0)
        print(f"💰 Total Dues in Database: ₹{total_dues:.2f}")
        
        print("\n📊 Dashboard Data Summary:")
        print(f"   Users: {users_count}")
        print(f"   Merchants: {merchants_count}")
        print(f"   Transactions: {transactions_count}")
        print(f"   Total Dues: ₹{total_dues:.2f}")
        
        if users_count == 0 and merchants_count == 0 and transactions_count == 0:
            print("\n⚠️  WARNING: No data found in database!")
            print("   The dashboard will show 0 values because there's no data.")
        else:
            print("\n✅ Data found in database!")
            print("   The dashboard should show these values if API calls work correctly.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_dashboard_data())
