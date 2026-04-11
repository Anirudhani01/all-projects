#!/usr/bin/env python3
"""
Test runner for MoodBooster backend tests
"""

import pytest
import sys
import os
import asyncio
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def run_tests():
    """Run all tests with proper configuration"""
    
    # Test configuration
    test_args = [
        "tests/",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker handling
        "--disable-warnings",  # Disable warnings
        "--color=yes",  # Colored output
        "-x",  # Stop on first failure
    ]
    
    # Add coverage if available
    try:
        import coverage
        test_args.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
    except ImportError:
        print("⚠️  Coverage not available. Install with: pip install pytest-cov")
    
    # Run tests
    exit_code = pytest.main(test_args)
    return exit_code

def run_specific_test(test_name):
    """Run a specific test file or test function"""
    test_args = [
        f"tests/{test_name}",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    exit_code = pytest.main(test_args)
    return exit_code

def run_async_tests():
    """Run async tests specifically"""
    test_args = [
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes",
        "-k", "async"  # Only run async tests
    ]
    
    exit_code = pytest.main(test_args)
    return exit_code

def main():
    """Main test runner function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MoodBooster Test Runner")
    parser.add_argument("--test", "-t", help="Run specific test file or function")
    parser.add_argument("--async-only", "-a", action="store_true", help="Run only async tests")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage")
    
    args = parser.parse_args()
    
    print("🧪 Running MoodBooster Tests")
    print("=" * 50)
    
    if args.test:
        print(f"Running specific test: {args.test}")
        exit_code = run_specific_test(args.test)
    elif args.async_only:
        print("Running async tests only...")
        exit_code = run_async_tests()
    else:
        print("Running all tests...")
        exit_code = run_tests()
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
