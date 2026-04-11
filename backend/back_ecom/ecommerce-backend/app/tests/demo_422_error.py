#!/usr/bin/env python3
"""
Demonstration script showing the 422 Unprocessable Entity error scenarios
and how to fix them for the user registration endpoint.

This file is located in the proper test directory structure.
"""

import requests
import json

# Base URL for the API (adjust if your server runs on a different port)
BASE_URL = "http://localhost:8000"

def test_registration_scenarios():
    """Test various registration scenarios to demonstrate 422 errors."""
    
    print("🔍 Testing User Registration Scenarios")
    print("=" * 50)
    
    # Scenario 1: WRONG FIELD NAME (mail instead of email) - EXPECTED: 422
    print("\n1️⃣ Testing WRONG FIELD NAME (mail instead of email)")
    print("Expected: 422 Unprocessable Entity")
    
    wrong_field_data = {
        "mail": "ani@gmail.com",  # ❌ Wrong field name
        "name": "anirudh",
        "password": "ani123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=wrong_field_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 422:
            print("✅ Correctly received 422 error")
            error_detail = response.json().get("detail", [])
            print(f"Error Details: {json.dumps(error_detail, indent=2)}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the FastAPI server is running.")
        print("   Run: python start_dev.py")
        return
    
    # Scenario 2: SHORT PASSWORD (6 chars, minimum 8 required) - EXPECTED: 422
    print("\n2️⃣ Testing SHORT PASSWORD (6 characters, minimum 8 required)")
    print("Expected: 422 Unprocessable Entity")
    
    short_password_data = {
        "email": "ani@gmail.com",
        "name": "anirudh",
        "password": "ani123"  # ❌ Only 6 characters
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=short_password_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 422:
            print("✅ Correctly received 422 error")
            error_detail = response.json().get("detail", [])
            print(f"Error Details: {json.dumps(error_detail, indent=2)}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
    
    # Scenario 3: CORRECT DATA FORMAT - EXPECTED: Not 422 (could be 200, 400, or 500)
    print("\n3️⃣ Testing CORRECT DATA FORMAT")
    print("Expected: NOT 422 (could be 200, 400, or 500)")
    
    correct_data = {
        "email": "ani@gmail.com",
        "name": "anirudh",
        "password": "ani123456"  # ✅ 8+ characters
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=correct_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 422:
            print("✅ Correctly passed validation (no 422 error)")
            if response.status_code == 200:
                print("🎉 User registered successfully!")
            elif response.status_code == 400:
                print("ℹ️  User already exists (expected for repeated requests)")
            elif response.status_code == 500:
                print("⚠️  Database error (expected if MongoDB not running)")
            else:
                print(f"ℹ️  Status code: {response.status_code}")
        else:
            print("❌ Unexpectedly received 422 error")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
    
    # Scenario 4: INVALID EMAIL FORMAT - EXPECTED: 422
    print("\n4️⃣ Testing INVALID EMAIL FORMAT")
    print("Expected: 422 Unprocessable Entity")
    
    invalid_email_data = {
        "email": "invalid-email",  # ❌ Invalid email format
        "name": "anirudh",
        "password": "ani123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=invalid_email_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 422:
            print("✅ Correctly received 422 error")
            error_detail = response.json().get("detail", [])
            print(f"Error Details: {json.dumps(error_detail, indent=2)}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")

def test_login_scenarios():
    """Test login scenarios."""
    
    print("\n🔐 Testing User Login Scenarios")
    print("=" * 50)
    
    # Scenario 1: Missing password field - EXPECTED: 422
    print("\n1️⃣ Testing MISSING PASSWORD FIELD")
    print("Expected: 422 Unprocessable Entity")
    
    missing_password_data = {
        "email": "ani@gmail.com"
        # ❌ Missing password field
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=missing_password_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 422:
            print("✅ Correctly received 422 error")
            error_detail = response.json().get("detail", [])
            print(f"Error Details: {json.dumps(error_detail, indent=2)}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
    
    # Scenario 2: Correct login format - EXPECTED: Not 422 (could be 401 or 500)
    print("\n2️⃣ Testing CORRECT LOGIN FORMAT")
    print("Expected: NOT 422 (could be 401 or 500)")
    
    correct_login_data = {
        "email": "ani@gmail.com",
        "password": "ani123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=correct_login_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 422:
            print("✅ Correctly passed validation (no 422 error)")
            if response.status_code == 200:
                print("🎉 Login successful!")
                data = response.json()
                print(f"Access Token: {data.get('access_token', 'N/A')[:20]}...")
            elif response.status_code == 401:
                print("ℹ️  Invalid credentials (expected if user not registered)")
            elif response.status_code == 500:
                print("⚠️  Database error (expected if MongoDB not running)")
            else:
                print(f"ℹ️  Status code: {response.status_code}")
        else:
            print("❌ Unexpectedly received 422 error")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")

def show_solution():
    """Show the solution to fix the 422 errors."""
    
    print("\n💡 SOLUTION: How to Fix the 422 Errors")
    print("=" * 50)
    
    print("""
❌ WRONG FORMAT (causes 422 error):
{
    "mail": "ani@gmail.com",     # ❌ Should be "email"
    "name": "anirudh",
    "password": "ani123"         # ❌ Too short (minimum 8 chars)
}

✅ CORRECT FORMAT (passes validation):
{
    "email": "ani@gmail.com",    # ✅ Correct field name
    "name": "anirudh",
    "password": "ani123456"      # ✅ 8+ characters
}
""")
    
    print("Key Changes Made:")
    print("1. 'mail' → 'email' (correct field name)")
    print("2. 'ani123' → 'ani123456' (minimum 8 characters)")
    print("3. All required fields present")
    print("4. Valid email format")
    print("5. Name length 2+ characters")

def main():
    """Main function to run all demonstrations."""
    
    print("🚀 FastAPI User Registration 422 Error Demonstration")
    print("=" * 60)
    
    # Test registration scenarios
    test_registration_scenarios()
    
    # Test login scenarios
    test_login_scenarios()
    
    # Show solution
    show_solution()
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print("• The 422 errors were caused by incorrect field names and validation failures")
    print("• The API is working correctly - it's properly validating input data")
    print("• Use the correct field names and meet all validation requirements")
    print("• Run the tests with: python -m pytest app/tests/test_auth_simple.py -v")

if __name__ == "__main__":
    main()
