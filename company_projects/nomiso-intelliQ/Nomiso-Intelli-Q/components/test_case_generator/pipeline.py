import json
import logging
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from components.test_case_generator.worker_functions import generate_test_cases_for_flow, detect_duplicates_with_llm

# Load environment variables from the .env file
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(env_path)

# Configure logging
log_file = os.getenv("LOG_FILE", "pipeline.log")  # Path to the log file from the environment
logging.basicConfig(
    level=logging.INFO,  # Default logging level
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger("TestCasePipeline")  # Create a named logger for the pipeline


class TestCasePipeline:
    """
    Pipeline for generating test cases by integrating AdaptiveRAG for chunk retrieval and TestCaseGenerator.
    """
    def __init__(self, document_path, api_key, logger=None):
        """
        Initializes the pipeline.

        Args:
            document_path (str): Path to the input JSON file containing flows and additional context.
            api_key (str): OpenAI API key for RAG and test case generation.
            logger (logging.Logger): Logger instance for logging. If None, a default logger is used.
        """
        self.document_path = document_path
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__)  # Use the passed logger or create a default logger

    def load_input_file(self):
        """
        Loads the input JSON file and extracts the flows and additional context.

        Returns:
            tuple: A tuple containing:
                - list[dict]: A list of flows.
                - dict: Additional context from the input file.
        """
        try:
            self.logger.info(f"Loading input file from {self.document_path}")
            with open(self.document_path, 'r') as file:
                data = json.load(file)
                flows = data.get("flows", [])
                business_context = {
                    "business_objective": data.get("business_objective", {}),
                    "scope": data.get("scope", {}),
                    "actors_permissions": data.get("actors_permissions", {}),
                    "assumptions": data.get("assumptions", []),
                    "dependencies": data.get("dependencies", []),
                    "constraints": data.get("constraints", []),
                    "non_functional_requirements": data.get("non_functional_requirements", [])
                }
                return flows, business_context
        except Exception as e:
            self.logger.error(f"Error loading input file: {e}")
            return [], {}

    def generate_test_cases(self, flows, business_context, platform="web"):
        """
        Generates test cases for all flows using parallel processing.

        Args:
            flows (list[dict]): List of flows.
            business_context (dict): Business context.
            platform (str): Platform for test cases.

        Returns:
            list[dict]: Generated test cases with sequential IDs.
        """
        total_flows = len(flows)
        self.logger.info(f"Total flows to process: {total_flows} for platform: {platform}")

        all_test_cases = []

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust max_workers based on your system's capacity
            future_to_flow = {
                executor.submit(
                    generate_test_cases_for_flow,
                    flow,
                    business_context,
                    platform,
                    flow_index,
                    total_flows,
                    self.api_key,
                    self.logger
                ): flow_index for flow_index, flow in enumerate(flows, start=1)
            }

            # Process completed futures
            for future in as_completed(future_to_flow):
                flow_index = future_to_flow[future]
                try:
                    test_cases = future.result()
                    all_test_cases.extend(test_cases)
                except Exception as e:
                    self.logger.error(f"Error processing flow {flow_index}: {e}")

        # Assign sequential test case IDs
        for idx, test_case in enumerate(all_test_cases, start=1):
            test_case["test_case_id"] = f"{platform}_TC_{idx}"

        return all_test_cases

    def remove_duplicates_and_update_ids(self, test_cases, platform, business_context):
        """
        Removes duplicates from the test cases, updates their IDs, and returns the cleaned list.

        Args:
            test_cases (list[dict]): List of test cases to process.
            platform (str): Platform for test cases (e.g., "web", "mobile").
            business_context (dict): Business context to provide additional information to the LLM.

        Returns:
            list[dict]: Cleaned list of test cases with updated IDs.
        """
        self.logger.info(f"Removing duplicates for platform: {platform}")

        try:
            # Construct a detailed context prompt for the LLM
            context_prompt = (
                "Business Context:\n"
                f"Business Objective: {business_context.get('business_objective', 'N/A')}\n"
                f"Scope: {business_context.get('scope', 'N/A')}\n"
                f"Actors and Permissions: {business_context.get('actors_permissions', 'N/A')}\n"
                f"Assumptions: {', '.join(business_context.get('assumptions', []))}\n"
                f"Dependencies: {', '.join(business_context.get('dependencies', []))}\n"
                f"Constraints: {', '.join(business_context.get('constraints', []))}\n"
                f"Non-Functional Requirements: {', '.join(business_context.get('non_functional_requirements', []))}\n"
            )

            # Make an LLM call to detect duplicates, passing the business context
            duplicate_ids = detect_duplicates_with_llm(test_cases, context_prompt, self.api_key, self.logger)

            # Remove duplicates and keep originals
            cleaned_test_cases = [test_case for test_case in test_cases if test_case["test_case_id"] not in duplicate_ids]

            # Reassign sequential test case IDs
            for idx, test_case in enumerate(cleaned_test_cases, start=1):
                test_case["test_case_id"] = f"{platform}_TC_{idx}"

            self.logger.info(f"Removed {len(duplicate_ids)} duplicate test cases. Remaining test cases: {len(cleaned_test_cases)}")
            return cleaned_test_cases
        except Exception as e:
            self.logger.error(f"Error during duplicate removal: {e}")
            return test_cases

    def save_test_cases_to_file(self, test_cases, output_file_path):
        """
        Saves the generated test cases to a JSON file.

        Args:
            test_cases (list[dict]): List of test cases to save.
            output_file_path (str): Path to save the JSON file.
        """
        try:
            self.logger.info(f"Saving test cases to file: {output_file_path}")
            with open(output_file_path, 'w', encoding='utf-8') as file:
                json.dump(test_cases, file, indent=4, ensure_ascii=False)
            self.logger.info(f"Test cases successfully saved to {output_file_path}")
        except Exception as e:
            self.logger.error(f"Error saving test cases to file: {e}")


# Example usage
if __name__ == "__main__":
    input_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "input_structure.json"))
    output_file_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "generated_test_cases"))

    openai_api_key = os.getenv("OPENAI_API_KEY")
    print(openai_api_key)

    pipeline = TestCasePipeline(document_path=input_file_path, api_key=openai_api_key, logger=logger)

    flows, business_context = pipeline.load_input_file()

    # Generate and clean web test cases
    web_test_cases = pipeline.generate_test_cases(flows, business_context, platform="web")
    cleaned_web_test_cases = pipeline.remove_duplicates_and_update_ids(web_test_cases, platform="web", business_context=business_context)
    pipeline.save_test_cases_to_file(cleaned_web_test_cases, f"{output_file_base}_web.json")

    # # Generate and clean mobile test cases
    # mobile_test_cases = pipeline.generate_test_cases(flows, business_context, platform="mobile")
    # cleaned_mobile_test_cases = pipeline.remove_duplicates_and_update_ids(mobile_test_cases, platform="mobile", business_context=business_context)
    # pipeline.save_test_cases_to_file(cleaned_mobile_test_cases, f"{output_file_base}_mobile.json")