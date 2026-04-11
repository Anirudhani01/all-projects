#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database
from datetime import datetime, timezone

async def create_merchant_wallets():
    await connect_to_mongo()
    db = await get_database()
    
    # Get all merchants
    merchants = await db.merchants.find({}).to_list(10)
    print('Creating wallets for merchants:')
    
    for merchant in merchants:
        merchant_id = merchant["_id"]
        merchant_name = merchant.get("name", "Unknown")
        
        # Check if wallet already exists
        existing_wallet = await db.merchant_wallets.find_one({"merchant_id": merchant_id})
        
        if existing_wallet:
            print(f"  ✅ {merchant_name} - Wallet exists (Balance: ₹{existing_wallet.get('balance', 0)})")
        else:
            # Create wallet
            wallet_data = {
                "merchant_id": merchant_id,
                "balance": 0.0,
                "total_received": 0.0,
                "total_fees": 0.0,
                "transaction_count": 0,
                "last_transaction_at": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = await db.merchant_wallets.insert_one(wallet_data)
            print(f"  ✅ {merchant_name} - Created wallet with ID: {result.inserted_id}")

if __name__ == "__main__":
    asyncio.run(create_merchant_wallets())
