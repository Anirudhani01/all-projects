#!/usr/bin/env python3

import requests
import json

def test_repayment_simple():
    base_url = "http://localhost:8000/api/v1"
    
    # Login with the user
    login_data = {
        "email": "nani@gmail.com",
        "password": "nani123"
    }
    
    try:
        # Login
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            token = login_response["access_token"]
            user_id = login_response["user"]["user_id"]
            
            print(f"✅ Login successful! User ID: {user_id}")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test repayment of ₹200 (within the outstanding amount of ₹300)
            repayment_amount = 200.0
            custom_user_id = 60  # The custom user ID for nani@gmail.com
            
            print(f"\n🔄 Processing repayment of ₹{repayment_amount}...")
            
            # The endpoint expects the amount as a query parameter
            repay_response = requests.post(
                f"{base_url}/users/{custom_user_id}/repay?amount={repayment_amount}",
                headers=headers
            )
            
            print(f"Repayment Status: {repay_response.status_code}")
            print(f"Repayment Response: {repay_response.text}")
            
            if repay_response.status_code == 200:
                repay_result = repay_response.json()
                print(f"✅ Repayment successful!")
                print(f"   Repayment Amount: ₹{repay_result.get('repayment_amount')}")
                print(f"   New Outstanding Amount: ₹{repay_result.get('new_outstanding_amount')}")
                print(f"   New Bank Balance: ₹{repay_result.get('new_bank_balance')}")
                
            else:
                print(f"❌ Repayment failed: {repay_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_repayment_simple()
