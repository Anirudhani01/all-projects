#!/usr/bin/env python3

import requests
import json

def test_user_credit():
    # Login to get fresh token
    login_data = {
        "email": "nani@gmail.com",
        "password": "nani123"
    }
    
    try:
        # Login
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            token = login_response["access_token"]
            user_id = login_response["user"]["user_id"]
            
            print(f"✅ Login successful! User ID: {user_id}")
            
            # Test user credit endpoint
            headers = {"Authorization": f"Bearer {token}"}
            credit_response = requests.get(f"http://localhost:8000/api/v1/wallet/user-credit/{user_id}", headers=headers)
            
            print(f"Credit Endpoint Status: {credit_response.status_code}")
            print(f"Credit Response: {credit_response.text}")
            
            if credit_response.status_code == 200:
                credit_data = credit_response.json()
                print(f"✅ Credit info retrieved successfully!")
                print(f"   Credit Limit: ₹{credit_data.get('credit_limit', 0)}")
                print(f"   Available Credit: ₹{credit_data.get('available_credit', 0)}")
                print(f"   Outstanding Amount: ₹{credit_data.get('outstanding_amount', 0)}")
            else:
                print(f"❌ Failed to get credit info: {credit_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_user_credit()
