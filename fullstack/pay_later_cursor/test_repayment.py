#!/usr/bin/env python3

import requests
import json

def test_repayment():
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
            
            # Get user's financial summary before repayment
            print(f"\n💰 Getting user's financial summary...")
            custom_user_id = 60
            summary_response = requests.get(f"{base_url}/users/{custom_user_id}/financial-summary", headers=headers)
            
            if summary_response.status_code == 200:
                summary = summary_response.json()
                print(f"✅ Financial Summary:")
                print(f"   Credit Limit: ₹{summary['credit']['credit_limit']}")
                print(f"   Available Credit: ₹{summary['credit']['available_credit']}")
                print(f"   Outstanding Amount: ₹{summary['credit']['outstanding_amount']}")
                print(f"   Bank Balance: ₹{summary['bank']['balance']}")
            
            # Test repayment of ₹500
            repayment_amount = 500.0
            
            print(f"\n🔄 Processing repayment of ₹{repayment_amount}...")
            
            # Use the custom user ID (60) instead of the MongoDB ObjectId
            custom_user_id = 60
            
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
                
                # Get updated financial summary
                print(f"\n💰 Getting updated financial summary...")
                summary_after_response = requests.get(f"{base_url}/users/{custom_user_id}/financial-summary", headers=headers)
                
                if summary_after_response.status_code == 200:
                    summary_after = summary_after_response.json()
                    print(f"✅ Updated Financial Summary:")
                    print(f"   Credit Limit: ₹{summary_after['credit']['credit_limit']}")
                    print(f"   Available Credit: ₹{summary_after['credit']['available_credit']}")
                    print(f"   Outstanding Amount: ₹{summary_after['credit']['outstanding_amount']}")
                    print(f"   Bank Balance: ₹{summary_after['bank']['balance']}")
                    
                    # Verify the changes
                    outstanding_decrease = summary['credit']['outstanding_amount'] - summary_after['credit']['outstanding_amount']
                    bank_decrease = summary['bank']['balance'] - summary_after['bank']['balance']
                    available_increase = summary_after['credit']['available_credit'] - summary['credit']['available_credit']
                    
                    print(f"\n✅ Verification:")
                    print(f"   Outstanding Amount Decrease: ₹{outstanding_decrease}")
                    print(f"   Bank Balance Decrease: ₹{bank_decrease}")
                    print(f"   Available Credit Increase: ₹{available_increase}")
                    print(f"   Expected Repayment: ₹{repayment_amount}")
                    
                    if abs(outstanding_decrease - repayment_amount) < 0.01 and abs(bank_decrease - repayment_amount) < 0.01:
                        print(f"   ✅ Repayment logic working correctly!")
                    else:
                        print(f"   ❌ Repayment logic has issues!")
                    
            else:
                print(f"❌ Repayment failed: {repay_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_repayment()
