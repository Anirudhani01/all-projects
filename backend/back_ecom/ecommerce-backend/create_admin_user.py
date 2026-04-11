#!/usr/bin/env python3
"""
Script to create an admin user for testing purposes
"""

import requests
import json

def create_admin_user():
    """Create an admin user with the specified credentials."""
    
    # User data
    user_data = {
        "first_name": "admin1",
        "last_name": "admin1", 
        "email": "admin1@gmail.com",
        "password": "admin1pass",
        "role": "admin"
    }
    
    try:
        # Make POST request to register endpoint
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            headers={"Content-Type": "application/json"},
            json=user_data
        )
        
        if response.status_code == 200:
            print("✅ Admin user created successfully!")
            print(f"📧 Email: {user_data['email']}")
            print(f"🔑 Password: {user_data['password']}")
            print(f"👤 Role: {user_data['role']}")
            print("\n🎯 You can now login with these credentials!")
        else:
            print(f"❌ Failed to create user. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server!")
        print("💡 Make sure your backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Creating admin user...")
    print("=" * 40)
    create_admin_user()
