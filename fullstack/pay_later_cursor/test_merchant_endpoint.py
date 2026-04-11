#!/usr/bin/env python3
"""
Script to test the merchant /me endpoint directly
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.mongo import mongodb
from app.modules.merchants.service import MerchantService
from app.modules.merchants.repository import MerchantRepository
from app.auth.repository import AuthRepository
from app.auth.service import AuthService
from app.auth.jwt_handler import JWTHandler

async def test_merchant_endpoint():
    """Test the merchant /me endpoint"""
    try:
        print("🧪 Testing merchant /me endpoint...")
        
        # Connect to database first
        await mongodb.connect()
        
        # Get database connection
        database = mongodb.get_database()
        
        # Get repositories and services
        merchant_repo = MerchantRepository(database)
        merchant_service = MerchantService(merchant_repo)
        auth_repo = AuthRepository(database)
        auth_service = AuthService(auth_repo)
        
        # Get user
        user = await auth_repo.get_user_by_email("ajio@gmail.com")
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ Found user: {user.email}")
        
        # Test getting merchant by email
        try:
            merchant = await merchant_service.get_merchant_by_email("ajio@gmail.com")
            print("✅ Merchant service.get_merchant_by_email() works:")
            print(f"  - ID: {merchant.id}")
            print(f"  - Name: {merchant.name}")
            print(f"  - Email: {merchant.email}")
            print(f"  - Merchant ID: {merchant.merchant_id}")
            print(f"  - Fee: {merchant.current_fee_pct}")
        except Exception as e:
            print(f"❌ Error in get_merchant_by_email: {str(e)}")
        
        # Test repository directly
        try:
            merchant = await merchant_repo.get_merchant_by_email("ajio@gmail.com")
            if merchant:
                print("✅ Repository.get_merchant_by_email() works:")
                print(f"  - ID: {merchant._id}")
                print(f"  - Name: {merchant.name}")
                print(f"  - Email: {merchant.email}")
            else:
                print("❌ Repository.get_merchant_by_email() returned None")
        except Exception as e:
            print(f"❌ Error in repository: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_merchant_endpoint())
