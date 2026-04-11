#!/usr/bin/env python3

import requests
import json

def test_wallet_fresh():
    base_url = "http://localhost:8000/api/v1"
    
    # Login with a different user
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
            
            # Test adding money to KFC merchant wallet (10% fee)
            merchant_id = "68a0c8fa5efcb6a3f8ef7e93"  # KFC
            amount = 100.0
            
            wallet_data = {
                "merchant_id": merchant_id,
                "amount": amount,
                "idempotency_key": f"test_fresh_wallet_{user_id}_{merchant_id}_{amount}"
            }
            
            print(f"\n🔄 Adding ₹{amount} to KFC wallet (10% fee)...")
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
                
                # Test user credit endpoint after transaction
                credit_after_response = requests.get(f"{base_url}/wallet/user-credit/{user_id}", headers=headers)
                
                if credit_after_response.status_code == 200:
                    credit_after = credit_after_response.json()
                    print(f"\n💰 Credit After Transaction:")
                    print(f"   Credit Limit: ₹{credit_after.get('credit_limit', 0)}")
                    print(f"   Available Credit: ₹{credit_after.get('available_credit', 0)}")
                    print(f"   Outstanding Amount: ₹{credit_after.get('outstanding_amount', 0)}")
                    
            else:
                print(f"❌ Failed to add to wallet: {wallet_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_wallet_fresh()
