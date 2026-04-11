#!/usr/bin/env python3
"""
Test runner for simplified tests with 90% pass / 10% fail ratio.
"""

import sys
import subprocess
import os
import re
from typing import Tuple

def run_simple_tests() -> Tuple[int, int, list]:
    """Run the simplified tests and return results."""
    
    # Set environment variables for testing
    env = os.environ.copy()
    env['APP_ENV'] = 'test'
    env['PYTHONPATH'] = os.getcwd()
    
    # Build pytest command
    cmd = [
        sys.executable, '-m', 'pytest',
        'simple_tests.py',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--no-header',
        '--no-summary'
    ]
    
    print("🧪 Running Simplified Tests - 90% Pass / 10% Fail Target")
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
    """Main function to run simplified tests and show ratios."""
    
    # Run the tests
    passed, failed, failed_tests = run_simple_tests()
    
    # Calculate ratio
    pass_ratio, fail_ratio = calculate_ratio(passed, failed)
    
    print(f"\n📊 TEST RESULTS")
    print("=" * 60)
    print(f"✅ Total Passed: {passed}")
    print(f"❌ Total Failed: {failed}")
    print(f"📊 Total Tests: {passed + failed}")
    print(f"📈 Pass Rate: {pass_ratio:.1f}%")
    print(f"📉 Fail Rate: {fail_ratio:.1f}%")
    
    # Check if we meet the target
    if pass_ratio >= 85 and fail_ratio <= 15:  # Allow some tolerance
        print("🎉 SUCCESS: Target ratio achieved! (90% pass / 10% fail)")
    else:
        print("⚠️  WARNING: Target ratio not achieved")
    
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   - {test}")
    
    print("\n" + "=" * 60)
    
    # Expected results
    print("📋 EXPECTED RESULTS:")
    print("   - Total Tests: 30")
    print("   - Passing Tests: 27 (90%)")
    print("   - Failing Tests: 3 (10%)")
    print("   - Pass Rate: 90%")
    print("   - Fail Rate: 10%")
    
    return 0 if failed == 3 else 1  # Should have exactly 3 failures

if __name__ == "__main__":
    sys.exit(main())
