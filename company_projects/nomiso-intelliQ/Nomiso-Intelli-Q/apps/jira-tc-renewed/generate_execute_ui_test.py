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
import time
import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from requests.auth import HTTPBasicAuth
from src.logger.logger import AppLogger
import ast

from src.openai.openai_constants import OpenAIConstants

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'test_case_generator.env'))

APP_LOGGER = AppLogger("JiraTestCaseFetcher")

class JiraTestCaseFetcher:
    def __init__(self, domain, email, api_token):
        self.domain = domain
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {
            "Accept": "application/json"
        }
        self.base_url = f"https://{domain}/rest/api/3"
        APP_LOGGER.logger.info("Started Fetching Test cases")

    def get_issue(self, issue_key):
        url = f"{self.base_url}/issue/{issue_key}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def extract_test_steps_from_adf(self, description_adf):
        """
        Extracts test steps from the Atlassian Document Format (ADF) table in the description field.
        Returns a list of dicts with step_number, test_step, expected_output.
        """
        test_steps = []
        if not description_adf:
            return test_steps

        # The description is a dict with 'content' key
        content = description_adf.get('content', [])
        for block in content:
            if block.get('type') == 'table':
                # Found the table block
                rows = block.get('content', [])
                # Skip header row (first row)
                for row in rows[1:]:
                    cells = row.get('content', [])
                    if len(cells) >= 3:
                        step_number = self.extract_text_from_adf(cells[0])
                        test_step = self.extract_text_from_adf(cells[1])
                        expected_output = self.extract_text_from_adf(cells[2])
                        test_steps.append({
                            "step_number": step_number,
                            "test_step": test_step,
                            "expected_output": expected_output
                        })
                break
        APP_LOGGER.log_status("Fetched the test steps")
        return test_steps

    def extract_text_from_adf(self, cell):
        """
        Extract text from an ADF table cell, which contains paragraphs and text nodes.
        """
        texts = []
        for paragraph in cell.get('content', []):
            if paragraph.get('type') == 'paragraph':
                for text_node in paragraph.get('content', []):
                    if text_node.get('type') == 'text':
                        texts.append(text_node.get('text', ''))
        return ' '.join(texts).strip()

    def save_test_case(self, issue_key, summary, description, test_steps):
        """
        Save the test case details in a JSON file inside test_cases directory.
        """
        os.makedirs('test_cases', exist_ok=True)
        filename = os.path.join('test_cases', f"{issue_key}.json")
        data = {
            "issue_key": issue_key,
            "summary": summary,
            "description": description,
            "test_steps": test_steps
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        APP_LOGGER.logger.info("Saving the test cases in json")

    def extract_plain_text_from_adf(self, description_adf):
        """
        Extract plain text from ADF description ignoring tables.
        """
        texts = []
        for block in description_adf.get('content', []):
            if block.get('type') == 'paragraph':
                for text_node in block.get('content', []):
                    if text_node.get('type') == 'text':
                        texts.append(text_node.get('text', ''))
        return '\n'.join(texts).strip()

    def fetch_and_save_test_case(self, issue_key):
        issue = self.get_issue(issue_key)
        fields = issue.get('fields', {})
        summary = fields.get('summary', '')
        description = fields.get('description', {})

        # description may be a dict (ADF) or string, handle both
        if isinstance(description, dict):
            test_steps = self.extract_test_steps_from_adf(description)
            # For human-readable description text, extract paragraphs excluding the table
            desc_text = self.extract_plain_text_from_adf(description)
        else:
            test_steps = []
            desc_text = description if description else ""

        self.save_test_case(issue_key, summary, desc_text, test_steps)


# Enhanced Jira Integration
class JiraClient:
    def __init__(self):
        self.domain = os.getenv("JIRA_DOMAIN")  # Fix typo in environment variable name
        self.email = os.getenv("EMAIL") 
        self.api_token = os.getenv("JIRA_API")
        
        if not all([self.domain, self.email, self.api_token]):
            APP_LOGGER.logger.info("Jira credentials not fully configured in environment variables")
            APP_LOGGER.logger.error(f"Domain: {self.domain}, Email: {self.email}, Token: {'Present' if self.api_token else 'Missing'}")
            self.enabled = False
        else:
            self.enabled = True
            self.auth = HTTPBasicAuth(self.email, self.api_token)
            self.headers = {"Accept": "application/json"}
            self.base_url = f"https://{self.domain}/rest/api/3"
            APP_LOGGER.logger.info("Jira client initialized successfully")
            APP_LOGGER.logger.info(f"Using Jira domain: {self.domain}")
    
    def get_issue(self, issue_key):
        """Get complete issue details from Jira"""
        if not self.enabled:
            APP_LOGGER.logger.info("Jira client not enabled, skipping API call")
            return None
            
        try:
            url = f"{self.base_url}/issue/{issue_key}?expand=issuelinks"
            APP_LOGGER.logger.info(f"Fetching issue data from {url}")
            response = requests.get(url, headers=self.headers, auth=self.auth)
            response.raise_for_status()
            APP_LOGGER.logger.info(f"Successfully retrieved issue {issue_key}")
            return response.json()
        except Exception as e:
            APP_LOGGER.logger.error(f"Error fetching Jira issue {issue_key}: {str(e)}")
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
            APP_LOGGER.logger.info(f"Found {len(issue_links)} issue links for {issue_key}")
            
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
                        APP_LOGGER.logger.info(f"Found dependency: {issue_key} is {link_direction} {linked_key}")
            
            # Also check for all custom fields
            custom_fields = issue_data.get('fields', {})
            for field_key, field_value in custom_fields.items():
                # Look for fields that might contain dependency information
                if field_value and any(term in field_key.lower() for term in ['depend', 'block', 'link', 'relation']):
                    APP_LOGGER.logger.info(f"Checking custom field {field_key} for dependencies")
                    
                    # Handle different field value types
                    if isinstance(field_value, list):
                        for item in field_value:
                            if isinstance(item, dict) and 'key' in item:
                                links.append({
                                    'type': 'depends on',
                                    'key': item['key'],
                                    'direction': 'blocked by'
                                })
                                APP_LOGGER.logger.info(f"Found dependency in custom field: {issue_key} depends on {item['key']}")
                    elif isinstance(field_value, dict) and 'key' in field_value:
                        links.append({
                            'type': 'depends on',
                            'key': field_value['key'],
                            'direction': 'blocked by'
                        })
                        APP_LOGGER.logger.info(f"Found dependency in custom field: {issue_key} depends on {field_value['key']}")
                    elif isinstance(field_value, str) and re.search(r'[A-Z]+-\d+', field_value):
                        # Extract issue keys from text fields
                        matches = re.findall(r'[A-Z]+-\d+', field_value)
                        for match in matches:
                            links.append({
                                'type': 'depends on',
                                'key': match,
                                'direction': 'blocked by'
                            })
                            APP_LOGGER.logger.info(f"Found dependency in text field: {issue_key} depends on {match}")
                        
            return links
        except Exception as e:
            APP_LOGGER.logger.error(f"Error parsing issue links for {issue_key}: {str(e)}")
            return []
    
    def find_dependencies(self, issue_key):
        """Find all issues that this issue depends on"""
        links = self.get_issue_links(issue_key)
        dependencies = [link['key'] for link in links if link['direction'] == 'blocked by']
        
        if dependencies:
            APP_LOGGER.logger.info(f"Found dependencies for {issue_key}: {dependencies}")
        else:
            APP_LOGGER.logger.warning(f"No dependencies found for {issue_key}")
            
        return dependencies

# Initialize Jira client
jira_client = JiraClient()

def find_latest_test_case():
    """Auto-detect latest test case JSON file"""
    base_dir = Path("test_cases")
    if not base_dir.exists():
        APP_LOGGER.logger.info("test_cases directory not found. Creating it.")
        base_dir.mkdir(parents=True, exist_ok=True)
        return None
        
    for folder in sorted(base_dir.glob("*"), reverse=True):
        if folder.is_dir():
            json_files = sorted(folder.glob("*.json"), reverse=True)
            if json_files:
                APP_LOGGER.logger.info(f"Latest test case found: {json_files[0]}")
                return json_files[0]
                
    # If we didn't find files in subfolders, look for JSON files directly in test_cases
    json_files = sorted(base_dir.glob("*.json"), reverse=True)
    if json_files:
        APP_LOGGER.logger.info(f"Latest test case found: {json_files[0]}")
        return json_files[0]
        
    return None


def find_test_case_by_id(test_id):
    """Locate test case file by ID"""
    base_dir = Path("test_cases")
    if not base_dir.exists():
        APP_LOGGER.logger.info("test_cases directory not found. Creating it.")
        base_dir.mkdir(parents=True, exist_ok=True)
        return None

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
    """Load a test case from JSON file or fetch from Jira if not found"""
    test_file = find_test_case_by_id(test_id)
    if not test_file:
        APP_LOGGER.log_status(f" Test case file for {test_id} not found locally. Fetching from Jira...")
        
        if jira_client.enabled:
            # Create a JiraTestCaseFetcher instance
            fetcher = JiraTestCaseFetcher(
                jira_client.domain, 
                jira_client.email, 
                jira_client.api_token
            )
            
            # Fetch and save the test case
            try:
                fetcher.fetch_and_save_test_case(test_id)
                APP_LOGGER.log_status(f"Successfully fetched {test_id} from Jira")
                # Try to find the file again now that it should be downloaded
                test_file = find_test_case_by_id(test_id)
            except Exception as e:
                APP_LOGGER.logger.error(f"Error fetching {test_id} from Jira: {str(e)}")
                
        if not test_file:
            APP_LOGGER.logger.error(f" Test case file for {test_id} not found locally or in Jira.")
            return None
    
    APP_LOGGER.logger.info(f"Found test case: {test_file}")
    
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
    If dependency is found but not available locally, fetch it from Jira.
    
    Returns:
        String: Dependency test ID if found, None otherwise
    """
    # Get dependencies from Jira
    if jira_client.enabled:
        jira_dependencies = jira_client.find_dependencies(test_id)
        if jira_dependencies:
            APP_LOGGER.logger.info(f"Dependencies found in Jira for {test_id}: {jira_dependencies}")
            
            # For each dependency, check if it exists locally - if not, fetch it
            for dep_id in jira_dependencies:
                dep_file = find_test_case_by_id(dep_id)
                if not dep_file:
                    APP_LOGGER.logger.info(f"Dependency {dep_id} not found locally. Fetching from Jira...")
                    # Create a JiraTestCaseFetcher instance
                    fetcher = JiraTestCaseFetcher(
                        jira_client.domain, 
                        jira_client.email, 
                        jira_client.api_token
                    )
                    # Fetch and save the test case
                    try:
                        fetcher.fetch_and_save_test_case(dep_id)
                        APP_LOGGER.log_status(f"Successfully fetched dependency {dep_id} from Jira")
                    except Exception as e:
                        APP_LOGGER.logger.info(f"Error fetching dependency {dep_id} from Jira: {str(e)}")
            
            return jira_dependencies
            
    APP_LOGGER.logger.info(f"No dependencies found for {test_id} in Jira")
    return None

# def build_dependency_prompt(test_flow_builder, chrome_driver_path, element_locators):
#     """Create a prompt for generating code that handles dependencies between tests with dynamic adaptation"""
    
#     return f"""
#     You are a world-class Selenium test automation engineer with extraordinary skills in web UI automation using Python. 
    
#     **TASK:**
#     You will be given a multiple test scenarios, create a Selenium script that handles given test scenarios:
    
#     **INSTRUCTIONS:**
#     1. STEP-BY-STEP EXECUTION:
#         - Execute each step in the exact order specified
#         - For each step, implement precise element location and interaction
#         - For each step, verify the expected result
#     2. ROBUST ELEMENT LOCATION:
#         - For each UI element mentioned in the steps, implement multiple location strategies
#         - Include smart fallbacks when elements can't be found with primary locators
#         - Use descriptive, semantic locators based on the element's purpose
#     3. COMPLETE ERROR HANDLING:
#         - Add screenshots at each step and on failures
#         - Include detailed logging of each action and result
#         - Implement proper test result verification
#     4. The code MUST handle any OpenCRX workflow described in the steps, not just login. Follow each step precisely, regardless of the flow (could be account creation, data entry, navigation, etc.).
#     5. CREATE COMPLETE, EXECUTABLE PYTHON CODE THAT WORKS ON FIRST RUN.
#     6. Use following chrome driver path: `{chrome_driver_path}` for UI automation test. And use Web driver initialization code: `webdriver.Chrome(service=Service(executable_path=CHROME_DRIVER_PATH))` 
#     7. Wait for 2 seconds for each webpage loading. Wait 2 seconds for each test step.
#     8. Provide the output in following JSON format:
#         **OUTPUT JSON FORMAT:**
#         {{
#             "ui_automation_code": "<Generated UI Automation Code as raw string>"
#         }}

#     **TEST SCENARIOS:**
#     {test_flow_builder}
    
#     **ELEMENT LOCATORS:**
#     ```
#     {element_locators}
#     ```
    
#     **ADDITIONAL INPUT:**
#     OPENCRX_USERNAME: ```{os.getenv("OPENCRX_USERNAME")}```
#     OPENCRX_PASSWORD: ```{os.getenv("OPENCRX_PASSWORD")}```
    

#     Provide the output in following JSON format:
#     **OUTPUT JSON FORMAT:**
#     {{
#         'ui_automation_code': '<Generated UI automation code>'
#     }}
#     """

def build_dependency_prompt(test_flow_builder, chrome_driver_path, element_locators):
    """Create a prompt for generating code that handles dependencies between tests with dynamic adaptation"""
    
    return f"""
    You are a highly skilled Selenium UI automation engineer specialized in creating precise, reliable, and robust Python automation scripts.

    **TASK:**
    Given detailed test scenarios and element locators in structured JSON format, generate a complete Selenium Python automation script that accurately implements each scenario.
    
    **INSTRUCTIONS:**
    1. Thorougly analyze the `TEST SCENARIOS` and `ELEMENT LOCATORS` to understand the test flow.
    2. Generate selenium automation code using Python with exact test flow.
    3. Add screenshots at each step and on failures and verify outcomes explicitly after each action.
    4. Include detailed logging of each action and result
    5. Use following chrome driver path: `{chrome_driver_path}` for UI automation test. And use Web driver initialization code: `webdriver.Chrome(service=Service(executable_path=CHROME_DRIVER_PATH))` 
    6. Wait for 2 seconds for each webpage loading and for each test step.
    7. Provide the output in following JSON format:
    **OUTPUT JSON FORMAT:**
    {{
        "ui_automation_code": "<Generated UI Automation Code as raw string>"
    }}

    **TEST SCENARIOS:**
    ```
    {test_flow_builder}
    ```
    **ELEMENT LOCATORS:**
    ```
    {element_locators}
    ```
    **ADDITIONAL INPUT:**
    OPENCRX_USERNAME: ```{os.getenv("OPENCRX_USERNAME")}```
    OPENCRX_PASSWORD: ```{os.getenv("OPENCRX_PASSWORD")}```

    **OUTPUT:**
    """

def generate_selenium_code(prompt):
    """Call OpenAI API to generate code"""

    try:
        openai_client = OpenAI(api_key = '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')
        agent = os.getenv("AGENT4")
        model_architecture = OpenAIConstants.get_model(agent=agent)
        model_architecture = model_architecture['user_story_llm']
        APP_LOGGER.log_status(f"Model: {model_architecture['model']}")
        if model_architecture['model'] in [OpenAIConstants.O1_CONFIG['model'],
                                            OpenAIConstants.O1_MINI_CONFIG['model'],
                                            OpenAIConstants.O3_MINI_CONFIG['model'],
                                            OpenAIConstants.O4_MINI_CONFIG['model']]:
            messages=[
                {"role": "user", "content": prompt}
            ]
            completion = openai_client.chat.completions.create(
                    model=model_architecture['model'],
                    messages= messages,
                    reasoning_effort=model_architecture['reasoning_effort'],
                    n=1,
                    timeout=model_architecture['timeout'],
                )
        else:
            messages=[
                {"role": "system", "content": "You are an expert Selenium test automation developer for OpenCRX."},
                {"role": "user", "content": prompt}
            ]
            
            completion = openai_client.chat.completions.create(
                    model=model_architecture['model'],
                    messages= messages,
                    max_tokens=model_architecture['max_tokens'],
                    n=1,
                    temperature=0.1,
                    response_format={"type": "json_object"},
                    timeout=model_architecture['timeout']
                )
        return completion.choices[0].message.content.replace('\n', '').strip()
    except Exception as error:
        pass
    return ''
    

def save_code(code, test_id):
    """Save generated code to file"""
    output_dir = Path("selenium")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"test_{test_id.lower().replace('-', '_')}.py"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)
    return output_path

