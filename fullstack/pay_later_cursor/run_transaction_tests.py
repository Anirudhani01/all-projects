#!/usr/bin/env python3
"""
Test runner for transaction endpoint tests.
This script runs the comprehensive test cases for the three transaction endpoints.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """Run the transaction endpoint tests."""
    print("🧪 Running Transaction Endpoint Tests")
    print("=" * 50)
    
    # Check if pytest is available
    try:
        import pytest
        print("✓ pytest is available")
    except ImportError:
        print("❌ pytest is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"], check=True)
        print("✓ pytest installed successfully")
    
    # Check if httpx is available (required for TestClient)
    try:
        import httpx
        print("✓ httpx is available")
    except ImportError:
        print("❌ httpx is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "httpx"], check=True)
        print("✓ httpx installed successfully")
    
    # Run the tests
    test_file = Path(__file__).parent / "test_transaction_endpoints.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"📁 Running tests from: {test_file}")
    print()
    
    # Run pytest with verbose output
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        str(test_file), 
        "-v", 
        "--tb=short",
        "--color=yes"
    ])
    
    print()
    print("=" * 50)
    
    if result.returncode == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

def run_integration_tests():
    """Run only integration tests."""
    print("🔗 Running Integration Tests Only")
    print("=" * 50)
    
    test_file = Path(__file__).parent / "test_transaction_endpoints.py"
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        str(test_file), 
        "-k", "TestTransactionEndpointsIntegration",
        "-v", 
        "--tb=short",
        "--color=yes"
    ])
    
    print()
    print("=" * 50)
    
    if result.returncode == 0:
        print("🎉 Integration tests passed!")
        return True
    else:
        print("❌ Integration tests failed!")
        return False

def run_unit_tests():
    """Run only unit tests."""
    print("🔧 Running Unit Tests Only")
    print("=" * 50)
    
    test_file = Path(__file__).parent / "test_transaction_endpoints.py"
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        str(test_file), 
        "-k", "TestTransactionEndpoints and not TestTransactionEndpointsIntegration",
        "-v", 
        "--tb=short",
        "--color=yes"
    ])
    
    print()
    print("=" * 50)
    
    if result.returncode == 0:
        print("🎉 Unit tests passed!")
        return True
    else:
        print("❌ Unit tests failed!")
        return False

def main():
    """Main function to run tests based on command line arguments."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "integration":
            return run_integration_tests()
        elif test_type == "unit":
            return run_unit_tests()
        elif test_type == "all":
            return run_tests()
        else:
            print("Usage: python run_transaction_tests.py [all|unit|integration]")
            print("  all: Run all tests (default)")
            print("  unit: Run only unit tests")
            print("  integration: Run only integration tests")
            return False
    else:
        return run_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
