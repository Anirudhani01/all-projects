"""
Selenium Test Case Code Generator

Concrete implementation of AITestCaseCodeGenerator specifically for Selenium WebDriver.
This class handles Selenium-specific test code generation, locator management,
and script validation.
"""

import json
import logging
from typing import Dict, List, Any
from pathlib import Path
import re

from openai import OpenAI
from .base_generator import AITestCaseCodeGenerator
from .test_context import TestContext


class SeleniumTestCaseCodeGenerator(AITestCaseCodeGenerator):
    """
    Selenium-specific implementation of the test case code generator.
    
    This class generates Selenium WebDriver test scripts using OpenAI's API
    and provides Selenium-specific validation and locator handling.
    """
    
    def __init__(self, api_key: str, model: str, logger: logging.Logger = None):
        """
        Initialize the Selenium code generator.
        
        Args:
            api_key (str): OpenAI API key
            model (str): OpenAI model name
            logger (logging.Logger): Logger instance
        """
        super().__init__(api_key, model, logger)
        self.openai_client = OpenAI(api_key=api_key)
        self.framework_name = "selenium"
        
        # Load Selenium-specific prompts
        self._load_prompts()
    
    def _load_prompts(self) -> None:
        """Load Selenium-specific prompts."""
        try:
            # Try to load from selenium_script_generator prompts
            from ..selenium_script_generator.prompts import selenium_system_prompt, selenium_user_prompt
            self.system_prompt = selenium_system_prompt
            self.user_prompt_template = selenium_user_prompt
            
        except ImportError:
            # Fallback to basic prompts if module not available
            self.logger.warning("Could not load Selenium prompts, using fallback")
            self._setup_fallback_prompts()
    
    def _setup_fallback_prompts(self) -> None:
        """Setup fallback prompts if main prompts are not available."""
        self.system_prompt = """
You are a Selenium test automation expert. Generate complete, executable Python Selenium scripts
that use helper functions and follow best practices for robust test automation.

Generate COMPLETE, EXECUTABLE Python code that runs successfully on the FIRST execution.
Always import and use helper functions for browser management, element finding, and screenshots.
Use robust element detection with multiple locator strategies.
Take screenshots after every step for debugging and reporting.
"""
        
        self.user_prompt_template = """
Create a Selenium Python test script for the following test case:

Test Case: {test_case}
Context: {context}
Previous Test Cases: {previous_test_cases}

Generate a complete Python script that uses helper functions and follows Selenium best practices.
"""
    
    def generate_script(self, test_case: Dict, context: TestContext, 
                       previous_test_cases: List[Dict] = None) -> str:
        """
        Generate a Selenium test script for the given test case.
        
        Args:
            test_case (Dict): Test case data including steps and expected outcomes
            context (TestContext): Test execution context with environment settings
            previous_test_cases (List[Dict]): Previous test cases for context
            
        Returns:
            str: Generated Selenium test script code
            
        Raises:
            RuntimeError: If script generation fails
        """
        try:
            test_case_id = test_case['test_case_id']
            self.logger.info(f"Generating Selenium script for: {test_case_id}")
            
            # Preprocess the test case
            processed_test_case = self.preprocess_test_case(test_case)
            
            # Get credentials from context (securely)
            credentials = context.get_credentials()
            
            # Prepare previous test cases context
            previous_context = ""
            if previous_test_cases:
                previous_context = json.dumps(previous_test_cases, indent=2)
                self.logger.debug(f"Including {len(previous_test_cases)} previous test cases as context")
            
            # Format the user prompt
            user_prompt = self.user_prompt_template.format(
                test_case=json.dumps([processed_test_case], indent=4),
                test_case_id=test_case_id,
                element_locators=json.dumps(context.locators, indent=4),
                base_url=context.base_url,
                username=credentials.get('username', ''),
                password=credentials.get('password', ''),
                step_wait_time=context.step_wait_time,
                element_wait_timeout=context.element_wait_timeout,
                previous_test_cases=previous_context
            )
            
            self.logger.debug(f"System prompt length: {len(self.system_prompt)}")
            self.logger.debug(f"User prompt length: {len(user_prompt)}")
            
            # Generate script using OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0
            )
            
            script_code = response.choices[0].message.content
            
            if not script_code or not script_code.strip():
                raise RuntimeError("Generated script is empty")
            
            # Postprocess the script
            script_code = self.postprocess_script(script_code, processed_test_case)
            
            self.logger.info(f"Successfully generated Selenium script for: {test_case_id}")
            self.logger.debug(f"Generated script length: {len(script_code)} characters")
            
            return script_code
            
        except Exception as e:
            self.logger.error(f"Failed to generate Selenium script: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Failed to generate Selenium script: {str(e)}")
    
    def validate_script(self, script_code: str) -> bool:
        """
        Validate the generated Selenium script for syntax and structure.
        
        Args:
            script_code (str): Generated script code to validate
            
        Returns:
            bool: True if script is valid, False otherwise
        """
        if not script_code or not script_code.strip():
            self.logger.error("Script code is empty")
            return False
        
        try:
            # Check Python syntax
            compile(script_code, '<script>', 'exec')
            
            # Check for required Selenium patterns
            required_patterns = [
                r'from helper import',  # Helper imports
                r'def main\(\):',       # Main function
                r'if __name__ == "__main__":',  # Main execution
            ]
            
            for pattern in required_patterns:
                if not re.search(pattern, script_code):
                    self.logger.warning(f"Missing required pattern: {pattern}")
                    return False
            
            # Check for Selenium-specific imports/usage
            selenium_indicators = [
                'webdriver',
                'driver',
                'launch_browser',
                'find_element'
            ]
            
            has_selenium = any(indicator in script_code for indicator in selenium_indicators)
            if not has_selenium:
                self.logger.warning("Script doesn't appear to contain Selenium code")
                return False
            
            self.logger.debug("Selenium script validation passed")
            return True
            
        except SyntaxError as e:
            self.logger.error(f"Script syntax error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Script validation error: {e}")
            return False
    
    def get_framework_name(self) -> str:
        """
        Get the framework name.
        
        Returns:
            str: Framework name ('selenium')
        """
        return self.framework_name
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get list of platforms supported by Selenium.
        
        Returns:
            List[str]: List of supported platforms
        """
        return ['web']
    
    def extract_locators(self, test_case: Dict, context: TestContext) -> Dict:
        """
        Extract or generate locators for the Selenium test case.
        
        This method implements dynamic locator generation based on the test case
        requirements and application profile.
        
        Args:
            test_case (Dict): Test case requiring locators
            context (TestContext): Test execution context
            
        Returns:
            Dict: Extracted locators for the test case
        """
        try:
            # If using static locators, return existing ones
            if context.locator_extraction_mode == 'static' and context.locators:
                return context.locators
            
            # Dynamic locator generation based on test case analysis
            locators = self._generate_dynamic_locators(test_case, context)
            
            self.logger.info(f"Generated {len(locators)} locators for test case: {test_case.get('test_case_id')}")
            return locators
            
        except Exception as e:
            self.logger.error(f"Failed to extract locators: {str(e)}")
            return {}
    
    def _generate_dynamic_locators(self, test_case: Dict, context: TestContext) -> Dict:
        """
        Generate dynamic locators based on test case analysis.
        
        Args:
            test_case (Dict): Test case to analyze
            context (TestContext): Test execution context
            
        Returns:
            Dict: Generated locators
        """
        locators = {}
        
        # Analyze test steps to identify required elements
        test_steps = test_case.get('test_steps', [])
        
        # Common locator categories for web applications
        common_locators = {
            'login_page': {
                'username_field': {
                    'name': 'username',
                    'id': 'username',
                    'xpath': '//input[@type="text"]',
                    'css_selector': 'input[type="text"]'
                },
                'password_field': {
                    'name': 'password',
                    'id': 'password',
                    'xpath': '//input[@type="password"]',
                    'css_selector': 'input[type="password"]'
                },
                'login_button': {
                    'xpath': '//button[@type="submit"]',
                    'css_selector': 'button[type="submit"]',
                    'xpath_by_text': '//button[contains(text(), "Login")]'
                }
            },
            'navigation': {
                'menu_items': {
                    'xpath': '//nav//a',
                    'css_selector': 'nav a'
                }
            }
        }
        
        # Extract specific locators based on application profile
        if context.application_profile == 'opencrx':
            locators.update(self._get_opencrx_locators())
        else:
            locators.update(common_locators)
        
        # Analyze test steps to add specific locators
        for step in test_steps:
            step_text = step.get('step', '').lower()
            
            # Look for specific UI elements mentioned in steps
            if 'click' in step_text and 'button' in step_text:
                # Add generic button locators
                if 'buttons' not in locators:
                    locators['buttons'] = {}
                
            if 'enter' in step_text or 'input' in step_text:
                # Add generic input locators
                if 'inputs' not in locators:
                    locators['inputs'] = {}
        
        return locators
    
    def _get_opencrx_locators(self) -> Dict:
        """
        Get OpenCRX-specific locators.
        
        Returns:
            Dict: OpenCRX locators
        """
        return {
            'login_page': {
                'username_field': {
                    'name': 'j_username',
                    'xpath': '//input[@name="j_username"]',
                    'css_selector': 'input[name="j_username"]'
                },
                'password_field': {
                    'name': 'j_password',
                    'xpath': '//input[@name="j_password"]',
                    'css_selector': 'input[name="j_password"]'
                },
                'login_button': {
                    'xpath': '//button[@type="submit"]',
                    'css_selector': 'button[type="submit"]'
                }
            },
            'navigation': {
                'products_tab': {
                    'xpath': '//div[@id="bs-top-navigation"]//a[normalize-space()="Products"]',
                    'xpath_alt': '//a[@title="Products" and contains(@class,"nav-link")]'
                }
            },
            'products_page': {
                'new_button': {
                    'xpath': '//div[@id="G_0"]//button[normalize-space()="New" and contains(@class,"btn-sm")]',
                    'xpath_alt': '//h2[contains(normalize-space(),"Products")]/following::button[normalize-space()="New"][1]'
                }
            }
        }
    
    def preprocess_test_case(self, test_case: Dict) -> Dict:
        """
        Preprocess test case data for Selenium script generation.
        
        Args:
            test_case (Dict): Raw test case data
            
        Returns:
            Dict: Preprocessed test case data
        """
        processed = test_case.copy()
        
        # Ensure required fields exist
        if 'test_case_id' not in processed:
            processed['test_case_id'] = 'unknown_test'
        
        if 'test_steps' not in processed:
            processed['test_steps'] = []
        
        # Process test steps to add Selenium-specific information
        processed_steps = []
        for step in processed.get('test_steps', []):
            processed_step = step.copy()
            
            # Add automation hints based on step content
            step_text = step.get('step', '').lower()
            
            if 'click' in step_text:
                processed_step['automation_action'] = 'click'
            elif 'enter' in step_text or 'type' in step_text:
                processed_step['automation_action'] = 'input'
            elif 'verify' in step_text or 'check' in step_text:
                processed_step['automation_action'] = 'verify'
            elif 'navigate' in step_text or 'go to' in step_text:
                processed_step['automation_action'] = 'navigate'
            
            processed_steps.append(processed_step)
        
        processed['test_steps'] = processed_steps
        
        return processed
    
    def postprocess_script(self, script_code: str, test_case: Dict) -> str:
        """
        Postprocess generated Selenium script code.
        
        Args:
            script_code (str): Raw generated script
            test_case (Dict): Test case data used for generation
            
        Returns:
            str: Postprocessed script code
        """
        processed_script = script_code
        
        # Remove any code block markers that might be in the response
        processed_script = re.sub(r'^```python\s*\n', '', processed_script, flags=re.MULTILINE)
        processed_script = re.sub(r'^```\s*$', '', processed_script, flags=re.MULTILINE)
        
        # Ensure proper imports are at the top
        if 'import sys' not in processed_script or 'from helper import' not in processed_script:
            header = """import sys
import os
sys.path.append(os.path.dirname(__file__))
from helper import *

"""
            # Remove existing import statements
            processed_script = re.sub(r'^(import sys.*?\n|import os.*?\n|sys\.path\.append.*?\n|from helper import.*?\n)', '', processed_script, flags=re.MULTILINE)
            processed_script = header + processed_script
        
        # Ensure script has proper main execution
        if 'if __name__ == "__main__":' not in processed_script:
            processed_script += '\n\nif __name__ == "__main__":\n    main()\n'
        
        return processed_script