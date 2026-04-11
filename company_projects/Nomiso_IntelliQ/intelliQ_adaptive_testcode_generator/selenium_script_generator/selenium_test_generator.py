import os
import sys
import json
import datetime
import logging
from pathlib import Path
from typing import List, Dict, Union, Tuple
from dotenv import load_dotenv

# Import test framework modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from test_framework import TestContext, TestRunner
from test_framework.selenium_generator import SeleniumTestCaseCodeGenerator

def setup_logging() -> logging.Logger:
    logger = logging.getLogger("SeleniumTestGenerator")
    logger.setLevel(logging.DEBUG)  # Set logger to DEBUG to capture all levels
    
    if not logger.handlers:
        # Create logs folder in same directory as this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(current_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        log_file = os.path.join(logs_dir, "selenium_test.log")
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Add file handler - captures DEBUG and above
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Add console handler - only INFO and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger



def load_environment() -> None:
    """Load environment variables from .env file."""
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


def validate_config() -> None:
    """Validate required configuration."""
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("Missing required environment variable: OPENAI_API_KEY")


def create_directories() -> None:
    """Create necessary directories."""
    for directory in ["selenium", "reports"]:
        Path(directory).mkdir(exist_ok=True)


# All legacy functions removed - functionality moved to TestRunner and TestContext
# The old AICodeGenerator class has been completely removed


def generate_from_json(json_input: Union[str, List[Dict], Path]) -> List:
    """Generate and execute tests from JSON input using the new framework."""
    # Setup environment
    load_environment()
    validate_config()
    
    try:
        # Initialize test context
        context = TestContext()
        
        # Load locators if available (for backward compatibility)
        locators_path = Path("locators.json")
        if locators_path.exists():
            with open(locators_path, "r", encoding='utf-8') as file:
                locators = json.load(file)
                context.update_locators(locators)
        
        # Initialize Selenium generator
        selenium_generator = SeleniumTestCaseCodeGenerator(
            context.api_key,
            context.model_name,
            context.get_logger(__name__)
        )
        
        # Initialize test runner
        runner = TestRunner(context, selenium_generator)
        
        context.get_logger(__name__).info("Selenium Test Generator initialized successfully")
        
        # Run tests
        results = runner.run_from_json(json_input)
        
        # Generate report
        runner.generate_report(results)
        
        return results
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to generate tests from JSON: {str(e)}")
        raise


def main():
    """Main entry point for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python selenium_test_generator.py <json_file>")
        print("Example:")
        print("  python selenium_test_generator.py test_cases.json")
        return 1
    
    input_arg = sys.argv[1]
    
    try:
        # Process JSON file
        if Path(input_arg).exists() or input_arg.endswith('.json'):
            results = generate_from_json(input_arg)
            
            passed = sum(1 for r in results if r.success)
            total = len(results)
            print(f"\nExecution Summary:")
            print(f"Total Tests: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {total - passed}")
            
            return 0 if passed == total else 1
        else:
            print("Error: Please provide a valid JSON file")
            return 1
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())