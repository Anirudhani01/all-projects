from jira.jira_client import JiraClient
from jira.new_jira_story_parser import UserStoryParser
import os
import json
from dotenv import load_dotenv
from src.logger.logger import AppLogger

load_dotenv(dotenv_path=os.path.join(os.getcwd(), "test_case_generator.env"))


class JiraManager:
    def __init__(self, story_id):
        self.logger = AppLogger("Jira Story Extraction").get_logger()
        self.logger.info("Initializing JiraManager...")
        AppLogger(__name__).log_status("Getting the user Story")

        self.story_id = story_id
        self.userStories = []

        try:
            self.email = str(os.getenv("EMAIL"))
            self.domain = str(os.getenv("JIRA_DOMAIN"))
            self.jira_api = str(os.getenv("JIRA_API"))
            self.jira_project = str(os.getenv("JIRA_STORY_PROJECT"))

            if not all(
                [
                    self.email,
                    self.domain,
                    self.jira_api,
                    self.jira_project,
                    self.story_id,
                ]
            ):
                raise ValueError("Missing environment variables or story_id.")

            self.logger.info(
                f"Loaded environment variables: EMAIL={self.email}, DOMAIN={self.domain}, PROJECT={self.jira_project}"
            )
            jira = JiraClient(self.email, self.jira_api, self.domain)

            self.logger.info(f"Fetching user story with ID: {self.story_id}")
            issue = jira.get_user_story_by_id(self.story_id)

            if issue:
                self.logger.info(f"Processing story {self.story_id}...")
                self.process_and_save_user_stories([issue])
            else:
                self.logger.error(f"User story with ID {self.story_id} not found.")

        except Exception as e:
            print("The error::", e)
            self.logger.error(
                f"Error during Jira user story extraction: {str(e)}", exc_info=True
            )

    def process_and_save_user_stories(self, issues):
        for issue in issues:
            try:
                if not isinstance(issue, dict):
                    raise ValueError(f"Issue is not a valid dictionary: {issue}")

                story_id = issue.get("key")
                summary = issue["fields"].get("summary", "")
                description = issue["fields"].get("description", {})

                # self.logger.info(f"Processing story {story_id}: {summary}")

                if description and isinstance(description, dict):
                    adf = description.get("content", [])
                    parser = UserStoryParser(adf=adf, issue_id=story_id, title=summary)
                    story_data = parser.parse()
                    self.userStories.append(story_data)
                else:
                    self.logger.warning(
                        f"No valid description found for issue {story_id}. Skipping."
                    )
            except Exception as e:
                self.logger.error(
                    f"Failed to process issue {issue.get('key', 'UNKNOWN')}: {str(e)}",
                    exc_info=True,
                )
