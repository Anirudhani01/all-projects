"""
Base Test Case Code Generator

Abstract base class that defines the interface for test automation code generators.
This allows for easy extension to support different frameworks (Selenium, Appium, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import logging
from pathlib import Path


class AITestCaseCodeGenerator(ABC):
    """
    Abstract base class for AI-powered test case code generators.
    
    This class defines the common interface that all test framework generators
    must implement, ensuring consistency across different automation frameworks.
    """
    
    def __init__(self, api_key: str, model: str, logger: logging.Logger = None):
        """
        Initialize the base code generator.
        
        Args:
            api_key (str): API key for the LLM service
            model (str): Model name to use for code generation
            logger (logging.Logger): Logger instance for logging operations
        """
        self.api_key = api_key
        self.model = model
        self.logger = logger or logging.getLogger(__name__)
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate the generator configuration."""
        if not self.api_key:
            raise ValueError("API key is required for code generation")
        if not self.model:
            raise ValueError("Model name is required for code generation")
    
    @abstractmethod
    def generate_script(self, test_case: Dict, context: 'TestContext', 
                       previous_test_cases: List[Dict] = None) -> str:
        """
        Generate a test automation script for the given test case.
        
        Args:
            test_case (Dict): Test case data including steps and expected outcomes
            context (TestContext): Test execution context with environment settings
            previous_test_cases (List[Dict]): Previous test cases for context
            
        Returns:
            str: Generated test script code
            
        Raises:
            RuntimeError: If script generation fails
        """
        pass
    
    @abstractmethod
    def validate_script(self, script_code: str) -> bool:
        """
        Validate the generated script for syntax and basic structure.
        
        Args:
            script_code (str): Generated script code to validate
            
        Returns:
            bool: True if script is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """
        Get the name of the testing framework this generator supports.
        
        Returns:
            str: Framework name (e.g., 'selenium', 'appium', 'playwright')
        """
        pass
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get list of platforms supported by this generator.
        
        Returns:
            List[str]: List of supported platforms
        """
        return ['web']  # Default implementation for web platforms
    
    def preprocess_test_case(self, test_case: Dict) -> Dict:
        """
        Preprocess test case data before script generation.
        
        This method can be overridden by subclasses to perform framework-specific
        preprocessing of test case data.
        
        Args:
            test_case (Dict): Raw test case data
            
        Returns:
            Dict: Preprocessed test case data
        """
        return test_case
    
    def postprocess_script(self, script_code: str, test_case: Dict) -> str:
        """
        Postprocess generated script code.
        
        This method can be overridden by subclasses to perform framework-specific
        postprocessing of generated script code.
        
        Args:
            script_code (str): Raw generated script
            test_case (Dict): Test case data used for generation
            
        Returns:
            str: Postprocessed script code
        """
        return script_code
    
    def extract_locators(self, test_case: Dict, context: 'TestContext') -> Dict:
        """
        Extract or generate locators for the test case.
        
        This method should be implemented by subclasses to provide framework-specific
        locator extraction logic.
        
        Args:
            test_case (Dict): Test case requiring locators
            context (TestContext): Test execution context
            
        Returns:
            Dict: Extracted locators for the test case
        """
        # Default implementation returns empty dict
        # Subclasses should override this method
        self.logger.warning("Using default empty locators. Override extract_locators() in subclass.")
        return {}
    
    def get_script_template(self) -> str:
        """
        Get the base script template for this framework.
        
        Returns:
            str: Base script template
        """
        return """
# Generated test script
# Framework: {framework}

def main():
    print("Test script template - override in subclass")
    
if __name__ == "__main__":
    main()
""".format(framework=self.get_framework_name())