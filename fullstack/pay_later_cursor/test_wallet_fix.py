#!/usr/bin/env python3

import requests
import json

def test_wallet_fix():
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
            
            # Test user credit endpoint before transaction
            headers = {"Authorization": f"Bearer {token}"}
            credit_response = requests.get(f"{base_url}/wallet/user-credit/{user_id}", headers=headers)
            
            if credit_response.status_code == 200:
                credit_before = credit_response.json()
                print(f"💰 Credit Before Transaction:")
                print(f"   Credit Limit: ₹{credit_before.get('credit_limit', 0)}")
                print(f"   Available Credit: ₹{credit_before.get('available_credit', 0)}")
                print(f"   Outstanding Amount: ₹{credit_before.get('outstanding_amount', 0)}")
            
            # Test adding money to Flipkart merchant wallet (using custom_merchant_id)
            merchant_id = "2"  # Flipkart's custom_merchant_id
            amount = 10.0
            
            wallet_data = {
                "merchant_id": merchant_id,
                "amount": amount,
                "idempotency_key": f"test_wallet_fix_{user_id}_{merchant_id}_{amount}"
            }
            
            print(f"\n🔄 Adding ₹{amount} to Flipkart wallet (using custom_merchant_id: {merchant_id})...")
            wallet_response = requests.post(
                f"{base_url}/wallet/add-to-merchant", 
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
                credit_after_response = requests.get(f"{base_url}/wallet/user-credit/{user_id}", headers=headers)
                
                if credit_after_response.status_code == 200:
                    credit_after = credit_after_response.json()
                    print(f"\n💰 Credit After Transaction:")
                    print(f"   Credit Limit: ₹{credit_after.get('credit_limit', 0)}")
                    print(f"   Available Credit: ₹{credit_after.get('available_credit', 0)}")
                    print(f"   Outstanding Amount: ₹{credit_after.get('outstanding_amount', 0)}")
                    
                    # Verify the credit decreased
                    credit_before_available = credit_before.get('available_credit', 0)
                    credit_after_available = credit_after.get('available_credit', 0)
                    credit_decrease = credit_before_available - credit_after_available
                    
                    print(f"\n✅ Verification:")
                    print(f"   Credit Decrease: ₹{credit_decrease}")
                    print(f"   Expected Decrease: ₹{wallet_result.get('total_amount')}")
                    
                    if abs(credit_decrease - wallet_result.get('total_amount', 0)) < 0.01:
                        print(f"   ✅ Credit decrease matches expected amount!")
                    else:
                        print(f"   ❌ Credit decrease doesn't match expected amount!")
                    
            else:
                print(f"❌ Failed to add to wallet: {wallet_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_wallet_fix()
