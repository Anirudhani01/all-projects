#!/usr/bin/env python3

import requests

def test_endpoint():
    base_url = "http://localhost:8000/api/v1"
    
    # Test if the server is running
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"Server Status: {response.status_code}")
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Test login
    login_data = {
        "email": "nani@gmail.com",
        "password": "nani123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            token = login_response["access_token"]
            print("✅ Login successful")
            
            # Test a simple GET request to see if authentication works
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test getting user profile
            user_response = requests.get(f"{base_url}/users/60", headers=headers)
            print(f"User Profile Status: {user_response.status_code}")
            print(f"User Profile Response: {user_response.text[:200]}...")
            
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint()
