#!/usr/bin/env python3
"""
Fixed test runner for LazyPay application.
This script runs tests with proper mocking and without database connections.
"""

import sys
import subprocess
import os

def run_tests(module=None, test_type=None):
    """Run tests with proper configuration."""
    
    # Set environment variables for testing
    env = os.environ.copy()
    env['APP_ENV'] = 'test'
    env['PYTHONPATH'] = os.getcwd()
    
    # Build pytest command
    cmd = [
        sys.executable, '-m', 'pytest',
        '-v',  # Verbose output
        '--tb=short',  # Short traceback
        '--disable-warnings',  # Disable warnings
        '--no-header',  # No header
        '--no-summary'  # No summary
    ]
    
    if module:
        if module == 'users':
            cmd.append('app/tests/test_user/')
        elif module == 'merchants':
            cmd.append('app/tests/test_merchants/')
        elif module == 'transactions':
            cmd.append('app/tests/test_transactions/')
        else:
            print(f"❌ Unknown module: {module}")
            return False
    else:
        # Run all tests
        cmd.append('app/tests/')
    
    if test_type:
        if test_type == 'unit':
            cmd.extend(['-k', 'not Integration'])
        elif test_type == 'integration':
            cmd.extend(['-k', 'Integration'])
    
    print(f"🚀 Running tests with command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main function to run tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run LazyPay tests')
    parser.add_argument('module', nargs='?', choices=['users', 'merchants', 'transactions'], 
                       help='Specific module to test')
    parser.add_argument('--type', choices=['unit', 'integration'], 
                       help='Type of tests to run')
    
    args = parser.parse_args()
    
    print("🧪 LazyPay Test Runner")
    print("=" * 60)
    
    success = run_tests(args.module, args.type)
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
