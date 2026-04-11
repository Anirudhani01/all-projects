import json
import requests
from src.logger.logger import AppLogger


class TestCaseImporter:
    def __init__(self, jira_client, project_key, qa_project_key):
        self.logger = AppLogger(__name__).get_logger()
        self.jira_client = jira_client
        self.project_key = project_key
        self.qa_project_key = qa_project_key

    
    def format_test_steps(self, test_steps):
        """
        Format test steps as an Atlassian Document Format (ADF) table.
        This allows Jira to display the table in rich text format.
        """
        table_content = []
        header_row = {
            "type": "tableRow",
            "content": [
                {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Step #"}]}]},
                {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Test Step"}]}]},
                {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Expected Output"}]}]},
            ]
        }
        table_content.append(header_row)

        for step in test_steps:
            row = {
                "type": "tableRow",
                "content": [
                    {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": str(step.get("step_number", ""))}]}]},
                    {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": step.get("test_step", "")}]}]},
                    {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": step.get("expected_output", "--")}]}]},
                ]
            }
            table_content.append(row)

        return {
            "type": "table",
            "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
            "content": table_content
        }

    def create_test_case(self, test_case, user_story_id=None, test_type=None):
        description = test_case.get("test_case_description", "")
        test_steps = test_case.get("test_steps", [])

        full_description = {
        "version": 1,
        "type": "doc",
        "content": []
        }
        summary = f"{test_type if test_type else 'Test'}: {description}"
        steps_table_adf = self.format_test_steps(test_steps)
        full_description["content"].append(steps_table_adf)
        
        test_case_key = self.jira_client.create_test_case(
            self.qa_project_key,
            summary,
            full_description,
            test_steps
        )
        
        if test_case_key and user_story_id:
            self.jira_client.link_test_case_to_story(test_case_key, user_story_id)
        
        return test_case_key

    def process_nested_test_cases(self, nested_test_cases):
        """
        Process nested test cases and upload them to Jira.
        """
        try:
            created_count = 0
            
            for data in nested_test_cases:
                user_story = data.get("user_story", {})
                user_story_id = user_story.get("id")

                test_cases_by_type = data.get("test_cases_by_type", {})

                for test_type, test_cases_data in test_cases_by_type.items():
                    AppLogger(__name__).log_status("Sending test case to JIRA")
                    test_cases = test_cases_data.get("test_cases", [])

                    for test_case in test_cases:
                        test_case_key = self.create_test_case(
                            test_case,
                            user_story_id=user_story_id,
                            test_type=test_type
                        )
                        if test_case_key:
                            created_count += 1
                            self.logger.info(f"Created test case: {test_case_key}")
                        else:
                            self.logger.warning(f"Failed to create test case for: {test_case.get('test_case_description', 'Unknown')}")

            self.logger.info(f"Processed nested test cases: created {created_count} test cases")
            return created_count
        except Exception as e:
            self.logger.error(f"Error processing nested test cases: {e}", exc_info=True)
            return 0