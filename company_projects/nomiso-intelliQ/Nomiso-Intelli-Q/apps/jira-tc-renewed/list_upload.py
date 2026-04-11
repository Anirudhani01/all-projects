import os
from dotenv import load_dotenv

from jira.jira_list_upload import TestCaseImporter
from src.logger.logger import AppLogger
from jira.jira_client import JiraClient

class JiraTestCaseProcessor:
    def __init__(self, nested_test_case_json):
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'test_case_generator.env'))
        self.logger = AppLogger("jira_test_case_processor").get_logger()
        self.email = os.getenv("EMAIL")
        self.api_token = os.getenv("JIRA_API")
        self.domain = os.getenv("JIRA_DOMAIN")
        self.project_key = os.getenv("JIRA_STORY_PROJECT")
        self.qa_project_key = os.getenv("JIRA_QA_PROJECT")
        self.test_cases_data = nested_test_case_json

        self.jira_client = JiraClient(self.email, self.api_token, self.domain)
        self.importer = TestCaseImporter(self.jira_client, self.project_key, self.qa_project_key)

    def run(self):
        self.logger.info("Processing test cases from nested list...")
        created_count = self.importer.process_nested_test_cases(self.test_cases_data)
        self.logger.info(f"Test case upload completed. Total created: {created_count}")
