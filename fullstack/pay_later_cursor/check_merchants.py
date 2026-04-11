#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database

async def check_merchants():
    await connect_to_mongo()
    db = await get_database()
    
    # Get all merchants
    merchants = await db.merchants.find({}).to_list(10)
    print('Merchants:')
    for m in merchants:
        print(f'  {m.get("name", "N/A")} - ID: {m.get("_id")} - Fee: {m.get("current_fee_pct", 0)}%')
    
    # Check merchant wallets
    print('\nMerchant Wallets:')
    wallets = await db.merchant_wallets.find({}).to_list(10)
    for w in wallets:
        print(f'  Merchant ID: {w.get("merchant_id")} - Balance: ₹{w.get("balance", 0)}')

if __name__ == "__main__":
    asyncio.run(check_merchants())
