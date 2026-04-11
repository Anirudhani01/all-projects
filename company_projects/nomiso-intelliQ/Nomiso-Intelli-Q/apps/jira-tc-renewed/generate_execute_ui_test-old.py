#!/usr/bin/env python3
"""
Pure Prompt Test Converter
Converts test cases to Selenium code using LLM (OpenAI)

Usage:
    python pure_prompt_converter.py QA-239
    or just:
    python pure_prompt_converter.py  # Auto-detect latest
"""

import os
import re
import sys
import json
import openai
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from src.logger.logger import AppLogger
from openai import OpenAI
import ast

from src.openai.openai_constants import OpenAIConstants
from extract import JiraTestCaseFetcher

logger = AppLogger('FunctionalTestCases').get_logger()
logger.info("Found the latest test cases")

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'test_case_generator.env'))
openai.api_key = os.getenv("OPENAI_API_KEY")


def find_latest_test_case():
    """Auto-detect latest test case JSON file"""
    base_dir = Path("test_cases")
    for folder in sorted(base_dir.glob("*"), reverse=True):
        if folder.is_dir():
            json_files = sorted(folder.glob("*.json"), reverse=True)
            if json_files:
                AppLogger(__name__).log_status(f"Latest test case found: {json_files[0]}")
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


def build_prompt(test_id, test_summary, steps_text, chrome_driver_path, element_locators):
    """Create a powerful prompt that ensures complete login functionality testing"""
    return f"""
    You are a world-class Selenium test automation engineer with extraordinary skills in web UI automation. Create flawless Python code for OpenCRX test automation that executes a COMPLETE login process.

    YOUR TASK:
    Create a Selenium script that follows EACH `TEST STEP` EXACTLY as specified:

    1. STEP-BY-STEP EXECUTION:
        - Execute each step in the exact order specified
        - For each step, implement precise element location and interaction
        - For each step, verify the expected result
    2. ROBUST ELEMENT LOCATION:
        - For each UI element mentioned in the steps, implement multiple location strategies
        - Include smart fallbacks when elements can't be found with primary locators
        - Use descriptive, semantic locators based on the element's purpose
    3. COMPLETE ERROR HANDLING:
        - Add screenshots at each step and on failures
        - Include detailed logging of each action and result
        - Implement proper test result verification
    4. The code MUST handle any OpenCRX workflow described in the steps, not just login. Follow each step precisely, regardless of the flow (could be account creation, data entry, navigation, etc.).
    5. CREATE COMPLETE, EXECUTABLE PYTHON CODE THAT WORKS ON FIRST RUN.
    6. Use following chrome driver path: `{chrome_driver_path}` for UI automation test. And use Web driver initialization code: `webdriver.Chrome(service=Service(executable_path=CHROME_DRIVER_PATH))` 
    7. Wait for 10 seconds for each webpage loading. Wait 2 seconds for each test step.
    8. Provide the output in following JSON format:
        **OUTPUT JSON FORMAT:**
        {{
            'ui_automation_code': '<Generated UI Automation Code>'
        }}

    **TEST INFORMATION:**
    - Test ID: {test_id}
    - Test Summary: {test_summary}
    **TEST STEPS:**
    {steps_text}

    **ADDITIONAL INPUT:**
    OPENCRX_USERNAME: ```{os.getenv("OPENCRX_USERNAME")}```
    OPENCRX_PASSWORD: ```{os.getenv("OPENCRX_PASSWORD")}```
    ELEMENT_LOCATORS:
    ```
    {element_locators}
    ```

    Use `ADDITIONAL INPUT` where ever necessary.

    **OUTPUT:**
    """

def generate_selenium_code(prompt):
    """Call OpenAI API to generate code"""

    try:
        openai_client = OpenAI(api_key = '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')
        agent = os.getenv("AGENT3")
        model_architecture = OpenAIConstants.get_model(agent=agent)
        model_architecture = model_architecture['user_story_llm']

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

def run_script(script_path):
    """Run the generated test script and display PASS/FAIL"""
    print("Running the test...")
    result = subprocess.run(['python', script_path], capture_output=True)
    exit_code = result.returncode

    if int(exit_code) == 0:
        AppLogger(__name__).log_status(f"success: ")
    else:
        AppLogger(__name__).log_status(f"failed: ")

    # Print out any output from the test
    if result.stdout:
        AppLogger(__name__).log_status(f"Test: ")
        print(result.stdout.decode('utf-8'))

    return exit_code

def main():

    # Ensure output folder exists
    Path("selenium").mkdir(parents=True, exist_ok=True)

    test_id = sys.argv[1] if len(sys.argv) > 1 else None
    # test_id = 'QA-287'

    DOMAIN = os.getenv('JIRA_DOMAIN')
    EMAIL = os.getenv("EMAIL")
    API_TOKEN = os.getenv("JIRA_API")

    TEST_CASE_ID = test_id

    fetcher = JiraTestCaseFetcher(DOMAIN, EMAIL, API_TOKEN)
    fetcher.fetch_and_save_test_case(TEST_CASE_ID)

    test_file = (
        find_test_case_by_id(test_id) if test_id
        else find_latest_test_case()
    )

    if not test_file:
        print("❌ No test case file found.")
        return 1

    test_id = test_file.stem
    print(f"✅ Found test case: {test_file}")

    with open(test_file, "r", encoding="utf-8") as f:
        test_case = json.load(f)

    test_summary = test_case.get("summary", "Unnamed Test")
    steps_text = extract_test_steps(test_case)

    chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')
    element_locator_path = os.getenv('ELEMENT_LOCATOR_PATH')
    with open(element_locator_path, 'r', encoding='utf-8') as file:
        element_locators = file.read()

    prompt = build_prompt(test_id, test_summary, steps_text, chrome_driver_path, element_locators)

    print("⚙️ Generating Selenium code...")
    try:
        code = generate_selenium_code(prompt)
        code = code.replace('```json', '').strip('```')
        code = ast.literal_eval(code)

        code = code['ui_automation_code']
        
        script_path = save_code(code, test_id)
        print(f"✅ Saved Selenium script: {script_path}")

        return run_script(script_path)

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
