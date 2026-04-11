#!/usr/bin/env python3

import requests
import json

def test_dashboard_apis():
    base_url = "http://localhost:8000/api/v1"
    
    # Login as admin
    login_data = {
        "email": "admin@admin.com",
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
            if users_response.status_code == 200:
                users_data = users_response.json()
                print(f"✅ Users API Working! Found {users_data.get('total', 0)} users")
            else:
                print(f"❌ Users API Error: {users_response.text}")
            
            # Test Transactions API
            print(f"\n🔍 Testing Transactions API...")
            transactions_response = requests.get(f"{base_url}/transactions/", headers=headers)
            print(f"Transactions API Status: {transactions_response.status_code}")
            if transactions_response.status_code == 200:
                transactions_data = transactions_response.json()
                print(f"✅ Transactions API Working! Found {len(transactions_data.get('transactions', []))} transactions")
            else:
                print(f"❌ Transactions API Error: {transactions_response.text}")
            
            # Test Reports APIs
            print(f"\n🔍 Testing Reports APIs...")
            
            # Total Dues
            total_dues_response = requests.get(f"{base_url}/reports/total-dues", headers=headers)
            print(f"Total Dues API Status: {total_dues_response.status_code}")
            if total_dues_response.status_code == 200:
                total_dues_data = total_dues_response.json()
                print(f"✅ Total Dues API Working! Total: ₹{total_dues_data.get('total', 0)}")
            else:
                print(f"❌ Total Dues API Error: {total_dues_response.text}")
            
            # Users at Credit Limit
            users_at_limit_response = requests.get(f"{base_url}/reports/users-at-credit-limit", headers=headers)
            print(f"Users at Credit Limit API Status: {users_at_limit_response.status_code}")
            if users_at_limit_response.status_code == 200:
                users_at_limit_data = users_at_limit_response.json()
                print(f"✅ Users at Credit Limit API Working! Count: {users_at_limit_data.get('total_count', 0)}")
            else:
                print(f"❌ Users at Credit Limit API Error: {users_at_limit_response.text}")
            
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dashboard_apis()
