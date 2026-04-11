#!/usr/bin/env python3
"""
RBAC Integration Test - Phase 4
Tests the complete RBAC integration with the main application
"""

import asyncio
import sys
import os
import requests
import json

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.rbac.initializer import RBACInitializer
from app.rbac.repository import RBACRepository
from app.rbac.service import RBACService
from app.db.mongo import get_database
import structlog

logger = structlog.get_logger(__name__)

BASE_URL = 'http://localhost:8000'

async def test_rbac_initialization():
    """Test RBAC system initialization."""
    print("🔐 TESTING RBAC INITIALIZATION")
    print("=" * 40)
    
    try:
        # Get database connection
        database = get_database()
        rbac_repository = RBACRepository(database)
        initializer = RBACInitializer(rbac_repository)
        
        # Initialize RBAC system
        result = await initializer.initialize_rbac_system()
        print(f"✅ RBAC System initialized: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ RBAC Initialization failed: {str(e)}")
        return False

async def test_rbac_service():
    """Test RBAC service functionality."""
    print("\n🔧 TESTING RBAC SERVICE")
    print("=" * 30)
    
    try:
        database = get_database()
        rbac_repository = RBACRepository(database)
        rbac_service = RBACService(rbac_repository)
        
        # Test role retrieval
        roles = await rbac_service.get_all_roles()
        print(f"✅ Found {len(roles)} roles")
        
        # Test permission retrieval
        permissions = await rbac_service.get_all_permissions()
        print(f"✅ Found {len(permissions)} permissions")
        
        # Test admin role
        admin_role = await rbac_service.get_role_by_name("admin")
        if admin_role:
            print(f"✅ Admin role found with {len(admin_role.permissions)} permissions")
        
        return True
        
    except Exception as e:
        print(f"❌ RBAC Service test failed: {str(e)}")
        return False

def test_application_startup():
    """Test if the application starts with RBAC integration."""
    print("\n🚀 TESTING APPLICATION STARTUP")
    print("=" * 35)
    
    try:
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Application health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Application not running. Please start the application first.")
        return False
    except Exception as e:
        print(f"❌ Application startup test failed: {str(e)}")
        return False

def test_rbac_endpoints():
    """Test RBAC API endpoints."""
    print("\n🌐 TESTING RBAC ENDPOINTS")
    print("=" * 30)
    
    try:
        # Test RBAC health endpoint
        response = requests.get(f"{BASE_URL}/api/v1/rbac/health")
        if response.status_code == 200:
            print("✅ RBAC health endpoint working")
        else:
            print(f"❌ RBAC health endpoint failed: {response.status_code}")
            return False
        
        # Test roles endpoint (should require authentication)
        response = requests.get(f"{BASE_URL}/api/v1/rbac/roles")
        if response.status_code == 401:
            print("✅ RBAC roles endpoint properly secured")
        else:
            print(f"❌ RBAC roles endpoint not properly secured: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ RBAC endpoints test failed: {str(e)}")
        return False

def test_protected_endpoints():
    """Test that existing endpoints are properly protected."""
    print("\n🔒 TESTING PROTECTED ENDPOINTS")
    print("=" * 35)
    
    endpoints_to_test = [
        "/api/v1/users/",
        "/api/v1/merchants/",
        "/api/v1/transactions/",
        "/api/v1/reports/fee/test-merchant"
    ]
    
    all_protected = True
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"✅ {endpoint} properly protected")
            else:
                print(f"❌ {endpoint} not properly protected: {response.status_code}")
                all_protected = False
                
        except Exception as e:
            print(f"❌ Error testing {endpoint}: {str(e)}")
            all_protected = False
    
    return all_protected

def test_authentication_flow():
    """Test complete authentication and RBAC flow."""
    print("\n🔐 TESTING AUTHENTICATION FLOW")
    print("=" * 35)
    
    try:
        # Step 1: Register a test user
        register_data = {
            "email": "rbac_test@example.com",
            "name": "RBAC Test User",
            "password": "testpass123",
            "role": "user"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
        if response.status_code == 201:
            print("✅ User registration successful")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            return False
        
        # Step 2: Login to get token
        login_data = {
            "email": "rbac_test@example.com",
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print("✅ User login successful")
        else:
            print(f"❌ User login failed: {response.status_code}")
            return False
        
        # Step 3: Test accessing protected endpoint with token
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{BASE_URL}/api/v1/users/", headers=headers)
        if response.status_code == 200:
            print("✅ Protected endpoint access successful")
        else:
            print(f"❌ Protected endpoint access failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication flow test failed: {str(e)}")
        return False

async def main():
    """Main test function."""
    print("🚀 RBAC PHASE 4 INTEGRATION TEST")
    print("=" * 50)
    
    # Test 1: RBAC Initialization
    init_success = await test_rbac_initialization()
    
    # Test 2: RBAC Service
    service_success = await test_rbac_service()
    
    # Test 3: Application Startup
    startup_success = test_application_startup()
    
    # Test 4: RBAC Endpoints
    endpoints_success = test_rbac_endpoints()
    
    # Test 5: Protected Endpoints
    protected_success = test_protected_endpoints()
    
    # Test 6: Authentication Flow
    auth_success = test_authentication_flow()
    
    # Summary
    print("\n📊 INTEGRATION TEST SUMMARY")
    print("=" * 30)
    print(f"RBAC Initialization: {'✅ PASSED' if init_success else '❌ FAILED'}")
    print(f"RBAC Service: {'✅ PASSED' if service_success else '❌ FAILED'}")
    print(f"Application Startup: {'✅ PASSED' if startup_success else '❌ FAILED'}")
    print(f"RBAC Endpoints: {'✅ PASSED' if endpoints_success else '❌ FAILED'}")
    print(f"Protected Endpoints: {'✅ PASSED' if protected_success else '❌ FAILED'}")
    print(f"Authentication Flow: {'✅ PASSED' if auth_success else '❌ FAILED'}")
    
    all_tests_passed = all([
        init_success, service_success, startup_success,
        endpoints_success, protected_success, auth_success
    ])
    
    if all_tests_passed:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ RBAC Phase 4 Integration is complete and working!")
        print("\n📋 Next Steps:")
        print("   1. Start Phase 5: Comprehensive testing")
        print("   2. Create test files in test_rbac/ folder")
        print("   3. Test with real user scenarios")
    else:
        print("\n⚠️  Some integration tests failed.")
        print("Please check the implementation and try again.")

if __name__ == "__main__":
    asyncio.run(main())
