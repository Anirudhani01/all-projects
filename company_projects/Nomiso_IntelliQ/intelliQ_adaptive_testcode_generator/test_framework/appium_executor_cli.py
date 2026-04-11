#!/usr/bin/env python3
"""
Appium Test Script Executor CLI

Direct command line interface for executing Appium test scripts.
This can be used as a Python module or standalone script.

Usage:
    python -m components.test_framework.appium_executor_cli
    python -m components.test_framework.appium_executor_cli --test-id mobile_TC001
    python components/test_framework/appium_executor_cli.py
"""

import argparse
import os
import sys
import logging
import subprocess
import time
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
import json
import datetime

# Add parent directories to path to enable imports
current_dir = Path(__file__).parent
components_dir = current_dir.parent
root_dir = components_dir.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(components_dir))

def setup_logging() -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger("AppiumExecutorCLI")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def find_appium_scripts(scripts_dir: Optional[str] = None, 
                       test_id: Optional[str] = None, 
                       pattern: Optional[str] = None) -> List[Path]:
    """
    Find Appium test scripts.
    
    Args:
        scripts_dir: Custom scripts directory
        test_id: Specific test case ID to execute
        pattern: Pattern to match script names
        
    Returns:
        List of script paths to execute
    """
    logger = logging.getLogger("AppiumExecutorCLI")
    
    # Determine script directories (prioritize the actual appium output directory)
    if scripts_dir:
        search_dirs = [Path(scripts_dir)]
    else:
        search_dirs = [
            Path('./components/appium_script_generator/appium/output'),
            Path('./appium/output'),
            Path('./appium'),
            Path('./mobile_scripts'),
            Path('./scripts')
        ]
    
    # Find all Python scripts
    scripts = []
    for search_dir in search_dirs:
        if search_dir.exists():
            logger.info(f"Searching for Appium scripts in: {search_dir}")
            
            # Get all .py files
            py_files = list(search_dir.glob('*.py'))
            
            # Filter out helper files and non-test scripts
            test_scripts = [
                f for f in py_files 
                if f.name not in ['helper.py', '__init__.py', 'script_generator.py']
                and not f.name.startswith('__')
            ]
            
            # Apply filters
            if test_id:
                test_scripts = [f for f in test_scripts if test_id in f.stem]
            
            if pattern:
                import fnmatch
                test_scripts = [f for f in test_scripts if fnmatch.fnmatch(f.name, pattern)]
            
            scripts.extend(test_scripts)
            logger.info(f"Found {len(test_scripts)} scripts in {search_dir}")
    
    # Remove duplicates and sort
    unique_scripts = list(set(scripts))
    unique_scripts.sort(key=lambda x: x.name)
    
    logger.info(f"Total Appium scripts to execute: {len(unique_scripts)}")
    return unique_scripts


