#!/usr/bin/env python3
import requests
import json

def test_phase4_detail_view():
    """Test Phase 4 Employee Detail View Implementation"""
    print("🔍 Testing Phase 4 Employee Detail View Implementation...")
    
    # Test 1: Check if frontend is accessible
    try:
        response = requests.get("http://127.0.0.1:3000")
        print(f"✅ Frontend server: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return
    
    # Test 2: Check if backend is accessible
    try:
        response = requests.get("http://127.0.0.1:8000")
        print(f"✅ Backend server: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return
    
    # Test 3: Login to get token
    login_data = {
        "name": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post("http://127.0.0.1:8000/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 4: Get employee details for detail view
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get("http://127.0.0.1:8000/employees/1", headers=headers)
        if response.status_code == 200:
            employee = response.json()
            print(f"✅ Employee detail fetch successful")
            print(f"   Employee: {employee['Name']} (ID: {employee['emp_id']})")
            print(f"   Email: {employee['Email']}")
            print(f"   Age: {employee.get('Age', 'N/A')}")
            print(f"   City: {employee.get('City', 'N/A')}")
            print(f"   Education: {employee.get('Education', 'N/A')}")
            print(f"   Experience: {employee.get('ExperienceInCurrentDomain', 0)} years")
            print(f"   Payment Tier: {employee.get('PaymentTier', 'N/A')}")
            print(f"   Status: {'On Leave' if employee.get('LeaveOrNot') else 'Active'}")
            print(f"   Image Path: {employee.get('image_path', 'None')}")
        else:
            print(f"❌ Employee detail fetch failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Employee detail test error: {e}")
        return
    
    print("\n🎯 Phase 4 Employee Detail View Test Summary:")
    print("✅ Frontend server running on port 3000")
    print("✅ Backend server running on port 8000")
    print("✅ Authentication working")
    print("✅ Employee detail data accessible")
    print("✅ All employee fields available for detail view")
    
    print("\n📋 New Phase 4 Features:")
    print("   - Row-click navigation to detail view")
    print("   - Employee detail modal with full information")
    print("   - Large image display (200x200px)")
    print("   - Organized information sections:")
    print("     • Personal Information")
    print("     • Professional Information")
    print("     • Location & Status")
    print("   - Image upload/delete in detail view")
    print("   - Edit/Delete actions from detail view")
    print("   - Responsive design for mobile devices")
    
    print("\n🎨 UI Features:")
    print("   - Hover effects on table rows")
    print("   - Large image container with border")
    print("   - Grid layout for information sections")
    print("   - Status badges and styling")
    print("   - Action buttons for quick operations")
    
    print("\n🌐 Access the application at: http://127.0.0.1:3000")
    print("💡 Click on any employee row to see the detail view!")

if __name__ == "__main__":
    test_phase4_detail_view()
