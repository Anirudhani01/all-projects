#!/usr/bin/env python3
"""
Test script to verify dashboard API endpoints are working correctly
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from app.auth.service import AuthService
from app.auth.repository import AuthRepository
from app.modules.users.service import UserService
from app.modules.merchants.service import MerchantService
from app.modules.transactions.service import TransactionService
from app.modules.reports.service import ReportService

async def test_dashboard_apis():
    """Test all dashboard API endpoints"""
    try:
        print("🔍 Testing Dashboard API Endpoints...")
        
        # Connect to database
        await mongodb.connect()
        database = mongodb.get_database()
        
        # Get services
        auth_repo = AuthRepository(database)
        auth_service = AuthService(auth_repo)
        user_service = UserService(database)
        merchant_service = MerchantService(database)
        transaction_service = TransactionService(database, user_service, merchant_service)
        report_service = ReportService(database)
        
        # Test 1: Get admin user and create token
        print("\n1️⃣ Testing Authentication...")
        admin_user = await auth_repo.get_user_by_email("admin@admin.com")
        if not admin_user:
            print("❌ Admin user not found")
            return
        
        print(f"✅ Found admin user: {admin_user.email}")
        
        # Test 2: Get users count
        print("\n2️⃣ Testing Users API...")
        try:
            users_response = await user_service.get_users_by_limit_status(
                reached_limit=None,
                page=1,
                size=10
            )
            print(f"✅ Users API working - Total users: {users_response.total}")
            print(f"   Users in response: {len(users_response.users)}")
        except Exception as e:
            print(f"❌ Users API error: {str(e)}")
        
        # Test 3: Get merchants count
        print("\n3️⃣ Testing Merchants API...")
        try:
            merchants_response = await merchant_service.get_all_merchants(
                page=1,
                size=10
            )
            print(f"✅ Merchants API working - Total merchants: {merchants_response.total}")
            print(f"   Merchants in response: {len(merchants_response.merchants)}")
        except Exception as e:
            print(f"❌ Merchants API error: {str(e)}")
        
        # Test 4: Get transactions count
        print("\n4️⃣ Testing Transactions API...")
        try:
            transactions_response = await transaction_service.get_transactions_with_filters(
                user_id=None,
                merchant_id=None,
                type=None,
                status=None,
                from_date=None,
                to_date=None,
                page=1,
                size=10
            )
            print(f"✅ Transactions API working - Total transactions: {transactions_response.total}")
            print(f"   Transactions in response: {len(transactions_response.transactions)}")
        except Exception as e:
            print(f"❌ Transactions API error: {str(e)}")
        
        # Test 5: Get total dues
        print("\n5️⃣ Testing Total Dues API...")
        try:
            dues_response = await report_service.get_total_dues_report(
                include_inactive_users=False
            )
            print(f"✅ Total Dues API working - Total dues: ₹{dues_response.total}")
            print(f"   Users with dues: {dues_response.total_users_with_dues}")
        except Exception as e:
            print(f"❌ Total Dues API error: {str(e)}")
        
        print("\n🎉 Dashboard API Testing Complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dashboard_apis())
