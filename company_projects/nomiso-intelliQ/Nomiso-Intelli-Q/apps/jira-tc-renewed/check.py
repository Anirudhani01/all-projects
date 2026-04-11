#!/usr/bin/env python3
"""
Pure Prompt Test Converter
Converts test cases to Selenium code using LLM (OpenAI)
With support for test dependencies and browser session reuse

Usage:
    python check.py QA-396
    or just:
    python check.py  # Auto-detect latest
"""

import os
import re
import sys
import json
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'test_case_generator.env'))

# Configure logging - simplified for this version
def log_info(message):
    print(f"INFO: {message}")

def log_error(message):
    print(f"ERROR: {message}")

def log_status(message):
    print(f"STATUS: {message}")


# Enhanced Jira Integration
class JiraClient:
    def __init__(self):
        self.domain = os.getenv("JIRA_DOMAIN")  # Fix typo in environment variable name
        self.email = os.getenv("EMAIL") 
        self.api_token = os.getenv("JIRA_API")
        
        if not all([self.domain, self.email, self.api_token]):
            log_error("Jira credentials not fully configured in environment variables")
            log_error(f"Domain: {self.domain}, Email: {self.email}, Token: {'Present' if self.api_token else 'Missing'}")
            self.enabled = False
        else:
            self.enabled = True
            self.auth = HTTPBasicAuth(self.email, self.api_token)
            self.headers = {"Accept": "application/json"}
            self.base_url = f"https://{self.domain}/rest/api/3"
            log_info("Jira client initialized successfully")
            log_info(f"Using Jira domain: {self.domain}")
    
    def get_issue(self, issue_key):
        """Get complete issue details from Jira"""
        if not self.enabled:
            log_info("Jira client not enabled, skipping API call")
            return None
            
        try:
            url = f"{self.base_url}/issue/{issue_key}?expand=issuelinks"
            log_info(f"Fetching issue data from {url}")
            response = requests.get(url, headers=self.headers, auth=self.auth)
            response.raise_for_status()
            log_info(f"Successfully retrieved issue {issue_key}")
            return response.json()
        except Exception as e:
            log_error(f"Error fetching Jira issue {issue_key}: {str(e)}")
            return None
    
    def get_issue_links(self, issue_key):
        """Get all linked issues for a Jira issue"""
        issue_data = self.get_issue(issue_key)
        if not issue_data:
            return []
            
        links = []
        try:
            # Get standard issue links
            issue_links = issue_data.get('fields', {}).get('issuelinks', [])
            log_info(f"Found {len(issue_links)} issue links for {issue_key}")
            
            for link in issue_links:
                link_type = link.get('type', {}).get('name', '').lower()
                link_direction = link.get('type', {}).get('inward', '').lower()
                
                # Check for blocking/dependency relationships
                dependency_terms = ['block', 'depend', 'require', 'prerequisite']
                is_dependency = any(term in link_type for term in dependency_terms)
                
                if is_dependency:
                    # Determine if this issue is blocked by the other
                    if 'inwardIssue' in link:
                        linked_key = link['inwardIssue']['key']
                        links.append({
                            'type': link_type, 
                            'key': linked_key,
                            'direction': 'blocked by'
                        })
                        log_info(f"Found dependency: {issue_key} is {link_direction} {linked_key}")
            
            # Also check for all custom fields
            custom_fields = issue_data.get('fields', {})
            for field_key, field_value in custom_fields.items():
                # Look for fields that might contain dependency information
                if field_value and any(term in field_key.lower() for term in ['depend', 'block', 'link', 'relation']):
                    log_info(f"Checking custom field {field_key} for dependencies")
                    
                    # Handle different field value types
                    if isinstance(field_value, list):
                        for item in field_value:
                            if isinstance(item, dict) and 'key' in item:
                                links.append({
                                    'type': 'depends on',
                                    'key': item['key'],
                                    'direction': 'blocked by'
                                })
                                log_info(f"Found dependency in custom field: {issue_key} depends on {item['key']}")
                    elif isinstance(field_value, dict) and 'key' in field_value:
                        links.append({
                            'type': 'depends on',
                            'key': field_value['key'],
                            'direction': 'blocked by'
                        })
                        log_info(f"Found dependency in custom field: {issue_key} depends on {field_value['key']}")
                    elif isinstance(field_value, str) and re.search(r'[A-Z]+-\d+', field_value):
                        # Extract issue keys from text fields
                        matches = re.findall(r'[A-Z]+-\d+', field_value)
                        for match in matches:
                            links.append({
                                'type': 'depends on',
                                'key': match,
                                'direction': 'blocked by'
                            })
                            log_info(f"Found dependency in text field: {issue_key} depends on {match}")
                        
            return links
        except Exception as e:
            log_error(f"Error parsing issue links for {issue_key}: {str(e)}")
            return []
    
    def find_dependencies(self, issue_key):
        """Find all issues that this issue depends on"""
        links = self.get_issue_links(issue_key)
        dependencies = [link['key'] for link in links if link['direction'] == 'blocked by']
        
        if dependencies:
            log_info(f"Found dependencies for {issue_key}: {dependencies}")
        else:
            log_info(f"No dependencies found for {issue_key}")
            
        return dependencies

