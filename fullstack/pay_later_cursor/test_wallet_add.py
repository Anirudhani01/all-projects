#!/usr/bin/env python3

import requests
import json

def test_wallet_add():
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
            
            # Test user credit endpoint before transaction
            headers = {"Authorization": f"Bearer {token}"}
            credit_response = requests.get(f"http://localhost:8000/api/v1/wallet/user-credit/{user_id}", headers=headers)
            
            if credit_response.status_code == 200:
                credit_before = credit_response.json()
                print(f"💰 Credit Before Transaction:")
                print(f"   Credit Limit: ₹{credit_before.get('credit_limit', 0)}")
                print(f"   Available Credit: ₹{credit_before.get('available_credit', 0)}")
                print(f"   Outstanding Amount: ₹{credit_before.get('outstanding_amount', 0)}")
            
            # Test adding money to FLIPKART merchant wallet (12% fee)
            merchant_id = "68a0cccf5efcb6a3f8ef7e97"  # FLIPKART
            amount = 300.0
            
            wallet_data = {
                "merchant_id": merchant_id,
                "amount": amount,
                "idempotency_key": f"test_wallet_add_{user_id}_{merchant_id}_{amount}"
            }
            
            print(f"\n🔄 Adding ₹{amount} to FLIPKART wallet (12% fee)...")
            wallet_response = requests.post(
                "http://localhost:8000/api/v1/wallet/add-to-merchant", 
                json=wallet_data,
                headers=headers
            )
            
            print(f"Wallet Add Status: {wallet_response.status_code}")
            print(f"Wallet Add Response: {wallet_response.text}")
            
            if wallet_response.status_code == 200:
                wallet_result = wallet_response.json()
                print(f"✅ Wallet add successful!")
                print(f"   Transaction ID: {wallet_result.get('transaction_id')}")
                print(f"   Amount: ₹{wallet_result.get('amount')}")
                print(f"   Fee Amount: ₹{wallet_result.get('fee_amount')}")
                print(f"   Total Amount: ₹{wallet_result.get('total_amount')}")
                print(f"   User Credit Before: ₹{wallet_result.get('user_credit_before')}")
                print(f"   User Credit After: ₹{wallet_result.get('user_credit_after')}")
                
                # Test user credit endpoint after transaction
                credit_after_response = requests.get(f"http://localhost:8000/api/v1/wallet/user-credit/{user_id}", headers=headers)
                
                if credit_after_response.status_code == 200:
                    credit_after = credit_after_response.json()
                    print(f"\n💰 Credit After Transaction:")
                    print(f"   Credit Limit: ₹{credit_after.get('credit_limit', 0)}")
                    print(f"   Available Credit: ₹{credit_after.get('available_credit', 0)}")
                    print(f"   Outstanding Amount: ₹{credit_after.get('outstanding_amount', 0)}")
                    
                    # Verify the logic
                    expected_outstanding = 550 + 300 + (300 * 0.12)  # Previous 550 + 300 + 12% fee = 886
                    expected_available = 2000 - expected_outstanding  # 2000 - 886 = 1114
                    
                    print(f"\n✅ Verification:")
                    print(f"   Expected Outstanding: ₹{expected_outstanding}")
                    print(f"   Actual Outstanding: ₹{credit_after.get('outstanding_amount', 0)}")
                    print(f"   Expected Available: ₹{expected_available}")
                    print(f"   Actual Available: ₹{credit_after.get('available_credit', 0)}")
                    
            else:
                print(f"❌ Failed to add to wallet: {wallet_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_wallet_add()
