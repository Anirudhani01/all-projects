import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import time
import re

from src.manager.file_manager import FileManager
from src.story_parser.list_story_parser import UserStoryParser
from src.openai.prompt.prompt_builder import PromptBuilder
from src.configuration.config import Constant
from src.openai.openai_constants import OpenAIConstants
from src.logger.logger import AppLogger
from list_upload import JiraTestCaseProcessor
from database.db import update_job_status_in_db


class OpenAITestCaseGenerator:
    def __init__(self, userStories, unique_id):
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), "test_case_generator.env"))
        self.api_key = str(os.getenv("OPENAI_API_KEY"))
        self.agent = os.getenv("AGENT3")

        self.testCases = []
        self.userStories = userStories
        self.unique_id = unique_id
        self.model_architecture = OpenAIConstants.get_model(agent=self.agent)
        self._openai_client = OpenAI(api_key=self.api_key)
        self.logger = AppLogger("TestCaseGenerator").get_logger()
        AppLogger("TestCaseGenerator").log_status(
            f"Initialized with agent: {self.agent}"
        )
        self.logger.info(
            f"Model configuration: {json.dumps(self.model_architecture, indent=2)}"
        )
        self.run()

    def __get_llm_response(self, prompt: dict, model_architecture: dict) -> str:
        """
        Send API request to OpenAI to generate get response for a prompt

        Args:
            prompt (str): prompt
            model_architecture (dict): model_architecture

        Returns:
            str: Response
        """
        try:
            if model_architecture["model"] in [
                OpenAIConstants.O1_CONFIG["model"],
                OpenAIConstants.O1_MINI_CONFIG["model"],
                OpenAIConstants.O3_MINI_CONFIG["model"],
                OpenAIConstants.O4_MINI_CONFIG["model"],
            ]:
                prompt[1]["content"] = (
                    prompt[0]["content"] + f"\n" + prompt[1]["content"]
                )
                prompt = [prompt[1]]
                completion = self._openai_client.chat.completions.create(
                    model=model_architecture["model"],
                    messages=prompt,
                    reasoning_effort=model_architecture["reasoning_effort"],
                    n=1,
                    timeout=model_architecture["timeout"],
                )
            else:
                # print(prompt)
                completion = self._openai_client.chat.completions.create(
                    model=model_architecture["model"],
                    messages=prompt,
                    max_tokens=model_architecture["max_tokens"],
                    n=1,
                    temperature=0.1,
                    response_format={"type": "json_object"},
                    timeout=model_architecture["timeout"],
                )
            return completion.choices[0].message.content.replace("\n", "").strip()
        except Exception as e:
            self.logger.error(f"Error -> __get_llm_response: {e}")
            return None

    def process_user_story_file(self, userStory) -> None:
        """For a user story, identifies test case types and generates test cases for each."""
        self.logger.info(f"Processing User Story ..........")
        try:
            parser = UserStoryParser(userStory)
            parser.load_data()
        except Exception as e:
            self.logger.error(f"Failed to parse user story JSON -> {e}")
            return

        prompt_builder = PromptBuilder(parser)

        # test_cases_types = ['Positive Test scenario']
        test_cases_types = [
            "Positive Test scenario",
            "Negative Test scenario",
            "Boundary Value / Edge Test scenario",
            # "User Acceptance Test scenario",
            # "Integration Test scenario",
            # "Usability Test scenario",
            # "Security Test scenario",
            # "Performance Test scenario",
            # "Database Test scenario",
        ]

        existing_test = []
        all_test_cases = {}

        for test_case_type in test_cases_types:
            AppLogger(__name__).log_status(
                f"Generating the test case for {test_case_type}"
            )
            tries = int(os.getenv("ATTEMPTS"))
            count = 0
            while tries > 0:
                self.logger.info(f"Generating test cases for type: {test_case_type}")
                existing_test_str = ",".join(existing_test)
                messages = prompt_builder.get_test_case_generation_flow_prompt(
                    existing_testcases=existing_test_str, test_case_type=test_case_type
                )
                response = self.__get_llm_response(
                    messages, self.model_architecture["user_story_llm"]
                )
                if not response:
                    self.logger.warning(
                        f"No response from OpenAI for test case type -> {test_case_type}"
                    )
                    continue
                try:
                    test_cases = json.loads(response)
                    # print("Printing Test Cases after Parsing in JSON Format")
                    # print(test_cases)
                    existing_test.append(test_case_type)
                    all_test_cases[test_case_type] = test_cases
                    count = len(test_cases["test_cases"])
                    break
                except Exception:
                    self.logger.warning(
                        f"Could not parse response as JSON for {test_case_type}"
                    )
                    tries -= 1
                    count = 0
                time.sleep(5)
            AppLogger(__name__).log_status(f"Generated test cases {count}")
            output_content = {
                "user_story": parser.get_user_story(),
                "test_cases_by_type": all_test_cases,
            }
            test_upload = JiraTestCaseProcessor([output_content])
            test_upload.run()
            all_test_cases = {}

            AppLogger(__name__).log_status(
                f"Pushing {test_case_type} test cases to jira"
            )

        print("The process ended")
        update_job_status_in_db(job_id=self.unique_id, status="completed")

    def run(self):
        self.logger.info(f"Found {len(self.userStories)} user story files.")

        for userStory in self.userStories:
            self.process_user_story_file(userStory)
