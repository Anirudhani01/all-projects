import requests
from requests.auth import HTTPBasicAuth
import json
from src.logger.logger import AppLogger
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'test_case_generator.env'))

class JiraClient:
    def __init__(self, email, api_token, domain):
        self.logger = AppLogger(__name__).get_logger()
        self.logger.info("Initializing JiraClient...")
        self.project_key = str(os.getenv('JIRA_STORY_PROJECT'))
        self.domain = domain
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://{domain}/rest/api/3"
        self.logger.info(f"Jira API URL base set to {self.base_url}")

    def create_test_case(self, project_key, summary, description, test_steps):
        self.logger.info(f"Creating test case: {summary}")

        payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": "Task"  
                }
            }
        }

        self.logger.info(f"Payload being sent to Jira......\n")

        try:
            url = f"https://{self.domain}/rest/api/3/issue"
            response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)
            response.raise_for_status()
            created_issue = response.json()
            self.logger.info(f"Test Case Created Successfully: {created_issue['key']}")
            return created_issue['key']
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Error creating test case: {err}", exc_info=True)
            self.logger.error(f"Response content: {response.text}")
        return None

    def link_test_case_to_story(self, test_case_key, story_key, link_type="Relates"):
        """
        Links the created test case to a user story.

        Args:
            test_case_key (str): The Jira key of the test case (e.g., TST-1).
            story_key (str): The Jira key of the story (e.g., TST-2).
            link_type (str): The type of link. Default is 'Relates'.
                            Common types: 'Relates', 'Blocks', 'Cloners', 'Duplicate', 'Tests'
        """
        self.logger.info(f"Linking test case {test_case_key} to story {story_key} with link type '{link_type}'")

        payload = {
            "type": {"name": link_type},
            "inwardIssue": {"key": story_key},
            "outwardIssue": {"key": test_case_key},
            "comment": {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Link created from automation between test case {test_case_key} and story {story_key}"
                                }
                            ]
                        }
                    ]
                }
            }
        }

        try:
            url = f"{self.base_url}/issueLink"
            response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)
            if response.status_code != 201:
                self.logger.error(f"Failed to link issues. Status Code: {response.status_code}, Response: {response.text}")
            response.raise_for_status()
            self.logger.info(f"Successfully linked test case {test_case_key} to story {story_key}")
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Error linking test case: {err}", exc_info=True)

    def get_user_story_by_id(self, story_id):
        """Fetches user stories for a given project."""
        if not story_id:
            self.logger.error("No story ID provided or found in environment variables.")
            return None

        self.logger.info(f"Fetching user story with ID: {story_id}")

        try:
            url = f"{self.base_url}/issue/{story_id}"
            response = requests.get(url, headers=self.headers, auth=self.auth)
            response.raise_for_status()
            self.logger.info(f"Successfully fetched story {story_id}")
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"HTTP error occurred while fetching story {story_id}: {http_err}", exc_info=True)
        except requests.exceptions.RequestException as req_err:
            self.logger.error(f"Request error occurred while fetching story {story_id}: {req_err}", exc_info=True)
        return None
    

    