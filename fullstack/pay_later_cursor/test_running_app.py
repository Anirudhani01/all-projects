#!/usr/bin/env python3
"""
Simple test script to test the running FastAPI application via HTTP requests.
This avoids the ModuleNotFoundError by not importing the app modules directly.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_user_endpoints():
    """Test user endpoints"""
    print("\n👤 Testing User Endpoints...")
    
    # Test 1: Create a user
    print("   📝 Creating user...")
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "credit_limit": 1000.0
    }
    
    try:
        response = requests.post(f"{API_BASE}/users/", json=user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            user_response = response.json()
            print(f"   User created: {user_response.get('user_id', 'N/A')}")
            user_id = user_response.get('user_id')
            
            # Test 2: Get user by ID
            print("   📖 Getting user by ID...")
            response = requests.get(f"{API_BASE}/users/{user_id}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   User retrieved: {response.json().get('name')}")
            
            # Test 3: Get user dues
            print("   💰 Getting user dues...")
            response = requests.get(f"{API_BASE}/users/{user_id}/dues")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                dues = response.json()
                print(f"   Dues: {dues.get('total_due', 0)}")
            
            return True
        else:
            print(f"   ❌ Failed to create user: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_merchant_endpoints():
    """Test merchant endpoints"""
    print("\n🏪 Testing Merchant Endpoints...")
    
    # Test 1: Create a merchant
    print("   📝 Creating merchant...")
    merchant_data = {
        "name": "Test Merchant",
        "current_fee_pct": 2.5
    }
    
    try:
        response = requests.post(f"{API_BASE}/merchants/", json=merchant_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            merchant_response = response.json()
            print(f"   Merchant created: {merchant_response.get('merchant_id', 'N/A')}")
            merchant_id = merchant_response.get('merchant_id')
            
            # Test 2: Get merchant by ID
            print("   📖 Getting merchant by ID...")
            response = requests.get(f"{API_BASE}/merchants/{merchant_id}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Merchant retrieved: {response.json().get('name')}")
            
            # Test 3: Update merchant fee
            print("   💰 Updating merchant fee...")
            fee_data = {"new_fee_pct": 3.0}
            response = requests.patch(f"{API_BASE}/merchants/{merchant_id}/fee", json=fee_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Fee updated: {response.json().get('current_fee_pct')}%")
            
            return True
        else:
            print(f"   ❌ Failed to create merchant: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_transaction_endpoints():
    """Test transaction endpoints"""
    print("\n💳 Testing Transaction Endpoints...")
    
    # First create a user and merchant for testing
    print("   📝 Creating test user and merchant...")
    
    # Create user
    user_data = {"name": "Transaction User", "email": "txn@example.com", "credit_limit": 2000.0}
    user_response = requests.post(f"{API_BASE}/users/", json=user_data)
    if user_response.status_code != 201:
        print("   ❌ Failed to create test user")
        return False
    user_id = user_response.json().get('user_id')
    
    # Create merchant
    merchant_data = {"name": "Transaction Merchant", "current_fee_pct": 2.0}
    merchant_response = requests.post(f"{API_BASE}/merchants/", json=merchant_data)
    if merchant_response.status_code != 201:
        print("   ❌ Failed to create test merchant")
        return False
    merchant_id = merchant_response.json().get('merchant_id')
    
    print(f"   ✅ Test user: {user_id}, Test merchant: {merchant_id}")
    
    # Test 1: Purchase transaction
    print("   🛒 Testing purchase transaction...")
    purchase_data = {
        "user_id": user_id,
        "merchant_id": merchant_id,
        "amount": 150.0,
        "description": "Test purchase"
    }
    
    try:
        response = requests.post(f"{API_BASE}/transactions/purchase", json=purchase_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            purchase_response = response.json()
            transaction_id = purchase_response.get('id')
            print(f"   Purchase successful: {transaction_id}")
            
            # Test 2: Get transaction by ID
            print("   📖 Getting transaction by ID...")
            response = requests.get(f"{API_BASE}/transactions/{transaction_id}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                txn = response.json()
                print(f"   Transaction: {txn.get('type')} - {txn.get('amount')}")
            
            # Test 3: Get transactions list
            print("   📋 Getting transactions list...")
            response = requests.get(f"{API_BASE}/transactions/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                transactions = response.json()
                print(f"   Found {len(transactions.get('transactions', []))} transactions")
            
            # Test 4: Get transaction summary
            print("   📊 Getting transaction summary...")
            response = requests.get(f"{API_BASE}/transactions/summary")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                summary = response.json()
                print(f"   Summary: {summary.get('total_transactions', 0)} transactions")
            
            # Test 5: Payment transaction
            print("   💰 Testing payment transaction...")
            payment_data = {
                "user_id": user_id,
                "amount": 50.0,
                "description": "Test payment"
            }
            
            response = requests.post(f"{API_BASE}/transactions/payment", json=payment_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                print("   Payment successful")
            
            return True
        else:
            print(f"   ❌ Failed to create purchase: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting API Tests...")
    print(f"📍 Testing application at: {BASE_URL}")
    print("=" * 50)
    
    # Wait a moment for the app to be ready
    time.sleep(2)
    
    results = []
    
    # Test health endpoint
    results.append(("Health", test_health_endpoint()))
    
    # Test user endpoints
    results.append(("Users", test_user_endpoints()))
    
    # Test merchant endpoints
    results.append(("Merchants", test_merchant_endpoints()))
    
    # Test transaction endpoints
    results.append(("Transactions", test_transaction_endpoints()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:12} : {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the application logs for details.")

if __name__ == "__main__":
    main()
