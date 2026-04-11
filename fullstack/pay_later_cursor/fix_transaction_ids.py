#!/usr/bin/env python3

import asyncio
from app.db.mongo import connect_to_mongo, get_database
from datetime import datetime, timezone
import uuid

async def fix_transaction_ids():
    await connect_to_mongo()
    db = await get_database()
    
    # Find transactions with null transaction_id
    null_transactions = await db.transactions.find({"transaction_id": None}).to_list(100)
    print(f"Found {len(null_transactions)} transactions with null transaction_id")
    
    for transaction in null_transactions:
        # Generate a unique transaction ID
        new_transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
        
        # Update the transaction
        result = await db.transactions.update_one(
            {"_id": transaction["_id"]},
            {"$set": {"transaction_id": new_transaction_id}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Fixed transaction {transaction['_id']} with new ID: {new_transaction_id}")
        else:
            print(f"❌ Failed to fix transaction {transaction['_id']}")
    
    # Also check for transactions with empty string transaction_id
    empty_transactions = await db.transactions.find({"transaction_id": ""}).to_list(100)
    print(f"Found {len(empty_transactions)} transactions with empty transaction_id")
    
    for transaction in empty_transactions:
        # Generate a unique transaction ID
        new_transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
        
        # Update the transaction
        result = await db.transactions.update_one(
            {"_id": transaction["_id"]},
            {"$set": {"transaction_id": new_transaction_id}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Fixed empty transaction {transaction['_id']} with new ID: {new_transaction_id}")
        else:
            print(f"❌ Failed to fix empty transaction {transaction['_id']}")

if __name__ == "__main__":
    asyncio.run(fix_transaction_ids())
