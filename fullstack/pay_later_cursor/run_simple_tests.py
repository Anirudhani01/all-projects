#!/usr/bin/env python3
"""
Simple test runner that mocks database connections and runs tests.
"""
import sys
import subprocess
import os
from unittest.mock import patch, AsyncMock

def run_simple_tests():
    """Run tests with mocked database connections."""
    
    # Set environment variables for testing
    env = os.environ.copy()
    env['APP_ENV'] = 'test'
    env['PYTHONPATH'] = os.getcwd()
    
    # Mock MongoDB connection before running tests
    with patch('app.db.mongo.MongoDB') as mock_mongo:
        # Configure the mock
        mock_instance = AsyncMock()
        mock_instance.get_database.return_value = AsyncMock()
        mock_instance.get_session.return_value = AsyncMock()
        mock_mongo.return_value = mock_instance
        
        # Build pytest command
        cmd = [
            sys.executable, '-m', 'pytest',
            'app/tests/test_user/test_user_endpoints.py',
            '-v',
            '--tb=short',
            '--disable-warnings'
        ]
        
        print("🚀 Running tests with mocked database...")
        print("=" * 60)
        
        try:
            result = subprocess.run(cmd, env=env, capture_output=False)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False

def main():
    """Main function."""
    print("🧪 Simple LazyPay Test Runner")
    print("=" * 60)
    
    success = run_simple_tests()
    
    if success:
        print("\n✅ Tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
