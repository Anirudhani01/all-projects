#!/usr/bin/env python3
"""
Script to directly create an admin user in MongoDB
"""

import asyncio
import motor.motor_asyncio
from passlib.hash import bcrypt
import uuid
from datetime import datetime

async def create_admin_user_direct():
    """Create admin user directly in MongoDB."""
    
    # MongoDB connection
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ecommerce_dev
    users_collection = db.users
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": "admin1@gmail.com"})
    if existing_user:
        print("✅ Admin user already exists!")
        print(f"📧 Email: admin1@gmail.com")
        print(f"🔑 Password: admin1pass")
        return
    
    # Create user data
    user_data = {
        "id": str(uuid.uuid4()),
        "first_name": "admin1",
        "last_name": "admin1",
        "email": "admin1@gmail.com",
        "hashed_password": bcrypt.hash("admin1pass"),
        "role": "admin",
        "isAdmin": True,
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    try:
        # Insert user
        result = await users_collection.insert_one(user_data)
        print("✅ Admin user created successfully!")
        print(f"📧 Email: {user_data['email']}")
        print(f"🔑 Password: admin1pass")
        print(f"👤 Role: {user_data['role']}")
        print(f"🆔 User ID: {user_data['id']}")
        print("\n🎯 You can now login with these credentials!")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")

if __name__ == "__main__":
    print("🚀 Creating admin user directly in MongoDB...")
    print("=" * 50)
    asyncio.run(create_admin_user_direct())
