#!/usr/bin/env python3

import requests
import json

def test_complete_repayment():
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
            custom_user_id = 60
            
            # Test final repayment of remaining ₹100
            repayment_amount = 100.0
            
            print(f"\n🔄 Processing final repayment of ₹{repayment_amount}...")
            
            repay_response = requests.post(
                f"{base_url}/users/{custom_user_id}/repay?amount={repayment_amount}",
                headers=headers
            )
            
            print(f"Repayment Status: {repay_response.status_code}")
            print(f"Repayment Response: {repay_response.text}")
            
            if repay_response.status_code == 200:
                repay_result = repay_response.json()
                print(f"✅ Final repayment successful!")
                print(f"   Repayment Amount: ₹{repay_result.get('repayment_amount')}")
                print(f"   New Outstanding Amount: ₹{repay_result.get('new_outstanding_amount')}")
                print(f"   New Bank Balance: ₹{repay_result.get('new_bank_balance')}")
                
                print(f"\n🎉 **COMPLETE REPAYMENT SUCCESSFUL!** 🎉")
                print(f"   User has fully repaid their outstanding amount!")
                print(f"   Outstanding Amount: ₹{repay_result.get('new_outstanding_amount')}")
                print(f"   Available Credit: ₹{2000 - repay_result.get('new_outstanding_amount')}")
                
            else:
                print(f"❌ Repayment failed: {repay_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_complete_repayment()
