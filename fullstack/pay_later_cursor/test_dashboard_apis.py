#!/usr/bin/env python3

import requests
import json

def test_dashboard_apis():
    base_url = "http://localhost:8000/api/v1"
    
    # Login as admin
    login_data = {
        "email": "admin@paylater.com",
        "password": "admin123"
    }
    
    try:
        # Login
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            token = login_response["access_token"]
            
            print(f"✅ Login successful!")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test Users API
            print(f"\n🔍 Testing Users API...")
            users_response = requests.get(f"{base_url}/users/", headers=headers)
            print(f"Users API Status: {users_response.status_code}")
            print(f"Users API Response: {users_response.text[:200]}...")
            
            # Test Transactions API
            print(f"\n🔍 Testing Transactions API...")
            transactions_response = requests.get(f"{base_url}/transactions/", headers=headers)
            print(f"Transactions API Status: {transactions_response.status_code}")
            print(f"Transactions API Response: {transactions_response.text[:200]}...")
            
            # Test Reports APIs
            print(f"\n🔍 Testing Reports APIs...")
            
            # Total Dues
            total_dues_response = requests.get(f"{base_url}/reports/total-dues", headers=headers)
            print(f"Total Dues API Status: {total_dues_response.status_code}")
            print(f"Total Dues API Response: {total_dues_response.text[:200]}...")
            
            # Users at Credit Limit
            users_at_limit_response = requests.get(f"{base_url}/reports/users-at-credit-limit", headers=headers)
            print(f"Users at Credit Limit API Status: {users_at_limit_response.status_code}")
            print(f"Users at Credit Limit API Response: {users_at_limit_response.text[:200]}...")
            
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dashboard_apis()