def execute_appium_script(script_path: Path, timeout: int = 300) -> dict:
    """
    Execute a single Appium test script.
    
    Args:
        script_path: Path to the script to execute
        timeout: Execution timeout in seconds
        
    Returns:
        Execution result dictionary
    """
    logger = logging.getLogger("AppiumExecutorCLI")
    
    test_case_id = script_path.stem
    start_time = time.time()
    
    logger.info(f"Executing Appium script: {test_case_id}")
    
    try:
        # Execute the Python script in its directory (important for helper imports)
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=script_path.parent,  # Run in script directory so "from helper import *" works
            timeout=timeout
        )
        
        execution_time = time.time() - start_time
        success = result.returncode == 0
        
        # Collect logs
        logs = []
        if result.stdout:
            logs.append(f"STDOUT: {result.stdout}")
        if result.stderr:
            logs.append(f"STDERR: {result.stderr}")
        
        # Try to collect screenshots (basic approach)
        screenshots = []
        # Look for common screenshot patterns in the script directory
        screenshot_patterns = ['*.png', '*screenshot*', f'{test_case_id}*.png']
        for pattern in screenshot_patterns:
            screenshots.extend([str(p) for p in script_path.parent.glob(pattern)])
        
        result_dict = {
            'test_case_id': test_case_id,
            'success': success,
            'execution_time': execution_time,
            'script_path': str(script_path),
            'error_message': result.stderr if not success else "",
            'screenshots': list(set(screenshots)),  # Remove duplicates
            'logs': logs
        }
        
        status = "PASSED" if success else "FAILED"
        logger.info(f"Script {test_case_id}: {status} ({execution_time:.2f}s)")
        
        if not success and result.stderr:
            logger.error(f"Error in {test_case_id}: {result.stderr[:200]}")
        
        return result_dict
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        logger.error(f"Script {test_case_id}: TIMEOUT ({execution_time:.2f}s)")
        
        return {
            'test_case_id': test_case_id,
            'success': False,
            'execution_time': execution_time,
            'script_path': str(script_path),
            'error_message': f"Script execution timed out after {timeout} seconds",
            'screenshots': [],
            'logs': []
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Failed to execute {script_path}: {str(e)}")
        
        return {
            'test_case_id': test_case_id,
            'success': False,
            'execution_time': execution_time,
            'script_path': str(script_path),
            'error_message': str(e),
            'screenshots': [],
            'logs': []
        }


def execute_appium_scripts(scripts: List[Path], stop_on_failure: bool = False, 
                          timeout: int = 300) -> List[dict]:
    """Execute Appium test scripts."""
    logger = logging.getLogger("AppiumExecutorCLI")
    
    results = []
    
    for script_path in scripts:
        result = execute_appium_script(script_path, timeout)
        results.append(result)
        
        # Stop on failure if requested
        if not result['success'] and stop_on_failure:
            logger.warning("Stopping execution due to failure")
            break
    
    return results


def check_appium_prerequisites():
    """Check if Appium environment is ready."""
    logger = logging.getLogger("AppiumExecutorCLI")
    
    checks = []
    
    # Check if Appium server is reachable
    try:
        import requests
        appium_url = os.getenv("APPIUM_SERVER_URL", "http://localhost:4723")
        response = requests.get(f"{appium_url}/sessions", timeout=5)
        checks.append(("Appium Server", True, f"Reachable at {appium_url}"))
    except Exception as e:
        checks.append(("Appium Server", False, f"Not reachable: {str(e)}"))
    
    # Check if adb is available
    try:
        result = subprocess.run(['adb', 'version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            checks.append(("ADB", True, "Available"))
        else:
            checks.append(("ADB", False, "Not available"))
    except Exception:
        checks.append(("ADB", False, "Not available"))
    
    # Check for connected devices
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = [line for line in lines if line.strip() and 'device' in line]
            if devices:
                checks.append(("Android Devices", True, f"{len(devices)} device(s) connected"))
            else:
                checks.append(("Android Devices", False, "No devices connected"))
        else:
            checks.append(("Android Devices", False, "Cannot check devices"))
    except Exception:
        checks.append(("Android Devices", False, "Cannot check devices"))
    
    # Print checks
    print("\n" + "="*50)
    print("APPIUM ENVIRONMENT CHECK")
    print("="*50)
    
    all_ok = True
    for name, status, message in checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name:<20}: {message}")
        if not status:
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Some prerequisites are not met. Tests may fail.")
        print("   Make sure Appium server is running and devices are connected.")
    else:
        print("\n✅ Environment looks good for Appium testing!")
    
    print("="*50)
    return all_ok


def generate_report(results: List[dict]) -> Path:
    """Generate execution report."""
    logger = logging.getLogger("AppiumExecutorCLI")
    
    timestamp = datetime.datetime.now()
    
    # Calculate statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    total_time = sum(r['execution_time'] for r in results)
    
    # Create report
    report = {
        'timestamp': timestamp.isoformat(),
        'framework': 'appium',
        'execution_type': 'appium_cli',
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'total_execution_time': total_time,
        'results': results
    }
    
    # Save report
    reports_dir = Path('./reports')
    reports_dir.mkdir(exist_ok=True)
    
    report_filename = f"appium_execution_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    report_path = reports_dir / report_filename
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Execution report saved: {report_path}")
    return report_path


def print_summary(results: List[dict], report_path: Path):
    """Print execution summary."""
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    total_time = sum(r['execution_time'] for r in results)
    
    print(f"\n{'='*60}")
    print(f"APPIUM TEST EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests:     {total_tests}")
    print(f"Passed:          {passed_tests}")
    print(f"Failed:          {failed_tests}")
    
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"Success Rate:    {success_rate:.1f}%")
    
    print(f"Total Time:      {total_time:.2f} seconds")
    print(f"Report:          {report_path}")
    
    # Show failed tests
    if failed_tests > 0:
        print(f"\nFAILED TESTS:")
        for result in results:
            if not result['success']:
                print(f"  📱❌ {result['test_case_id']}: {result['error_message'][:100]}")
    
    print(f"{'='*60}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Execute Appium test scripts directly',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m components.test_framework.appium_executor_cli
  python -m components.test_framework.appium_executor_cli --test-id mobile_TC001
  python -m components.test_framework.appium_executor_cli --pattern mobile_*
  python -m components.test_framework.appium_executor_cli --scripts-dir ./appium/output/
        """
    )
    
    parser.add_argument(
        '--scripts-dir',
        help='Directory to search for Appium scripts'
    )
    
    parser.add_argument(
        '--test-id',
        help='Execute specific test case ID'
    )
    
    parser.add_argument(
        '--pattern',
        help='Pattern to match script names (e.g., mobile_*)'
    )
    
    parser.add_argument(
        '--stop-on-failure',
        action='store_true',
        help='Stop execution on first failure'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Script execution timeout in seconds (default: 300)'
    )
    
    parser.add_argument(
        '--skip-env-check',
        action='store_true',
        help='Skip Appium environment prerequisite check'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Setup logging
    logger = setup_logging()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        logger.info("Starting Appium test execution")
        
        # Check environment prerequisites
        if not args.skip_env_check:
            env_ok = check_appium_prerequisites()
            if not env_ok:
                response = input("\nContinue anyway? (y/N): ").strip().lower()
                if response != 'y':
                    logger.info("Execution cancelled by user")
                    return 1
        
        # Find scripts to execute
        scripts = find_appium_scripts(
            scripts_dir=args.scripts_dir,
            test_id=args.test_id,
            pattern=args.pattern
        )
        
        if not scripts:
            logger.warning("No Appium test scripts found to execute")
            print("\nNo scripts found. Try:")
            print("  1. Generating scripts first with main.py (TEST_FRAMEWORK=appium)")
            print("  2. Specifying --scripts-dir with correct path")
            print("  3. Checking that scripts exist in ./components/appium_script_generator/appium/output/")
            return 1
        
        # Execute scripts
        results = execute_appium_scripts(scripts, args.stop_on_failure, args.timeout)
        
        # Generate report and print summary
        report_path = generate_report(results)
        print_summary(results, report_path)
        
        # Return exit code based on results
        failed_count = sum(1 for r in results if not r['success'])
        return 1 if failed_count > 0 else 0
        
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())