"""
Appium Test Generator Service

Service function for generating and executing Appium tests from JSON input.
This mirrors the selenium_test_generator.py structure for consistency.
"""

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
from test_framework.appium_generator import AppiumTestCaseCodeGenerator


def setup_logging() -> logging.Logger:
    """Set up logging for Appium test generator."""
    logger = logging.getLogger("AppiumTestGenerator")
    logger.setLevel(logging.DEBUG)  # Set logger to DEBUG to capture all levels
    
    if not logger.handlers:
        # Create logs folder in same directory as this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(current_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        log_file = os.path.join(logs_dir, "appium_test.log")
        
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
    directories = ["components/appium_script_generator/appium/output", "reports"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def generate_appium_from_json(json_input: Union[str, List[Dict], Path]) -> List:
    """Generate and execute Appium tests from JSON input using the new framework."""
    # Setup environment
    load_environment()
    validate_config()
    
    try:
        # Initialize test context with mobile-specific settings
        context = TestContext()
        
        # Override context settings for Appium
        context.test_framework = 'appium'
        context.scripts_dir = "components/appium_script_generator/appium/output"
        
        # Load Appium locators if available
        locators_path = Path("components/appium_script_generator/appium/locators.json")
        if locators_path.exists():
            with open(locators_path, "r", encoding='utf-8') as file:
                locators = json.load(file)
                context.update_locators(locators)
        
        # Initialize Appium generator
        appium_generator = AppiumTestCaseCodeGenerator(
            context.api_key,
            context.model_name,
            context.get_logger(__name__)
        )
        
        # Initialize test runner with custom script writer for Appium
        runner = TestRunner(context, appium_generator)
        
        # Override script writer to save in Appium output directory
        from test_framework.script_writer import ScriptWriter
        appium_script_writer = AppiumScriptWriter(context)
        runner.script_writer = appium_script_writer
        
        context.get_logger(__name__).info("Appium Test Generator initialized successfully")
        
        # Run tests
        results = runner.run_from_json(json_input)
        
        # Generate report
        runner.generate_report(results)
        
        return results
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to generate Appium tests from JSON: {str(e)}")
        raise


class AppiumScriptWriter:
    """Custom script writer for Appium that saves to the correct directory."""
    
    def __init__(self, context: TestContext):
        self.context = context
        self.logger = context.get_logger(__name__)
        
        # Ensure Appium output directory exists
        self.output_dir = Path("components/appium_script_generator/appium/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_script(self, script_code: str, test_case_id: str) -> Path:
        """
        Save script to Appium output directory.
        
        Args:
            script_code (str): Generated script code
            test_case_id (str): Test case identifier
            
        Returns:
            Path: Path to saved script file
        """
        try:
            # Clean test case ID for filename
            clean_id = test_case_id.replace(' ', '_').replace('-', '_')
            script_filename = f"{clean_id}.py"
            script_path = self.output_dir / script_filename
            
            # Write script to file
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_code)
            
            self.logger.info(f"Appium script saved: {script_path}")
            return script_path
            
        except Exception as e:
            self.logger.error(f"Failed to save Appium script: {str(e)}")
            raise


def main():
    """Main entry point for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python appium_test_generator.py <json_file>")
        print("Example:")
        print("  python appium_test_generator.py test_cases_mobile.json")
        return 1
    
    input_arg = sys.argv[1]
    
    try:
        # Process JSON file
        if Path(input_arg).exists() or input_arg.endswith('.json'):
            results = generate_appium_from_json(input_arg)
            
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