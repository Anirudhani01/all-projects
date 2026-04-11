#!/usr/bin/env python3

import requests
import json

def test_repayment_direct():
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
            
            print(f"✅ Login successful!")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test repayment of ₹200
            repayment_amount = 200.0
            custom_user_id = 60
            
            print(f"\n🔄 Testing repayment endpoint directly...")
            print(f"URL: {base_url}/users/{custom_user_id}/repay?amount={repayment_amount}")
            
            # Test the endpoint
            repay_response = requests.post(
                f"{base_url}/users/{custom_user_id}/repay?amount={repayment_amount}",
                headers=headers
            )
            
            print(f"Repayment Status: {repay_response.status_code}")
            print(f"Repayment Headers: {dict(repay_response.headers)}")
            print(f"Repayment Response: {repay_response.text}")
            
            if repay_response.status_code == 200:
                repay_result = repay_response.json()
                print(f"✅ Repayment successful!")
                print(f"   Repayment Amount: ₹{repay_result.get('repayment_amount')}")
                print(f"   New Outstanding Amount: ₹{repay_result.get('new_outstanding_amount')}")
                print(f"   New Bank Balance: ₹{repay_result.get('new_bank_balance')}")
                
            elif repay_response.status_code == 403:
                print(f"❌ Forbidden - Authentication issue")
            elif repay_response.status_code == 400:
                print(f"❌ Bad Request - Validation issue")
            else:
                print(f"❌ Unexpected status code: {repay_response.status_code}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_repayment_direct()
