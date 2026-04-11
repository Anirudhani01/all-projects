import json
import os
import logging
import openai
import sys
class AppiumScriptGenerator:
    """
    A class to handle the generation of Appium automation scripts using OpenAI's API.
    """
    def __init__(self, api_key, documentation_file, testcase_file, locators_file, output_folder):
        self.api_key = api_key
        self.documentation_file = documentation_file
        self.testcase_file = testcase_file
        self.locators_file = locators_file
        self.output_folder = output_folder

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("script_generator.log", encoding="utf-8")
            ]
        )

        # Ensure the output folder exists
        os.makedirs(self.output_folder, exist_ok=True)

    def read_file(self, file_path):
        """
        Utility function to read a file and handle errors gracefully.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                logging.info(f"Successfully read file: {file_path}")
                return file.read() if file_path.endswith(".txt") else json.load(file)
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from file: {file_path}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error reading file {file_path}: {e}")
            raise

    def generate_script(self, base_code_documentation, test_case, locators):
        """
        Generate the Appium automation script for a specific test case using OpenAI's API.
        """
        logging.info(f"Generating script for test case ID: {test_case['test_case_id']}")
        try:
            # Initialize the OpenAI API client
            openai.api_key = self.api_key

            # Construct the prompt
            prompt = f"""
            You are an AI assistant that generates robust, production-ready Python scripts for Appium automation to test the Airtel Thanks app.

            ### Inputs:
            1. **Base Code Documentation**: Includes Appium driver initialization, shared configurations, and locator loading logic from helper.py.
            {base_code_documentation}
            2. **Test Case Requirements** (JSON defining workflows such as recharge, bill payment, rewards redemption):
            {json.dumps(test_case, indent=4)}
            3. **Locators**: Provide app element locators structured as a JSON object. Ensure the locators include all relevant screens and elements needed for the test case.
               {json.dumps(locators, indent=4)}

            ### Task:
            Generate a Python script that:
            1. Automates the test case end-to-end using Appium, importing all necessary functions and the `LOCATORS` variable from helper via:
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
                - **Always use the exact `screen_name` and `element_name` and `unique_identifier` strings exactly as they appear in `locators.json`** — check the **Locator** object keys for correct spelling, case, and underscores.
                - Do not rename, pluralize, abbreviate, or alter these names in any way.
                - Pass these exact names directly to `get_locator()` to avoid `KeyError`.
                - The `get_locator` function already handles:
                    - Checking whether LOCATORS is a list, dict, or JSON-like object.
                    - Verifying that the given screen name exists.
                    - Finding the element by exact name inside the screen’s `elements` list.
                    - Returning the locator dictionary in the correct format for `find_element_with_fallback()`.
                    - Raising/logging errors if not found.
                - Example in scripts:
                    locator_dict = get_locator("screen_name for that page from **Locator**", "element_name value from **Locator**")
                    find_element_with_fallback(driver, locator_dict, "Mobile Number Input")
                - This ensures scripts remain consistent with the **Locator** and resilient to changes.
            8.accordions expansion check:
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
            - OTP Flow: After entering mobile number, do not click “Get OTP” (app auto-triggers it). Wait for `home_page_after_login` using `wait_for_screen_transition()` and validate the home screen; avoid manual OTP entry.
            - When interacting with expandable elements, confirm success by waiting for the intended child/next element instead of re-clicking.
            - Use only necessary imports.

            ### Best Practices:
            - Use `send_keys()` for text input.
            - Do not re-implement helper functions; use as provided.
            - Handle minor UI text changes without breaking.

            ### Deliverables:
            - Output ONLY the Python script as a single runnable `.py` file.
            - The script must import and use `get_locator()` from `helper` with the exact names from the **Locator** object.
            - Include inline comments explaining key logic.
            - No extra notes or markdown in the output.
            """

            # Call the OpenAI API
            client=openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a coding assistant that generates Python scripts for Appium automation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=30000,
                temperature=0.3
            )

            # Extract the generated code from the response
            generated_code =  response.choices[0].message.content.strip().replace("```python", "").replace("```", "")

            # Save the generated code to a file
            output_file = os.path.join(self.output_folder, f"{test_case['test_case_id']}.py")
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(generated_code)
            logging.info(f"Generated script saved to {output_file}")

        except Exception as e:
            logging.error(f"Error during OpenAI API call for test case ID {test_case['test_case_id']}: {e}")
            raise

    def process_test_cases(self):
        """
        Read input files, generate scripts for each test case, and save outputs.
        """
        # Read the input files
        base_code_documentation = self.read_file(self.documentation_file)
        test_cases = self.read_file(self.testcase_file)
        locators = self.read_file(self.locators_file)

        # Loop through each test case and generate scripts
        for test_case in test_cases:
            self.generate_script(base_code_documentation, test_case, locators)


def main(api_key, documentation_file, testcase_file, locators_file, output_folder):
    """
    Main function to run the script generator.
    """
    # Initialize the script generator
    generator = AppiumScriptGenerator(
        api_key=api_key,
        documentation_file=documentation_file,
        testcase_file=testcase_file,
        locators_file=locators_file,
        output_folder=output_folder
    )

    # Process the test cases and generate the scripts
    generator.process_test_cases()


if __name__ == "__main__":
    # Example arguments
    API_KEY = os.getenv("OPENAI_API_KEY", "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")
    DOCUMENTATION_FILE = "script_documentation.txt"
    TESTCASE_FILE = "test_cases.json"
    LOCATORS_FILE = "locators.json"
    OUTPUT_FOLDER = "output"

    # Run the main function
    main(API_KEY, DOCUMENTATION_FILE, TESTCASE_FILE, LOCATORS_FILE, OUTPUT_FOLDER)