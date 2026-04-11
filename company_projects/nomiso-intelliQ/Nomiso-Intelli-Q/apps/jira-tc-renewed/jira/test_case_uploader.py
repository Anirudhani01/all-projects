import os
import json
from src.logger.logger import AppLogger
from jira.jira_client import JiraClient 
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'test_case_generator.env'))

class TestCaseUploader:
    def __init__(self):
        self.logger = AppLogger(__name__).get_logger()
        self.email = str(os.getenv('EMAIL'))
        self.api_token = str(os.getenv('JIRA_API'))
        self.domain = str(os.getenv('JIRA_DOMAIN'))
        self.test_cases_dir = str(os.getenv('OUTPUT_DIR'))
        self.project_key = str(os.getenv('JIRA_STORY_PROJECT'))
        self.jira_client = JiraClient(self.email, self.api_token, self.domain)
        self.logger.info(f"Initialized TestCaseUploader for directory: {self.test_cases_dir}")
        self.upload_all_test_cases()

    def upload_all_test_cases(self):
        for filename in os.listdir(self.test_cases_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.test_cases_dir, filename)
                try:
                    with open(file_path, 'r') as file:
                        test_case_data = json.load(file)
                        self._process_and_upload(test_case_data)
                except Exception as e:
                    self.logger.error(f"Failed to process file {filename}: {e}", exc_info=True)

    def _process_and_upload(self, data):
        user_story_id = data.get("user_story", {}).get("id")
        test_cases_by_type = data.get("test_cases_by_type", {})

        for case_type, case_data in test_cases_by_type.items():
            for case in case_data.get("test_cases", []):
                summary = f"{data['user_story']['title']} - {case['test_case_description']}"
                description = data['user_story']['story']
                steps = [
                    {"step": step["test_step"], "expectedResult": step["expected_output"]}
                    for step in case["test_steps"]
                ]

                self.logger.info(f"Uploading test case: {summary}")
                test_case_key = self.jira_client.create_test_case(self.project_key, summary, description, steps)
                if test_case_key:
                    self.jira_client.link_test_case_to_story(test_case_key, user_story_id)

# Example usage
# if __name__ == "__main__":
#     email = str(os.getenv('EMAIL'))
#     api_token = str(os.getenv('JIRA_API'))
#     domain = str(os.getenv('JIRA_DOMAIN'))
#     test_cases_dir = str(os.getenv('OUTPUT_DIR'))
#     project_key = str(os.getenv('JIRA_STORY_PROJECT'))

#     uploader = TestCaseUploader(email, api_token, domain, test_cases_dir, project_key)
#     uploader.upload_all_test_cases()
