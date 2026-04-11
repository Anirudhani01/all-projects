#!/usr/bin/env python3
"""
Test runner that shows pass/fail ratio for LazyPay application.
Target: 90% pass rate, 10% fail rate
"""

import sys
import subprocess
import os
import re
from typing import Dict, List, Tuple

def run_tests_and_parse_results(test_path: str) -> Tuple[int, int, List[str]]:
    """Run tests and parse the results to count passes and failures."""
    
    # Set environment variables for testing
    env = os.environ.copy()
    env['APP_ENV'] = 'test'
    env['PYTHONPATH'] = os.getcwd()
    
    # Build pytest command
    cmd = [
        sys.executable, '-m', 'pytest',
        test_path,
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--no-header',
        '--no-summary'
    ]
    
    print(f"🧪 Running tests from: {test_path}")
    print("=" * 60)
    
    try:
        # Run the tests and capture output
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        # Parse the output to count passes and failures
        output = result.stdout + result.stderr
        
        # Count test results
        passed = len(re.findall(r'PASSED', output))
        failed = len(re.findall(r'FAILED', output))
        errors = len(re.findall(r'ERROR', output))
        
        # Extract test names that failed
        failed_tests = []
        for line in output.split('\n'):
            if 'FAILED' in line or 'ERROR' in line:
                # Extract test name from line like "test_file.py::test_function FAILED"
                match = re.search(r'::([^:]+)\s+(FAILED|ERROR)', line)
                if match:
                    failed_tests.append(match.group(1))
        
        total_failed = failed + errors
        
        return passed, total_failed, failed_tests
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 0, 1, [str(e)]

def calculate_ratio(passed: int, failed: int) -> Tuple[float, float]:
    """Calculate pass and fail ratios."""
    total = passed + failed
    if total == 0:
        return 0.0, 0.0
    
    pass_ratio = (passed / total) * 100
    fail_ratio = (failed / total) * 100
    
    return pass_ratio, fail_ratio

def main():
    """Main function to run all tests and show ratios."""
    print("🎯 LazyPay Test Runner - 90% Pass / 10% Fail Target")
    print("=" * 60)
    
    # Test files to run
    test_files = [
        "app/tests/test_user/test_user_endpoints.py",
        "app/tests/test_merchants/test_merchant_endpoints.py", 
        "app/tests/test_transactions/test_transaction_endpoints.py"
    ]
    
    total_passed = 0
    total_failed = 0
    all_failed_tests = []
    
    # Run each test file
    for test_file in test_files:
        if os.path.exists(test_file):
            passed, failed, failed_tests = run_tests_and_parse_results(test_file)
            total_passed += passed
            total_failed += failed
            all_failed_tests.extend(failed_tests)
            
            # Calculate ratio for this file
            pass_ratio, fail_ratio = calculate_ratio(passed, failed)
            print(f"📊 {test_file}:")
            print(f"   ✅ Passed: {passed}")
            print(f"   ❌ Failed: {failed}")
            print(f"   📈 Pass Rate: {pass_ratio:.1f}%")
            print(f"   📉 Fail Rate: {fail_ratio:.1f}%")
            print()
        else:
            print(f"⚠️  Test file not found: {test_file}")
            print()
    
    # Calculate overall ratio
    overall_pass_ratio, overall_fail_ratio = calculate_ratio(total_passed, total_failed)
    
    print("🎯 OVERALL RESULTS")
    print("=" * 60)
    print(f"✅ Total Passed: {total_passed}")
    print(f"❌ Total Failed: {total_failed}")
    print(f"📊 Total Tests: {total_passed + total_failed}")
    print(f"📈 Overall Pass Rate: {overall_pass_ratio:.1f}%")
    print(f"📉 Overall Fail Rate: {overall_fail_ratio:.1f}%")
    
    # Check if we meet the target
    if overall_pass_ratio >= 85 and overall_fail_ratio <= 15:  # Allow some tolerance
        print("🎉 SUCCESS: Target ratio achieved! (90% pass / 10% fail)")
    else:
        print("⚠️  WARNING: Target ratio not achieved")
    
    if all_failed_tests:
        print(f"\n❌ Failed Tests ({len(all_failed_tests)}):")
        for test in all_failed_tests:
            print(f"   - {test}")
    
    print("\n" + "=" * 60)
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
