#!/usr/bin/env python3
"""
Debug test runner to identify specific test issues.
"""

import sys
import subprocess
import os

def run_single_test(test_path: str, test_name: str = None):
    """Run a single test to debug issues."""
    
    # Set environment variables for testing
    env = os.environ.copy()
    env['APP_ENV'] = 'test'
    env['PYTHONPATH'] = os.getcwd()
    
    # Build pytest command
    cmd = [
        sys.executable, '-m', 'pytest',
        test_path,
        '-v',
        '--tb=long',
        '--disable-warnings'
    ]
    
    if test_name:
        cmd.append(f"::{test_name}")
    
    print(f"🔍 Debugging test: {test_path}")
    if test_name:
        print(f"   Test: {test_name}")
    print("=" * 60)
    
    try:
        # Run the test and show full output
        result = subprocess.run(cmd, env=env, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Main function to debug tests."""
    print("🐛 LazyPay Test Debugger")
    print("=" * 60)
    
    # Test individual test files
    test_files = [
        "app/tests/test_user/test_user_endpoints.py",
        "app/tests/test_merchants/test_merchant_endpoints.py", 
        "app/tests/test_transactions/test_transaction_endpoints.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📁 Testing file: {test_file}")
            success = run_single_test(test_file)
            if success:
                print(f"✅ {test_file} - All tests passed")
            else:
                print(f"❌ {test_file} - Some tests failed")
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    print("\n" + "=" * 60)
    print("🔍 Debug complete!")

if __name__ == "__main__":
    main()
