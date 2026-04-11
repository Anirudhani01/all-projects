#!/usr/bin/env python3
"""
Test script to verify API endpoints using FastAPI test client
"""
import sys
import os
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

def test_api_endpoints():
    """Test all API endpoints using FastAPI test client"""
    
    client = TestClient(app)
    
    print("🧪 Testing Hospital Management System API...")
    
    try:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = client.get("/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test doctors endpoint
        print("\n2. Testing doctors endpoint...")
        response = client.get("/api/doctors/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data['total']} doctors")
            for doctor in data['doctors'][:2]:  # Show first 2
                print(f"   - {doctor['name']} ({doctor['specialization']})")
        
        # Test specializations
        print("\n3. Testing specializations endpoint...")
        response = client.get("/api/doctors/specializations/list")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Specializations: {response.json()}")
        
        # Test blog posts
        print("\n4. Testing blog posts endpoint...")
        response = client.get("/api/blog/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data['total']} blog posts")
            for post in data['posts'][:2]:  # Show first 2
                print(f"   - {post['title']} ({post['category']})")
        
        # Test contact messages
        print("\n5. Testing contact messages endpoint...")
        response = client.get("/api/contact/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data['total']} contact messages")
        
        # Test patients
        print("\n6. Testing patients endpoint...")
        response = client.get("/api/patients/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            patients = response.json()
            print(f"   Found {len(patients)} patients")
        
        # Test appointments
        print("\n7. Testing appointments endpoint...")
        response = client.get("/api/appointments/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            appointments = response.json()
            print(f"   Found {len(appointments)} appointments")
        
        # Test time slots
        print("\n8. Testing time slots endpoint...")
        response = client.get("/api/appointments/slots?doctor_id=1&appointment_date=2025-09-11")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            slots = response.json()
            print(f"   Found {len(slots)} time slots")
            for slot in slots[:3]:  # Show first 3
                print(f"   - {slot['time']} (available: {slot['is_available']})")
        
        print("\n✅ API testing completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_endpoints()
