#!/usr/bin/env python3
"""
Comprehensive test runner for all LazyPay API endpoints.
Runs tests for Users, Merchants, and Transactions modules.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """Run all tests for the LazyPay application."""
    print("🧪 Running All LazyPay API Tests")
    print("=" * 60)
    
    # Check if pytest is available
    try:
        import pytest
        print("✓ pytest is available")
    except ImportError:
        print("❌ pytest is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio", "httpx"], check=True)
        print("✓ pytest installed successfully")
    
    # Define test directories
    test_dirs = [
        "app/tests/test_user",
        "app/tests/test_merchants", 
        "app/tests/test_transactions"
    ]
    
    total_passed = 0
    total_failed = 0
    
    # Run tests for each module
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            print(f"❌ Test directory not found: {test_dir}")
            continue
            
        print(f"\n📁 Running tests for: {test_dir}")
        print("-" * 40)
        
        # Run pytest for this directory
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_dir, 
            "-v", 
            "--tb=short",
            "--color=yes"
        ])
        
        if result.returncode == 0:
            print(f"✅ {test_dir} tests passed!")
            total_passed += 1
        else:
            print(f"❌ {test_dir} tests failed!")
            total_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Modules passed: {total_passed}")
    print(f"❌ Modules failed: {total_failed}")
    print(f"📁 Total modules tested: {len(test_dirs)}")
    
    if total_failed == 0:
        print("\n🎉 All tests passed successfully!")
        return True
    else:
        print(f"\n⚠️  {total_failed} module(s) have failing tests.")
        return False

def run_user_tests():
    """Run only user tests."""
    print("👤 Running User Module Tests")
    print("=" * 40)
    
    test_dir = "app/tests/test_user"
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        return False
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        test_dir, 
        "-v", 
        "--tb=short",
        "--color=yes"
    ])
    
    return result.returncode == 0

def run_merchant_tests():
    """Run only merchant tests."""
    print("🏪 Running Merchant Module Tests")
    print("=" * 40)
    
    test_dir = "app/tests/test_merchants"
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        return False
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        test_dir, 
        "-v", 
        "--tb=short",
        "--color=yes"
    ])
    
    return result.returncode == 0

def run_transaction_tests():
    """Run only transaction tests."""
    print("💳 Running Transaction Module Tests")
    print("=" * 40)
    
    test_dir = "app/tests/test_transactions"
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        return False
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        test_dir, 
        "-v", 
        "--tb=short",
        "--color=yes"
    ])
    
    return result.returncode == 0

def run_integration_tests():
    """Run only integration tests."""
    print("🔗 Running Integration Tests")
    print("=" * 40)
    
    test_dirs = [
        "app/tests/test_user",
        "app/tests/test_merchants", 
        "app/tests/test_transactions"
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
            
        print(f"\n📁 Running integration tests for: {test_dir}")
        
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_dir, 
            "-k", "Integration",
            "-v", 
            "--tb=short",
            "--color=yes"
        ])
        
        if result.returncode == 0:
            print(f"✅ {test_dir} integration tests passed!")
            total_passed += 1
        else:
            print(f"❌ {test_dir} integration tests failed!")
            total_failed += 1
    
    print(f"\n📊 Integration Tests Summary: {total_passed} passed, {total_failed} failed")
    return total_failed == 0

def run_unit_tests():
    """Run only unit tests."""
    print("🔧 Running Unit Tests")
    print("=" * 40)
    
    test_dirs = [
        "app/tests/test_user",
        "app/tests/test_merchants", 
        "app/tests/test_transactions"
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
            
        print(f"\n📁 Running unit tests for: {test_dir}")
        
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_dir, 
            "-k", "not Integration",
            "-v", 
            "--tb=short",
            "--color=yes"
        ])
        
        if result.returncode == 0:
            print(f"✅ {test_dir} unit tests passed!")
            total_passed += 1
        else:
            print(f"❌ {test_dir} unit tests failed!")
            total_failed += 1
    
    print(f"\n📊 Unit Tests Summary: {total_passed} passed, {total_failed} failed")
    return total_failed == 0

def main():
    """Main function to run tests based on command line arguments."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "all":
            return run_tests()
        elif test_type == "users":
            return run_user_tests()
        elif test_type == "merchants":
            return run_merchant_tests()
        elif test_type == "transactions":
            return run_transaction_tests()
        elif test_type == "integration":
            return run_integration_tests()
        elif test_type == "unit":
            return run_unit_tests()
        else:
            print("Usage: python run_all_tests.py [all|users|merchants|transactions|integration|unit]")
            print("  all: Run all tests (default)")
            print("  users: Run only user tests")
            print("  merchants: Run only merchant tests")
            print("  transactions: Run only transaction tests")
            print("  integration: Run only integration tests")
            print("  unit: Run only unit tests")
            return False
    else:
        return run_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