def save_dependency_code(code, test_id):
    """Save dependency test code to file"""
    output_dir = Path("selenium")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"test_{test_id.lower().replace('-', '_')}.py"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)
    return output_path

def run_script(script_path):
    """Run the generated test script and display PASS/FAIL"""
    print(f"Started Test execution: {script_path}")
    result = subprocess.run(['python', script_path], capture_output=True, text=True)
    exit_code = result.returncode

    if int(exit_code) == 0:
        APP_LOGGER.log_status(f"Success: Test passed")
    else:
        APP_LOGGER.log_status(f"Failed: Test had errors")

    # Print out any output from the test
    if result.stdout:
        APP_LOGGER.log_status(f"Test output: ")
        print(result.stdout)

    return exit_code


def extract_code_from_response(response_text):
    """Extract code from OpenAI response, handling different possible formats"""
    # Try parsing as JSON first
    try:
        response_text = response_text.strip('```python').strip('```').strip('```json')
        return ast.literal_eval(response_text)['ui_automation_code']
    except json.JSONDecodeError:
        pass
    return ''


def handle_dependent_tests(test_id, test_flow_builder):
    """Handle the creation of a test that combines login and search with dependencies"""
    chrome_driver_path = os.getenv('CHROME_DRIVER_PATH', 'chromedriver.exe')
    element_locator_path = os.getenv('ELEMENT_LOCATOR_PATH', 'locators.json')
    
    try:
        with open(element_locator_path, 'r', encoding='utf-8') as file:
            element_locators = file.read()
    except FileNotFoundError:
        element_locators = "{}"
        APP_LOGGER.logger.error(f"Element locator file not found: {element_locator_path}")
    
    prompt = build_dependency_prompt(test_flow_builder, chrome_driver_path, element_locators)
    APP_LOGGER.log_status(f" Generating UI Automation Code for the test case: {test_id}")
    integrated_code = generate_selenium_code(prompt)
    try:
        # Extract the code from the response
        final_code = extract_code_from_response(integrated_code)
        # Save the code
        script_path = save_dependency_code(final_code, test_id)

        APP_LOGGER.log_status(f" Saved UI Automation code in: {script_path}")
        
        # Run the script
        success = run_script(script_path) == 0
        if success:
            APP_LOGGER.log_status(f"Test scenario {test_id} passed")
            return True
        else:
            APP_LOGGER.log_status(f"Test scenario {test_id} failed")
            return False
    except Exception as e:
        APP_LOGGER.logger.error(f" Error processing integrated code: {e}")
        return False


