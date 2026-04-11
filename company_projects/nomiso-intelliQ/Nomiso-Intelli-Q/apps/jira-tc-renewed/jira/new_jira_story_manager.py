from jira.jira_client import JiraClient
from jira.new_jira_story_parser import UserStoryParser
import os
import json
from dotenv import load_dotenv
from src.logger.logger import AppLogger

load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'test_case_generator.env'))

class JiraManager:
    def __init__(self):
        self.logger = AppLogger('Jira Story Extraction').get_logger()
        self.logger.info("Initializing JiraManager...")

        try:
            self.email = str(os.getenv('EMAIL'))
            self.domain = str(os.getenv('JIRA_DOMAIN'))
            self.jira_api = str(os.getenv('JIRA_API'))
            self.jira_project = str(os.getenv('JIRA_STORY_PROJECT'))
            self.input_dir = str(os.getenv('INPUT_DIR'))

            self.logger.info(f"Loaded environment variables: EMAIL={self.email}, DOMAIN={self.domain}, PROJECT={self.jira_project}")

            jira = JiraClient(self.email, self.jira_api, self.domain)

            self.logger.info("Fetching user stories from Jira...")
            issues = jira.get_user_stories(self.jira_project)

            self.logger.info(f"Fetched {len(issues)} issues. Processing...")
            self.process_and_save_user_stories(issues, output_dir=self.input_dir)

        except Exception as e:
            self.logger.error(f"Error during Jira user story extraction: {str(e)}", exc_info=True)

    def process_and_save_user_stories(self, issues, output_dir):
        for issue in issues:
            try:
                story_id = issue.get("key")
                summary = issue["fields"].get("summary", "")
                description = issue["fields"].get("description", {})

                self.logger.info(f"Processing story {story_id}: {summary}")

                if description and isinstance(description, dict):
                    adf = description.get("content", [])
                    parser = UserStoryParser(adf=adf, issue_id=story_id, title=summary)
                    story_data = parser.parse()

                    self.save_user_story_to_file(story_data, output_dir)
                else:
                    self.logger.warning(f"No valid description found for issue {story_id}. Skipping.")
            except Exception as e:
                self.logger.error(f"Failed to process issue {issue.get('key', 'UNKNOWN')}: {str(e)}", exc_info=True)

    def save_user_story_to_file(self, story_data, directory):
        try:
            os.makedirs(directory, exist_ok=True)
            filename = os.path.join(directory, f"{story_data['user_story']['id']}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(story_data, f, indent=4)
            self.logger.info(f"Saved user story to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving file {filename}: {str(e)}", exc_info=True)
