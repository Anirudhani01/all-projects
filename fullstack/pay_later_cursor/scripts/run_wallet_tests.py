#!/usr/bin/env python3
"""
Test runner script for wallet system tests.
"""

import sys
import os
import subprocess
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import structlog

logger = structlog.get_logger(__name__)


async def run_wallet_tests():
    """Run all wallet system tests."""
    try:
        logger.info("🧪 Starting wallet system tests...")
        
        # Test categories
        test_categories = [
            ("Unit Tests - Models", "app/tests/test_wallet/test_wallet_models.py"),
            ("Unit Tests - Service", "app/tests/test_wallet/test_wallet_service.py"),
            ("Integration Tests", "app/tests/test_wallet/test_wallet_integration.py"),
            ("API Endpoint Tests", "app/tests/test_wallet/test_wallet_endpoints.py"),
        ]
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category_name, test_file in test_categories:
            logger.info(f"\n--- Running {category_name} ---")
            
            if os.path.exists(test_file):
                try:
                    # Run pytest for the specific test file
                    result = subprocess.run([
                        sys.executable, "-m", "pytest", test_file,
                        "-v", "--tb=short", "--asyncio-mode=auto"
                    ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
                    
                    if result.returncode == 0:
                        logger.info(f"✅ {category_name} passed")
                        # Count passed tests (rough estimate)
                        passed_count = result.stdout.count("PASSED")
                        passed_tests += passed_count
                        total_tests += passed_count
                    else:
                        logger.error(f"❌ {category_name} failed")
                        logger.error(f"Error output: {result.stderr}")
                        # Count failed tests (rough estimate)
                        failed_count = result.stdout.count("FAILED")
                        failed_tests += failed_count
                        total_tests += failed_count
                        
                except Exception as e:
                    logger.error(f"❌ Error running {category_name}: {str(e)}")
                    failed_tests += 1
                    total_tests += 1
            else:
                logger.warning(f"⚠️ Test file not found: {test_file}")
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("📊 WALLET TEST RESULTS SUMMARY")
        logger.info("="*50)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        
        if failed_tests == 0:
            logger.info("🎉 All wallet tests passed!")
            return True
        else:
            logger.error(f"❌ {failed_tests} tests failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        return False


def main():
    """Main function."""
    logger.info("🚀 Starting wallet test runner...")
    
    # Run tests
    success = asyncio.run(run_wallet_tests())
    
    if success:
        logger.info("✅ All wallet tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Some wallet tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
