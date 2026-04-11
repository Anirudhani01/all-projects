#!/usr/bin/env python3
"""
Test script for Reports endpoints.
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint."""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_get_available_merchants():
    """Test getting available merchants."""
    print("🔍 Testing get available merchants...")
    response = requests.get(f"{BASE_URL}/api/v1/reports/available-merchants")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_get_available_users():
    """Test getting available users."""
    print("🔍 Testing get available users...")
    response = requests.get(f"{BASE_URL}/api/v1/reports/available-users")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_fee_collection_report(merchant_name):
    """Test fee collection report."""
    print(f"🔍 Testing fee collection report for merchant: {merchant_name}")
    
    # Test without date filters
    response = requests.get(f"{BASE_URL}/api/v1/reports/fee/{merchant_name}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test with date filters
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/reports/fee/{merchant_name}",
        params=params
    )
    print(f"Status (with date filters): {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_user_dues_report(user_name):
    """Test user dues report."""
    print(f"🔍 Testing user dues report for user: {user_name}")
    
    # Test without details
    response = requests.get(f"{BASE_URL}/api/v1/reports/dues/{user_name}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test with details
    params = {"include_details": "true"}
    response = requests.get(
        f"{BASE_URL}/api/v1/reports/dues/{user_name}",
        params=params
    )
    print(f"Status (with details): {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_users_at_credit_limit():
    """Test users at credit limit report."""
    print("🔍 Testing users at credit limit report...")
    response = requests.get(f"{BASE_URL}/api/v1/reports/users-at-credit-limit")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_total_dues():
    """Test total dues report."""
    print("🔍 Testing total dues report...")
    
    # Test without inactive users
    response = requests.get(f"{BASE_URL}/api/v1/reports/total-dues")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test with inactive users
    params = {"include_inactive_users": "true"}
    response = requests.get(
        f"{BASE_URL}/api/v1/reports/total-dues",
        params=params
    )
    print(f"Status (with inactive users): {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_invalid_merchant():
    """Test fee collection report with invalid merchant."""
    print("🔍 Testing fee collection report with invalid merchant...")
    response = requests.get(f"{BASE_URL}/api/v1/reports/fee/invalid_merchant")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_invalid_user():
    """Test user dues report with invalid user."""
    print("🔍 Testing user dues report with invalid user...")
    response = requests.get(f"{BASE_URL}/api/v1/reports/dues/invalid_user")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def main():
    """Main test function."""
    print("🧪 Testing Reports Endpoints")
    print("=" * 50)
    
    # Test health check first
    test_health_check()
    
    # Test available merchants and users
    test_get_available_merchants()
    test_get_available_users()
    
    # Get available merchants and users for testing
    try:
        merchants_response = requests.get(f"{BASE_URL}/api/v1/reports/available-merchants")
        users_response = requests.get(f"{BASE_URL}/api/v1/reports/available-users")
        
        if merchants_response.status_code == 200:
            merchants = merchants_response.json()
            if merchants:
                test_fee_collection_report(merchants[0])
            else:
                print("⚠️  No merchants available for testing")
        
        if users_response.status_code == 200:
            users = users_response.json()
            if users:
                test_user_dues_report(users[0])
            else:
                print("⚠️  No users available for testing")
        
    except Exception as e:
        print(f"❌ Error getting available merchants/users: {e}")
    
    # Test reports that don't require specific merchants/users
    test_users_at_credit_limit()
    test_total_dues()
    
    # Test error cases
    test_invalid_merchant()
    test_invalid_user()
    
    print("✅ Reports endpoint testing completed!")

if __name__ == "__main__":
    main()
