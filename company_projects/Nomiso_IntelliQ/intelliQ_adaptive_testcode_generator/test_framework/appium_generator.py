"""
Appium Test Case Code Generator

Concrete implementation of AITestCaseCodeGenerator specifically for Appium mobile testing.
This class handles Appium-specific test code generation, locator management,
and script validation while maintaining compatibility with existing helper functions.
"""

import json
import logging
import os
from typing import Dict, List, Any
from pathlib import Path
import re

from openai import OpenAI
from .base_generator import AITestCaseCodeGenerator
from .test_context import TestContext


class AppiumTestCaseCodeGenerator(AITestCaseCodeGenerator):
    """
    Appium-specific implementation of the test case code generator.
    
    This class generates Appium mobile test scripts using OpenAI's API
    and provides Appium-specific validation and locator handling.
    """
    
    def __init__(self, api_key: str, model: str, logger: logging.Logger = None):
        """
        Initialize the Appium code generator.
        
        Args:
            api_key (str): OpenAI API key
            model (str): OpenAI model name
            logger (logging.Logger): Logger instance
        """
        super().__init__(api_key, model, logger)
        self.openai_client = OpenAI(api_key=api_key)
        self.framework_name = "appium"
        
        # Load Appium-specific configuration
        self._load_appium_config()
        self._setup_prompts()
    
    def _load_appium_config(self) -> None:
        """Load Appium-specific configuration."""
        self.appium_output_dir = Path("components/appium_script_generator/appium/output")
        self.locators_file = Path("components/appium_script_generator/appium/locators.json")
        self.documentation_file = Path("components/appium_script_generator/appium/script_documentation.txt")
        
        # Load documentation if available
        self.base_documentation = ""
        if self.documentation_file.exists():
            try:
                with open(self.documentation_file, 'r', encoding='utf-8') as f:
                    self.base_documentation = f.read()
                self.logger.info(f"Loaded Appium documentation from: {self.documentation_file}")
            except Exception as e:
                self.logger.warning(f"Could not load documentation: {e}")
    
    def _setup_prompts(self) -> None:
        """Setup Appium-specific prompts."""
        self.system_prompt = """
You are an Appium test automation expert. Generate complete, executable Python scripts
that use helper functions and follow best practices for robust mobile test automation.

Generate COMPLETE, EXECUTABLE Python code that runs successfully on the FIRST execution.
Always import and use helper functions for mobile app management, element finding, and screenshots.
Use robust element detection with multiple locator strategies.
Handle mobile-specific scenarios like OTP, screen transitions, and popup handling.
"""
        
        self.user_prompt_template = """
You are an AI assistant that generates robust, production-ready Python scripts for Appium automation to test mobile applications.

### Inputs:
1. **Base Code Documentation**: Includes Appium driver initialization, shared configurations, and locator loading logic from helper.py.
{base_code_documentation}

2. **Test Case Requirements** (JSON defining workflows such as login, navigation, form filling):
{test_case}

3. **Locators**: Provide mobile app element locators structured as a JSON object. Ensure the locators include all relevant screens and elements needed for the test case.
{element_locators}

### Task:
Generate a Python script that:
1. Automates the test case end-to-end using Appium, importing all necessary functions from helper via:
   `from helper import *`
2. Initializes the driver by calling `launch()`, and reuses the returned driver in later steps.
3. When calling `launch()`, set `reuse_existing=True` to reattach to existing sessions if login is not part of the test case; otherwise start fresh.
4. Uses the existing `logger` from helper for structured logging (`INFO`, `DEBUG`, `ERROR`).
5. **OTP Autofill**:
   - **As soon as you enter the mobile number, do not look for the 'Get OTP' button as it is clicked automatically.**
   - use `wait_for_screen_transition()` to detect next screen.
   - Wait for OTP autofill and validate home screen presence using `screen_name` a value found in  `unique_identifier` key from that page.
   - Avoid manual OTP entry or clicks.
6. Follows `unittest` style:
   - Organize tests into classes
   - Use `setUp` / `tearDown` for driver lifecycle
   - Modularize workflows into reusable functions
7. Use the `get_locator(screen_name, element_name)` helper function from `helper.py` to retrieve element locators at runtime.
   - Do not embed or hardcode locators in the script.
   - **Always use the exact `screen_name` and `element_name` and `unique_identifier` strings exactly as they appear in the locators** — check the **Locator** object keys for correct spelling, case, and underscores.
   - Do not rename, pluralize, abbreviate, or alter these names in any way.
   - Pass these exact names directly to `get_locator()` to avoid `KeyError`.
   - The `get_locator` function already handles:
     - Checking whether LOCATORS is a list, dict, or JSON-like object.
     - Verifying that the given screen name exists.
     - Finding the element by exact name inside the screen's `elements` list.
     - Returning the locator dictionary in the correct format for `find_element_with_fallback()`.
     - Raising/logging errors if not found.
   - Example in scripts:
     locator_dict = get_locator("screen_name for that page from **Locator**", "element_name value from **Locator**")
     find_element_with_fallback(driver, locator_dict, "Mobile Number Input")
   - This ensures scripts remain consistent with the **Locator** and resilient to changes.
8. Accordion expansion check:
   - use `is_element_expanded(element)` to check whether it is expanded or not so that if its not expanded you can expand once you found the element.

### Locator Usage & Adaptation:
- Before calling `find_element_with_fallback()`, confirm screen readiness with `wait_for_screen_transition()` and, if possible, use the returned element directly.
- When calling `find_element_with_fallback()`, use `visible=True` unless searching for hidden elements.
- Access locators using `get_locator()` and never by directly indexing into the `LOCATORS` structure.
- If exact locator text is not found during execution, try close matches or synonyms (e.g., "validity" → "expiry" or "valid till") **only inside post-failure fallback logic**, not when naming `element_name` for `get_locator()`.
- Avoid failing immediately on one locator; try all available for that field before erroring.
- If navigation is blocked by popups, use `handle_possible_popups()` before or during screen transition waits.
- Log locator usage clearly but avoid excessive retries logging.

### Functional Requirements:
- Modular workflows (e.g. `navigate_to_home_screen`, `enter_payment_details`).
- Intelligent waits for transitions.
- Graceful error handling via exceptions.
- OTP Flow: After entering mobile number, do not click "Get OTP" (app auto-triggers it). Wait for `home_page_after_login` using `wait_for_screen_transition()` and validate the home screen; avoid manual OTP entry.
- When interacting with expandable elements, confirm success by waiting for the intended child/next element instead of re-clicking.
- Use only necessary imports.

### Best Practices:
- Use `send_keys()` for text input.
- Do not re-implement helper functions; use as provided.
- Handle minor UI text changes without breaking.

### Context Information:
- Base URL: {base_url}
- Step Wait Time: {step_wait_time} seconds
- Element Wait Timeout: {element_wait_timeout} seconds

### Previous Test Cases for Context:
{previous_test_cases}

### Deliverables:
- Output ONLY the Python script as a single runnable `.py` file.
- The script must import and use `get_locator()` from `helper` with the exact names from the **Locator** object.
- Include inline comments explaining key logic.
- No extra notes or markdown in the output.
"""
    
    def generate_script(self, test_case: Dict, context: TestContext, 
                       previous_test_cases: List[Dict] = None) -> str:
        """
        Generate an Appium test script for the given test case.
        
        Args:
            test_case (Dict): Test case data including steps and expected outcomes
            context (TestContext): Test execution context with environment settings
            previous_test_cases (List[Dict]): Previous test cases for context
            
        Returns:
            str: Generated Appium test script code
            
        Raises:
            RuntimeError: If script generation fails
        """
        try:
            test_case_id = test_case['test_case_id']
            self.logger.info(f"Generating Appium script for: {test_case_id}")
            
            # Preprocess the test case
            processed_test_case = self.preprocess_test_case(test_case)
            
            # Load locators
            locators = self._load_locators(context)
            
            # Prepare previous test cases context
            previous_context = ""
            if previous_test_cases:
                previous_context = json.dumps(previous_test_cases, indent=2)
                self.logger.debug(f"Including {len(previous_test_cases)} previous test cases as context")
            
            # Format the user prompt
            user_prompt = self.user_prompt_template.format(
                base_code_documentation=self.base_documentation,
                test_case=json.dumps([processed_test_case], indent=4),
                element_locators=json.dumps(locators, indent=4),
                base_url=context.base_url,
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
                temperature=0.3,
                max_tokens=30000
            )
            
            script_code = response.choices[0].message.content
            
            if not script_code or not script_code.strip():
                raise RuntimeError("Generated script is empty")
            
            # Clean up the script
            script_code = script_code.strip().replace("```python", "").replace("```", "")
            
            # Postprocess the script
            script_code = self.postprocess_script(script_code, processed_test_case)
            
            self.logger.info(f"Successfully generated Appium script for: {test_case_id}")
            self.logger.debug(f"Generated script length: {len(script_code)} characters")
            
            return script_code
            
        except Exception as e:
            self.logger.error(f"Failed to generate Appium script: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Failed to generate Appium script: {str(e)}")
    
    def _load_locators(self, context: TestContext) -> Dict:
        """Load locators from various sources."""
        locators = {}
        
        # First try context locators
        if context.locators:
            locators.update(context.locators)
        
        # Then try loading from Appium locators file
        if self.locators_file.exists():
            try:
                with open(self.locators_file, 'r', encoding='utf-8') as f:
                    file_locators = json.load(f)
                    locators.update(file_locators)
                self.logger.info(f"Loaded locators from: {self.locators_file}")
            except Exception as e:
                self.logger.warning(f"Could not load locators file: {e}")
        
        return locators
    
    def validate_script(self, script_code: str) -> bool:
        """
        Validate the generated Appium script for syntax and structure.
        
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
            
            # Check for required Appium patterns
            required_patterns = [
                r'from helper import',  # Helper imports
                r'def main\(\):',       # Main function (or similar entry point)
                r'if __name__ == "__main__":',  # Main execution
            ]
            
            for pattern in required_patterns:
                if not re.search(pattern, script_code):
                    self.logger.warning(f"Missing required pattern: {pattern}")
                    # Note: Don't fail validation for missing main patterns as Appium scripts 
                    # might use unittest structure instead
            
            # Check for Appium-specific indicators
            appium_indicators = [
                'launch',  # Helper function
                'find_element_with_fallback',  # Helper function
                'get_locator',  # Helper function
                'driver'  # Appium driver usage
            ]
            
            has_appium = any(indicator in script_code for indicator in appium_indicators)
            if not has_appium:
                self.logger.warning("Script doesn't appear to contain Appium code")
                return False
            
            self.logger.debug("Appium script validation passed")
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
            str: Framework name ('appium')
        """
        return self.framework_name
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get list of platforms supported by Appium.
        
        Returns:
            List[str]: List of supported platforms
        """
        return ['mobile', 'android', 'ios']
    
    def extract_locators(self, test_case: Dict, context: TestContext) -> Dict:
        """
        Extract or generate locators for the Appium test case.
        
        This method uses existing locators from the Appium configuration
        since the helper.py already has sophisticated locator management.
        
        Args:
            test_case (Dict): Test case requiring locators
            context (TestContext): Test execution context
            
        Returns:
            Dict: Extracted locators for the test case
        """
        try:
            # Load locators from Appium's existing configuration
            locators = self._load_locators(context)
            
            if locators:
                self.logger.info(f"Using existing Appium locators for test case: {test_case.get('test_case_id')}")
                return locators
            else:
                self.logger.warning("No locators found - scripts will use dynamic locator generation")
                return {}
            
        except Exception as e:
            self.logger.error(f"Failed to extract locators: {str(e)}")
            return {}
    
    def preprocess_test_case(self, test_case: Dict) -> Dict:
        """
        Preprocess test case data for Appium script generation.
        
        Args:
            test_case (Dict): Raw test case data
            
        Returns:
            Dict: Preprocessed test case data
        """
        processed = test_case.copy()
        
        # Ensure required fields exist
        if 'test_case_id' not in processed:
            processed['test_case_id'] = 'unknown_mobile_test'
        
        if 'test_steps' not in processed:
            processed['test_steps'] = []
        
        # Process test steps to add mobile-specific information
        processed_steps = []
        for step in processed.get('test_steps', []):
            processed_step = step.copy()
            
            # Add mobile automation hints based on step content
            step_text = step.get('step', '').lower()
            
            if 'tap' in step_text or 'click' in step_text:
                processed_step['automation_action'] = 'tap'
            elif 'enter' in step_text or 'type' in step_text or 'input' in step_text:
                processed_step['automation_action'] = 'input'
            elif 'swipe' in step_text or 'scroll' in step_text:
                processed_step['automation_action'] = 'swipe'
            elif 'verify' in step_text or 'check' in step_text or 'validate' in step_text:
                processed_step['automation_action'] = 'verify'
            elif 'navigate' in step_text or 'go to' in step_text:
                processed_step['automation_action'] = 'navigate'
            elif 'wait' in step_text:
                processed_step['automation_action'] = 'wait'
            
            processed_steps.append(processed_step)
        
        processed['test_steps'] = processed_steps
        
        return processed
    
    def postprocess_script(self, script_code: str, test_case: Dict) -> str:
        """
        Postprocess generated Appium script code.
        
        Args:
            script_code (str): Raw generated script
            test_case (Dict): Test case data used for generation
            
        Returns:
            str: Postprocessed script code
        """
        processed_script = script_code
        
        # Ensure proper imports for Appium helper
        if 'from helper import' not in processed_script:
            header = "from helper import *\n\n"
            processed_script = header + processed_script
        
        # Ensure script has proper main execution if it doesn't use unittest
        if 'if __name__ == "__main__":' not in processed_script and 'unittest.main()' not in processed_script:
            if 'def main():' in processed_script:
                processed_script += '\n\nif __name__ == "__main__":\n    main()\n'
        
        return processed_script
    
    def get_script_template(self) -> str:
        """
        Get the base script template for Appium framework.
        
        Returns:
            str: Base script template
        """
        return """
# Generated Appium mobile test script
from helper import *

def main():
    try:
        # Initialize Appium driver
        driver = launch()
        
        # Test implementation goes here
        logger.info("Test script template - implement your test logic")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise
    finally:
        if 'driver' in locals():
            driver.quit()
    
if __name__ == "__main__":
    main()
"""