import json
import logging
from components.test_case_generator.prompts import PromptsDesign  # Import the prompts file
from langchain_openai import ChatOpenAI
from components.test_case_generator.utils import safe_json_parse


class TestCaseGenerator:
    """
    A class to generate test cases based on flows, business context, context knowledge, and platform using AI prompts.
    """

    def __init__(self, flow, business_context, context_knowledge, platform, api_key, model_name="gpt-4.1", logger=None):
        """
        Initializes the TestCaseGenerator with flow, business context, context knowledge, platform, and OpenAI API key.

        Args:
            flow (dict): The flow containing flow name, paths, and additional information.
            business_context (dict): Additional business context describing objectives, scope, actors, etc.
            context_knowledge (str): Context knowledge retrieved from Adaptive RAG (retrieved chunks).
            platform (str): The platform for which test cases are being generated (e.g., "web" or "mobile").
            api_key (str): OpenAI API key for generating test cases.
            model_name (str): The name of the OpenAI model to use.
            logger (logging.Logger): Logger instance for logging. If None, a default logger is used.
        """
        self.flow = flow
        self.business_context = business_context
        self.context_knowledge = context_knowledge
        self.platform = platform  # Store the platform (e.g., "web" or "mobile")
        self.model_name = model_name
        self.api_key = api_key  # Set the OpenAI API key
        self.chat_model = ChatOpenAI(openai_api_key=self.api_key, model=self.model_name)
        self.logger = logger or logging.getLogger(__name__)  # Use the passed logger or create a default logger

    def format_prompt_for_test_case_type(self, test_case_type, existing_descriptions=None):
        """
        Formats the prompt for generating test cases based on a specific test case type and platform.
        Includes existing descriptions to avoid duplicates.

        Args:
            test_case_type (str): The specific test case type for which test cases will be generated.
            existing_descriptions (list[str]): A list of existing test case descriptions to avoid duplication.

        Returns:
            list[dict]: The formatted prompt messages.
        """
        try:
            # Convert the flow, business context, and existing descriptions to formatted strings
            flow_str = json.dumps(self.flow, indent=4, ensure_ascii=False)
            business_context_str = json.dumps(self.business_context, indent=4, ensure_ascii=False)
            existing_descriptions_str = json.dumps(existing_descriptions or [], indent=4, ensure_ascii=False)

            # Format the prompt by replacing placeholders in the TEST_CASE_GENERATION_USER_PROMPT
            prompt = PromptsDesign.TEST_CASE_GENERATION_USER_PROMPT.value.replace("<--flow-->", flow_str)
            prompt = prompt.replace("<--context_knowledge-->", self.context_knowledge)
            prompt = prompt.replace("<--business_context-->", business_context_str)
            prompt = prompt.replace("<--test_case_type-->", test_case_type)
            prompt = prompt.replace("<--existing_test_case_descriptions-->", existing_descriptions_str)
            prompt = prompt.replace("<--platform-->", self.platform)  # Replace the platform placeholder

            self.logger.debug(f"Prompt formatted for test case type '{test_case_type}' and platform '{self.platform}'.")

            # Return the formatted messages for the AI model
            return [
                {'role': 'system', 'content': PromptsDesign.TEST_CASE_GENERATION_SYSTEM_PROMPT.value},
                {'role': 'user', 'content': prompt}
            ]
        except Exception as e:
            self.logger.error(f"Error formatting prompt for test case type '{test_case_type}' and platform '{self.platform}': {e}")
            raise

    def generate_test_cases_for_type(self, test_case_type, existing_descriptions=None):
        """
        Generates test cases for a specific test case type using the formatted prompt.

        Args:
            test_case_type (str): The specific test case type for which test cases will be generated.
            existing_descriptions (list[str]): A list of existing test case descriptions to avoid duplication.

        Returns:
            list[dict]: Generated test cases in the specified JSON format.
        """
        try:
            self.logger.info(f"Generating test cases for type: {test_case_type} on platform: {self.platform}")
            # Format the prompt for the specific test case type and platform
            prompt = self.format_prompt_for_test_case_type(test_case_type, existing_descriptions)

            # Call OpenAI's GPT model with the prompt
            response = self.chat_model.invoke(prompt)

            # Parse the response from the AI
            generated_test_cases = safe_json_parse(response.content.strip())
            test_cases = generated_test_cases.get("test_cases", [])
            self.logger.info(f"Test cases generated for type '{test_case_type}' on platform '{self.platform}' successfully.")
            return test_cases

        except Exception as e:
            self.logger.error(f"Error generating test cases for type '{test_case_type}' on platform '{self.platform}': {e}")
            return []