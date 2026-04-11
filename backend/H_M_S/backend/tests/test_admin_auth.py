#!/usr/bin/env python3
"""Test admin authentication"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_auth():
    """Test admin authentication"""
    print("🔐 Testing Admin Authentication...")
    
    try:
        # Test login
        print("\n1. Testing admin login...")
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json={"username": "admin", "password": "admin123"})
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"   ✅ Login successful!")
            print(f"   Token: {token[:20]}...")
            print(f"   User: {data.get('user', {}).get('username')}")
            
            # Test protected endpoint
            print("\n2. Testing protected admin endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/api/admin/doctors/", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Admin access successful!")
                print(f"   Found {data.get('total', 0)} doctors")
            else:
                print(f"   ❌ Admin access failed: {response.text}")
                
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing admin auth: {e}")

if __name__ == "__main__":
    test_admin_auth()
