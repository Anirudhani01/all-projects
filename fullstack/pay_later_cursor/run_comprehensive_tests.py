#!/usr/bin/env python3
"""
Test runner for comprehensive tests with 90% pass / 10% fail ratio.
- 20 tests per module (Users, Merchants, Transactions)
- 18 passing tests per module
- 2 failing tests per module
- Total: 60 tests (54 passing, 6 failing)
"""

import sys
import subprocess
import os
import re
from typing import Tuple, Dict

def run_comprehensive_tests() -> Tuple[int, int, list, Dict]:
    """Run the comprehensive tests and return detailed results."""
    
    # Set environment variables for testing
    env = os.environ.copy()
    env['APP_ENV'] = 'test'
    env['PYTHONPATH'] = os.getcwd()
    
    # Build pytest command
    cmd = [
        sys.executable, '-m', 'pytest',
        'comprehensive_tests.py',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--no-header',
        '--no-summary'
    ]
    
    print("🧪 Running Comprehensive Tests - 90% Pass / 10% Fail Target")
    print("=" * 80)
    print("📋 Test Distribution:")
    print("   - Users: 20 tests (18 pass, 2 fail)")
    print("   - Merchants: 20 tests (18 pass, 2 fail)")
    print("   - Transactions: 20 tests (18 pass, 2 fail)")
    print("   - Total: 60 tests (54 pass, 6 fail)")
    print("=" * 80)
    
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
        
        # Calculate per-module statistics
        module_stats = {
            'users': {'passed': 0, 'failed': 0},
            'merchants': {'passed': 0, 'failed': 0},
            'transactions': {'passed': 0, 'failed': 0}
        }
        
        # Count tests per module
        for line in output.split('\n'):
            if 'PASSED' in line:
                if 'User' in line:
                    module_stats['users']['passed'] += 1
                elif 'Merchant' in line:
                    module_stats['merchants']['passed'] += 1
                elif 'Transaction' in line:
                    module_stats['transactions']['passed'] += 1
            elif 'FAILED' in line or 'ERROR' in line:
                if 'User' in line:
                    module_stats['users']['failed'] += 1
                elif 'Merchant' in line:
                    module_stats['merchants']['failed'] += 1
                elif 'Transaction' in line:
                    module_stats['transactions']['failed'] += 1
        
        return passed, total_failed, failed_tests, module_stats
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 0, 1, [str(e)], {}

def calculate_ratio(passed: int, failed: int) -> Tuple[float, float]:
    """Calculate pass and fail ratios."""
    total = passed + failed
    if total == 0:
        return 0.0, 0.0
    
    pass_ratio = (passed / total) * 100
    fail_ratio = (failed / total) * 100
    
    return pass_ratio, fail_ratio

def print_module_results(module_stats: Dict):
    """Print detailed results for each module."""
    print("\n📊 MODULE BREAKDOWN:")
    print("=" * 80)
    
    for module, stats in module_stats.items():
        total = stats['passed'] + stats['failed']
        if total > 0:
            pass_ratio = (stats['passed'] / total) * 100
            fail_ratio = (stats['failed'] / total) * 100
            
            print(f"🔹 {module.upper()} MODULE:")
            print(f"   ✅ Passed: {stats['passed']}/20")
            print(f"   ❌ Failed: {stats['failed']}/20")
            print(f"   📈 Pass Rate: {pass_ratio:.1f}%")
            print(f"   📉 Fail Rate: {fail_ratio:.1f}%")
            
            # Check if this module meets the target
            if stats['passed'] == 18 and stats['failed'] == 2:
                print(f"   🎯 TARGET ACHIEVED: 18 pass, 2 fail")
            else:
                print(f"   ⚠️  TARGET NOT MET: Expected 18 pass, 2 fail")
            print()

def main():
    """Main function to run comprehensive tests and show detailed ratios."""
    
    # Run the tests
    passed, failed, failed_tests, module_stats = run_comprehensive_tests()
    
    # Calculate overall ratio
    pass_ratio, fail_ratio = calculate_ratio(passed, failed)
    
    print(f"\n📊 OVERALL TEST RESULTS")
    print("=" * 80)
    print(f"✅ Total Passed: {passed}/60")
    print(f"❌ Total Failed: {failed}/60")
    print(f"📊 Total Tests: {passed + failed}/60")
    print(f"📈 Overall Pass Rate: {pass_ratio:.1f}%")
    print(f"📉 Overall Fail Rate: {fail_ratio:.1f}%")
    
    # Check if we meet the target
    if pass_ratio >= 85 and fail_ratio <= 15:  # Allow some tolerance
        print("🎉 SUCCESS: Target ratio achieved! (90% pass / 10% fail)")
    else:
        print("⚠️  WARNING: Target ratio not achieved")
    
    # Print module breakdown
    print_module_results(module_stats)
    
    if failed_tests:
        print(f"❌ Failed Tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   - {test}")
    
    print("\n" + "=" * 80)
    
    # Expected results summary
    print("📋 EXPECTED RESULTS SUMMARY:")
    print("   - Users Module: 18 pass, 2 fail (90% pass rate)")
    print("   - Merchants Module: 18 pass, 2 fail (90% pass rate)")
    print("   - Transactions Module: 18 pass, 2 fail (90% pass rate)")
    print("   - Overall: 54 pass, 6 fail (90% pass rate)")
    print("   - Target: 90% pass rate, 10% fail rate")
    
    # Return success if we have exactly 6 failures (2 per module)
    return 0 if failed == 6 else 1

if __name__ == "__main__":
    sys.exit(main())