# Initialize Jira client
jira_client = JiraClient()


def find_latest_test_case():
    """Auto-detect latest test case JSON file"""
    base_dir = Path("test_cases")
    for folder in sorted(base_dir.glob("*"), reverse=True):
        if folder.is_dir():
            json_files = sorted(folder.glob("*.json"), reverse=True)
            if json_files:
                log_info(f"Latest test case found: {json_files[0]}")
                return json_files[0]
    return None


def find_test_case_by_id(test_id):
    """Locate test case file by ID"""
    base_dir = Path("test_cases")

    # First try direct file
    direct_file = base_dir / f"{test_id}.json"
    if direct_file.exists():
        return direct_file

    # Then look inside folders
    for folder in sorted(base_dir.glob("*"), reverse=True):
        if folder.is_dir():
            file_path = folder / f"{test_id}.json"
            if file_path.exists():
                return file_path

    return None


def load_test_case(test_id):
    """Load a test case from JSON file"""
    test_file = find_test_case_by_id(test_id)
    if not test_file:
        print(f"❌ Test case file for {test_id} not found.")
        return None
        
    print(f"✅ Found test case: {test_file}")
    
    with open(test_file, "r", encoding="utf-8") as f:
        test_case = json.load(f)
    
    return test_case


def extract_test_steps(test_case):
    """Format steps into structured text"""
    steps = test_case.get("test_steps", [])
    step_lines = []
    for step in steps:
        step_num = step.get("step_number", "")
        description = step.get("test_step", "")
        expected = step.get("expected_output", "")
        step_lines.append(f"Step {step_num}: {description}\nExpected Result: {expected}\n")
    return "\n".join(step_lines)


def find_test_dependencies(test_id):
    """
    Dynamically determine test dependencies directly from Jira.
    
    Returns:
        String: Dependency test ID if found, None otherwise
    """
    # Get dependencies from Jira
    if jira_client.enabled:
        jira_dependencies = jira_client.find_dependencies(test_id)
        if jira_dependencies:
            log_info(f"Dependencies found in Jira for {test_id}: {jira_dependencies}")
            # Return the first dependency found - most critical one
            return jira_dependencies[0]
            
    log_info(f"No dependencies found for {test_id} in Jira")
    return None


def build_prompt(test_id, test_summary, steps_text, chrome_driver_path, element_locators):
    """Create a powerful prompt that ensures full utilization of the locators.json file"""
    
    # Fix Chrome driver path - convert backslashes to forward slashes
    chrome_driver_path_fixed = chrome_driver_path.replace('\\', '/')
    
    return f"""
    You are a world-class Selenium test automation expert specialized in OpenCRX. Create perfect, production-ready Python code that can execute every step of this test case with precision.

    YOUR TASK:
    1. PARSE AND USE THE LOCATORS.JSON FILE:
       - The element_locators provided contains a JSON structure with ALL element selectors
       - You MUST parse this JSON file at the beginning of your script
       - Create a smart ElementFinder class that uses these locators
       - DO NOT hardcode any element selectors - exclusively use the locators from this file
       
    2. EXACT STEP EXECUTION:
       - Your code must follow EACH test step with precision
       - For each UI element in the steps, use the corresponding locator from the JSON file
       - Include explicit verification for each expected result
       
    3. DYNAMIC APPLICATION NAVIGATION:
       - Carefully analyze each test step to identify navigation requirements
       - Extract navigation targets (menus, tabs, links) directly from the test steps
       - Follow the navigation flow as specified in the test steps
       - Ensure proper sequencing of navigation actions based on the test case description
       - Allow sufficient waiting time after each navigation action (at least 10 seconds)
       
    4. ROBUST ERROR HANDLING:
       - Implement explicit waits for all elements
       - Add detailed error messages for each step
       - Take screenshots at critical points
       - Enable test run continuation across dependencies
       
    5. LOCATORS.JSON STRUCTURE USAGE:
       - The JSON file is organized by sections (login, navigation, product_search, etc.)
       - Each section contains elements with multiple locator strategies (xpath, id, css, etc.)
       - Your code should try each strategy in order until one succeeds
       - If needed, implement fallback mechanisms when primary locators fail

    **TEST INFORMATION:**
    - Test ID: {test_id}
    - Test Summary: {test_summary}
    **TEST STEPS:**
    {steps_text}

    **ELEMENT LOCATORS (JSON):**
    ```
    {element_locators}
    ```

    **IMPLEMENTATION REQUIREMENTS:**
    - Chrome Driver Path: {chrome_driver_path_fixed}
    - Username: {os.getenv("OPENCRX_USERNAME")}
    - Password: {os.getenv("OPENCRX_PASSWORD")}
    - You MUST load and parse the element_locators JSON at runtime
    - Create a robust element finder class that uses multiple locator strategies
    - Element locators should be accessed by section and element name (e.g., "login.username_input")
    - Test QA-396 MUST follow the test case steps EXACTLY as specified

    **CODE OUTPUT FORMAT:**
    ```python
    # Full, production-quality Python code that uses the locators.json file
    # DO NOT OMIT ANY PARTS OF THE CODE
    ```

    Review your code carefully to ensure you're using the locators.json file correctly for all element interactions.
    """