def main():
    Path("screenshots").mkdir(parents=True, exist_ok=True)
    
    Path("selenium").mkdir(parents=True, exist_ok=True)
    
    Path("test_cases").mkdir(parents=True, exist_ok=True)

    test_id = sys.argv[1] if len(sys.argv) > 1 else None

    # If no test ID is provided, use the latest test case
    if not test_id:
        test_file = find_latest_test_case()
        if not test_file:
            APP_LOGGER.logger.error(" No test case file found.")
            return 1
        test_id = test_file.stem
    
    # Load the test case with automatic fetching from Jira if needed
    test_case = load_test_case(test_id)
    if not test_case:
        APP_LOGGER.logger.error(f" Test case file for {test_id} could not be found or fetched from Jira.")
        return 1
    
    # Dynamically check for dependencies directly from Jira
    test_flow = find_test_dependencies(test_id)
    test_flow.append(test_id)

    test_flow_builder = ''
    for test_id in test_flow:
        test = load_test_case(test_id)
        test_flow_builder += f'Test ID: {test.get("issue_key") or test.get("testId") or test.get("test_id", "")}\n'
        test_flow_builder += f'Test Summary: {test.get("summary")}\n'
        test_flow_builder += f'Test Steps\n: {extract_test_steps(test)}\n'

    if test_flow_builder:
        # Handle the dependent tests - both will be fetched from Jira if needed
        success = handle_dependent_tests(test_id, test_flow_builder)
        if success:
            APP_LOGGER.log_status(f"Successfully Test Case: {test_id}")
            return 0
        else:
            APP_LOGGER.logger.error(f" Failed to execute Test Case: {test_id}")
            return 1

if __name__ == "__main__":
    sys.exit(main())