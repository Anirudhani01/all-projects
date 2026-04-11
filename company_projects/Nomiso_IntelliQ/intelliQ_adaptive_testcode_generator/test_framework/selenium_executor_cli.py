#!/usr/bin/env python3
"""
Selenium Test Script Executor CLI

Direct command line interface for executing Selenium test scripts.
This can be used as a Python module or standalone script.

Usage:
    python -m components.test_framework.selenium_executor_cli
    python -m components.test_framework.selenium_executor_cli --test-id TC001
    python components/test_framework/selenium_executor_cli.py
"""

import argparse
import os
import sys
import logging
import glob
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
    logger = logging.getLogger("SeleniumExecutorCLI")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def find_selenium_scripts(scripts_dir: Optional[str] = None, 
                         test_id: Optional[str] = None, 
                         pattern: Optional[str] = None) -> List[Path]:
    """
    Find Selenium test scripts.
    
    Args:
        scripts_dir: Custom scripts directory
        test_id: Specific test case ID to execute
        pattern: Pattern to match script names
        
    Returns:
        List of script paths to execute
    """
    logger = logging.getLogger("SeleniumExecutorCLI")
    
    # Determine script directories
    if scripts_dir:
        search_dirs = [Path(scripts_dir)]
    else:
        search_dirs = [
            Path('./scripts'),
            Path('./selenium'),
            Path('./components/selenium_script_generator/selenium'),
            Path('./output')  # Fallback output directory
        ]
    
    # Find all Python scripts
    scripts = []
    for search_dir in search_dirs:
        if search_dir.exists():
            logger.info(f"Searching for Selenium scripts in: {search_dir}")
            
            # Get all .py files
            py_files = list(search_dir.glob('*.py'))
            
            # Filter out helper files and non-test scripts
            test_scripts = [
                f for f in py_files 
                if f.name not in ['helper.py', '__init__.py']
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
    
    logger.info(f"Total Selenium scripts to execute: {len(unique_scripts)}")
    return unique_scripts


def execute_selenium_scripts(scripts: List[Path], stop_on_failure: bool = False) -> List[dict]:
    """Execute Selenium test scripts using the framework executor."""
    logger = logging.getLogger("SeleniumExecutorCLI")
    
    try:
        from test_framework.test_context import TestContext
        from selenium_script_generator.test_executor import TestExecutor
        
        context = TestContext()
        executor = TestExecutor(logger)
        results = []
        
        for script_path in scripts:
            test_case_id = script_path.stem
            logger.info(f"Executing Selenium script: {script_path}")
            
            try:
                result = executor.execute_test_script(script_path, test_case_id)
                results.append(result.to_dict())
                
                status = "PASSED" if result.success else "FAILED"
                logger.info(f"Script {test_case_id}: {status} ({result.execution_time:.2f}s)")
                
                # Stop on failure if requested
                if not result.success and stop_on_failure:
                    logger.warning("Stopping execution due to failure")
                    break
                    
            except Exception as e:
                logger.error(f"Failed to execute {script_path}: {str(e)}")
                
                error_result = {
                    'test_case_id': test_case_id,
                    'success': False,
                    'execution_time': 0.0,
                    'script_path': str(script_path),
                    'error_message': str(e),
                    'screenshots': [],
                    'logs': []
                }
                results.append(error_result)
                
                if stop_on_failure:
                    logger.warning("Stopping execution due to error")
                    break
        
        return results
        
    except ImportError as e:
        logger.error(f"Failed to import Selenium executor: {e}")
        logger.error("Make sure you're running from the correct directory and selenium_script_generator is available")
        raise


def generate_report(results: List[dict]) -> Path:
    """Generate execution report."""
    logger = logging.getLogger("SeleniumExecutorCLI")
    
    timestamp = datetime.datetime.now()
    
    # Calculate statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    total_time = sum(r['execution_time'] for r in results)
    
    # Create report
    report = {
        'timestamp': timestamp.isoformat(),
        'framework': 'selenium',
        'execution_type': 'selenium_cli',
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'total_execution_time': total_time,
        'results': results
    }
    
    # Save report
    reports_dir = Path('./reports')
    reports_dir.mkdir(exist_ok=True)
    
    report_filename = f"selenium_execution_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
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
    print(f"SELENIUM TEST EXECUTION SUMMARY")
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
                print(f"  ❌ {result['test_case_id']}: {result['error_message'][:100]}")
    
    print(f"{'='*60}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Execute Selenium test scripts directly',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m components.test_framework.selenium_executor_cli
  python -m components.test_framework.selenium_executor_cli --test-id TC001
  python -m components.test_framework.selenium_executor_cli --pattern login_*
  python -m components.test_framework.selenium_executor_cli --scripts-dir ./custom/selenium/
        """
    )
    
    parser.add_argument(
        '--scripts-dir',
        help='Directory to search for Selenium scripts'
    )
    
    parser.add_argument(
        '--test-id',
        help='Execute specific test case ID'
    )
    
    parser.add_argument(
        '--pattern',
        help='Pattern to match script names (e.g., login_*)'
    )
    
    parser.add_argument(
        '--stop-on-failure',
        action='store_true',
        help='Stop execution on first failure'
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
        logger.info("Starting Selenium test execution")
        
        # Find scripts to execute
        scripts = find_selenium_scripts(
            scripts_dir=args.scripts_dir,
            test_id=args.test_id,
            pattern=args.pattern
        )
        
        if not scripts:
            logger.warning("No Selenium test scripts found to execute")
            print("\nNo scripts found. Try:")
            print("  1. Generating scripts first with main.py")
            print("  2. Specifying --scripts-dir with correct path")
            print("  3. Checking that scripts exist in expected directories")
            return 1
        
        # Execute scripts
        results = execute_selenium_scripts(scripts, args.stop_on_failure)
        
        # Generate report and print summary
        report_path = generate_report(results)
        print_summary(results, report_path)
        
        # Return exit code based on results
        failed_count = sum(1 for r in results if not r['success'])
        return 1 if failed_count > 0 else 0
        
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())