def build_dependency_prompt(login_test, search_test, chrome_driver_path, element_locators):
    """Create a prompt for generating code that handles dependencies between tests with dynamic adaptation"""
    
    # Fix Chrome driver path - convert backslashes to forward slashes
    chrome_driver_path_fixed = chrome_driver_path.replace('\\', '/')
    
    login_test_id = login_test.get("issue_key") or login_test.get("testId") or login_test.get("test_id", "")
    login_summary = login_test.get("summary", "Login Test")
    login_steps = extract_test_steps(login_test)
    
    search_test_id = search_test.get("issue_key") or search_test.get("testId") or search_test.get("test_id", "")
    search_summary = search_test.get("summary", "Product Search Test")
    search_steps = extract_test_steps(search_test)
    
    # Create a code snippet for the Chrome driver path - using hardcoded string to avoid f-string issues
    chrome_driver_setup = """
#  IMPORTANT - Use Service class for WebDriver initialization:
from selenium.webdriver.chrome.service import Service

# DO NOT initialize WebDriver directly with the path:
# driver = webdriver.Chrome(r\"""" + chrome_driver_path + """\")  # THIS WILL FAIL

# ALWAYS initialize with Service class:
driver = webdriver.Chrome(service=Service(r\"""" + chrome_driver_path + """\"))
"""

    # Create a code snippet for loading the locators file with the correct name
    locators_loading = """
# IMPORTANT - Load locators from the correct file name: 'locators.json'
# NOT 'element_locators.json' or any other variation
try:
    with open('locators.json') as f:
        locators = json.load(f)
    print("Successfully loaded locators from locators.json")
except FileNotFoundError:
    print("ERROR: locators.json file not found!")
    raise
"""
    
    return f"""
    You are a world-class Selenium test automation engineer with extraordinary skills in web UI automation. 
    
    YOUR TASK:
    Create a Selenium script that handles test dependencies by combining two test cases:
    
    1. FIRST_TEST: {login_test_id} - {login_summary}
    2. SECOND_TEST: {search_test_id} - {search_summary}
    
    The second test DEPENDS on the first test. This means:
    - First the `FIRST_TEST` is run and then continue `SECOND_TEST`
    - Keep the browser session open between tests
    - Run tests in sequence within the same browser session
    
    CRITICAL CHROME DRIVER INSTRUCTIONS:
    - Use EXACTLY the following Chrome driver path: {chrome_driver_path_fixed}
    - Do NOT modify this path or try to make it "cleaner" or "better"
    - Include the exact code snippet below in your script:
    ```python
{chrome_driver_setup}
    ```

    CRITICAL LOCATORS FILE INSTRUCTIONS:
    - The locators file is named 'locators.json' (NOT 'element_locators.json')
    - Use EXACTLY this code to load the locators:
    ```python
{locators_loading}
    ```
    
    KEY PRINCIPLES FOR IMPLEMENTATION:
    
    1. INTELLIGENT TEST CASE ANALYSIS:
       - Begin by carefully analyzing each test step's text and expected results
       - Extract key UI navigation patterns from the test steps
       - Identify specific UI elements mentioned in each step
       - Determine the correct sequence of interactions based on step descriptions
       - Adapt your implementation to match the exact workflow described in the test cases
       - Extract navigation targets (menus, tabs, links) from the test steps themselves
       
    2. PARSE AND USE THE LOCATORS.JSON FILE:
       - The locators file is named 'locators.json' (NOT 'element_locators.json')
       - Parse this JSON file at the beginning of your script
       - Create a smart ElementFinder class that uses these locators
       - ONLY use locators from this file - no hardcoded selectors
       - Extract and use both locator_type and value fields from each element definition
       
    3. EXTREME PATIENCE WITH UI INTERACTIONS:
       - OpenCRX is SIGNIFICANTLY SLOWER than typical web applications
       - Add time.sleep(10) after EVERY significant interaction
       - Use WebDriverWait with very long timeouts (30+ seconds)
       - Use EC.element_to_be_clickable() instead of just presence checks
       - Implement scrolling to elements before interaction
       
    4. ROBUST ERROR HANDLING:
       - Implement multiple fallback strategies for finding elements
       - Use JavaScript execution as a fallback for stubborn elements
       - Add detailed error messages and debug logging
       - Take screenshots at critical points and on failures
       
    5. PRECISE TEST STEP EXECUTION:
       - Follow EACH test step in the exact sequence specified
       - Do not skip steps or make assumptions about application state
       - Verify expected results after each action
       - Adapt to unique navigation patterns in each test case
       - Use the test step descriptions to guide your implementation
    
    **FIRST TEST STEPS:**
    {login_steps}
    
    **SECOND TEST STEPS:**
    {search_steps}
    
    **TECHNICAL SPECIFICATIONS:**
    - Initialize WebDriver with: `webdriver.Chrome(service=Service(executable_path=CHROME_DRIVER_PATH))`
    - Wait 10 seconds for page loads and 10 seconds between test steps
    - Base URL for the application is `http://localhost:8080/opencrx-core-CRX`
    - Locators file name: 'locators.json' (NOT 'element_locators.json')
    
    **ELEMENT LOCATORS:**
    ```
    {element_locators}
    ```
    
    **ADDITIONAL INPUT:**
    OPENCRX_USERNAME: ```{os.getenv("OPENCRX_USERNAME")}```
    OPENCRX_PASSWORD: ```{os.getenv("OPENCRX_PASSWORD")}```
    
    CRITICAL CHECKPOINT BEFORE SUBMITTING YOUR CODE:
    - Double-check that you're loading 'locators.json' (not 'element_locators.json')
    - Ensure Chrome is initialized with the Service class
    - Verify your ElementFinder is properly extracting locator_type and value
    
    Provide the output in following JSON format:
    **OUTPUT JSON FORMAT:**
    {{
        'ui_automation_code': '<Complete Python code that handles both test cases in sequence>'
    }}
    """

def generate_selenium_code(prompt):
    """Call OpenAI API to generate code"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            log_error("OPENAI_API_KEY environment variable not set")
            return ""
            
        openai_client = OpenAI(api_key=api_key)
        
        messages=[
            {"role": "system", "content": "You are an expert Selenium test automation developer for OpenCRX."},
            {"role": "user", "content": prompt}
        ]
        

        completion = openai_client.chat.completions.create(
            model="gpt-4", 
            messages=messages,
            temperature=0.1,
            max_tokens=4000
        )
        return completion.choices[0].message.content.strip()
    except Exception as error:
        log_error(f"Error generating code: {error}")
    return ''
    

def save_code(code, test_id):
    """Save generated code to file"""
    output_dir = Path("selenium")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"test_{test_id.lower().replace('-', '_')}.py"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)
    return output_path


def save_dependency_code(code, login_id, search_id):
    """Save dependency test code to file"""
    output_dir = Path("selenium")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"test_{login_id.lower().replace('-', '_')}_to_{search_id.lower().replace('-', '_')}.py"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)
    return output_path


def run_script(script_path):
    """Run the generated test script and display PASS/FAIL"""
    print(f"Running the test: {script_path}")
    result = subprocess.run(['python', script_path], capture_output=True, text=True)
    exit_code = result.returncode

    if int(exit_code) == 0:
        log_status(f"Success: Test passed")
    else:
        log_status(f"Failed: Test had errors")

    # Print out any output from the test
    if result.stdout:
        log_status(f"Test output: ")
        print(result.stdout)

    return exit_code


def extract_code_from_response(response_text):
    """Extract code from OpenAI response, handling different possible formats"""
    # Try parsing as JSON first
    try:
        json_data = json.loads(response_text)
        if isinstance(json_data, dict) and 'ui_automation_code' in json_data:
            return json_data['ui_automation_code']
    except json.JSONDecodeError:
        pass
    
    # Try looking for code blocks
    code_block_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1).strip()
    
    # If response has JSON format strings but isn't valid JSON
    ui_auto_match = re.search(r"'ui_automation_code':\s*'(.*?)'(?=\s*[}\n])", response_text, re.DOTALL)
    if ui_auto_match:
        return ui_auto_match.group(1).strip()
    
    # If all else fails, return the full response
    return response_text


def handle_dependent_tests(login_id, search_id):
    """Handle the creation of a test that combines login and search with dependencies"""
    # Load both test cases
    login_test = load_test_case(login_id)
    search_test = load_test_case(search_id)
    
    if not login_test or not search_test:
        return False
    
    # Get element locators
    chrome_driver_path = os.getenv('CHROME_DRIVER_PATH', 'chromedriver.exe')
    element_locator_path = os.getenv('ELEMENT_LOCATOR_PATH', 'locators.json')
    
    try:
        with open(element_locator_path, 'r', encoding='utf-8') as file:
            element_locators = file.read()
    except FileNotFoundError:
        element_locators = "{}"
        log_error(f"Element locator file not found: {element_locator_path}")
    
    # Generate the integrated test
    print(f"⚙️ Generating integrated test code for {login_id} → {search_id}...")
    prompt = build_dependency_prompt(login_test, search_test, chrome_driver_path, element_locators)
    
    integrated_code = generate_selenium_code(prompt)
    
    try:
        # Extract the code from the response
        final_code = extract_code_from_response(integrated_code)
            
        # Save the code
        script_path = save_dependency_code(final_code, login_id, search_id)
        print(f"✅ Saved integrated test script: {script_path}")
        
        # Run the script
        success = run_script(script_path) == 0
        if success:
            print(f"STATUS: Test chain {login_id} → {search_id} passed")
            return True
        else:
            print(f"STATUS: Test chain {login_id} → {search_id} failed")
            return False
    except Exception as e:
        print(f"❌ Error processing integrated code: {e}")
        return False


def main():
    # Ensure output folder exists
    Path("selenium").mkdir(parents=True, exist_ok=True)

    test_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    # If no test ID is provided, use the latest test case
    if not test_id:
        test_file = find_latest_test_case()
        if not test_file:
            print("❌ No test case file found.")
            return 1
        test_id = test_file.stem
    
    # Load the test case
    test_case = load_test_case(test_id)
    if not test_case:
        print(f"❌ Test case file not found: {test_id}")
        return 1
    
    # Dynamically check for dependencies directly from Jira
    dependency_id = find_test_dependencies(test_id)
    if dependency_id:
        print(f"🔄 Handling test dependency: {dependency_id} → {test_id}")
        
        # Handle the dependent tests
        success = handle_dependent_tests(dependency_id, test_id)
        if success:
            print(f"✅ Successfully executed dependency chain: {dependency_id} → {test_id}")
            return 0
        else:
            print(f"❌ Failed to execute dependency chain: {dependency_id} → {test_id}")
            return 1
    
    # Regular flow for non-dependent tests
    test_summary = test_case.get("summary", "Unnamed Test")
    steps_text = extract_test_steps(test_case)
    
    # Get element locators
    chrome_driver_path = os.getenv('CHROME_DRIVER_PATH', 'chromedriver.exe')
    element_locator_path = 'locators.json'
    
    try:
        with open(element_locator_path, 'r') as file:
            element_locators = json.load(file)
    except FileNotFoundError:
        element_locators = "{}"
        log_error(f"Element locator file not found: {element_locator_path}")
    
    # Generate the test script
    print(f"⚙️ Generating Selenium code for {test_id}...")
    prompt = build_prompt(test_id, test_summary, steps_text, chrome_driver_path, element_locators)
    
    code = generate_selenium_code(prompt)
    
    try:
        # Extract the code from the response
        final_code = extract_code_from_response(code)
            
        # Save the code
        script_path = save_code(final_code, test_id)
        print(f"✅ Saved Selenium script: {script_path}")
        
        # Run the script
        success = run_script(script_path) == 0
        if success:
            print(f"STATUS: Test {test_id} passed")
        else:
            print(f"STATUS: Test {test_id} failed")
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Error processing generated code: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())