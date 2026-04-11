import os
import json
import requests
from requests.auth import HTTPBasicAuth
import sys
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'test_case_generator.env'))

class JiraTestCaseFetcher:
    def __init__(self, domain, email, api_token):
        self.domain = domain
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {
            "Accept": "application/json"
        }
        self.base_url = f"https://{domain}/rest/api/3"

    def get_issue(self, issue_key):
        url = f"{self.base_url}/issue/{issue_key}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def extract_test_steps_from_adf(self, description_adf):
        """
        Extracts test steps from the Atlassian Document Format (ADF) table in the description field.
        Returns a list of dicts with step_number, test_step, expected_output.
        """
        test_steps = []
        if not description_adf:
            return test_steps

        # The description is a dict with 'content' key
        content = description_adf.get('content', [])
        for block in content:
            if block.get('type') == 'table':
                # Found the table block
                rows = block.get('content', [])
                # Skip header row (first row)
                for row in rows[1:]:
                    cells = row.get('content', [])
                    if len(cells) >= 3:
                        step_number = self.extract_text_from_adf(cells[0])
                        test_step = self.extract_text_from_adf(cells[1])
                        expected_output = self.extract_text_from_adf(cells[2])
                        test_steps.append({
                            "step_number": step_number,
                            "test_step": test_step,
                            "expected_output": expected_output
                        })
                break
        return test_steps

    def extract_text_from_adf(self, cell):
        """
        Extract text from an ADF table cell, which contains paragraphs and text nodes.
        """
        texts = []
        for paragraph in cell.get('content', []):
            if paragraph.get('type') == 'paragraph':
                for text_node in paragraph.get('content', []):
                    if text_node.get('type') == 'text':
                        texts.append(text_node.get('text', ''))
        return ' '.join(texts).strip()

    def save_test_case(self, issue_key, summary, description, test_steps):
        """
        Save the test case details in a JSON file inside test_cases directory.
        """
        os.makedirs('test_cases', exist_ok=True)
        filename = os.path.join('test_cases', f"{issue_key}.json")
        data = {
            "issue_key": issue_key,
            "summary": summary,
            "description": description,
            "test_steps": test_steps
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Saved test case {issue_key} to {filename}")

    def fetch_and_save_test_case(self, issue_key):
        issue = self.get_issue(issue_key)
        fields = issue.get('fields', {})
        summary = fields.get('summary', '')
        description = fields.get('description', {})

        # description may be a dict (ADF) or string, handle both
        if isinstance(description, dict):
            test_steps = self.extract_test_steps_from_adf(description)
            # For human-readable description text, extract paragraphs excluding the table
            desc_text = self.extract_plain_text_from_adf(description)
        else:
            test_steps = []
            desc_text = description if description else ""

        self.save_test_case(issue_key, summary, desc_text, test_steps)

    def extract_plain_text_from_adf(self, description_adf):
        """
        Extract plain text from ADF description ignoring tables.
        """
        texts = []
        for block in description_adf.get('content', []):
            if block.get('type') == 'paragraph':
                for text_node in block.get('content', []):
                    if text_node.get('type') == 'text':
                        texts.append(text_node.get('text', ''))
        return '\n'.join(texts).strip()


# if __name__ == "__main__":
#     if len(sys.argv) > 1:
#         arg1 = sys.argv[1]
#     else:
#         print("No command-line arguments provided.")
#         exit
#     # Replace with your Jira details
#     DOMAIN = os.getenv('JIRA_DOMAIN')
#     EMAIL = os.getenv("EMAIL")
#     API_TOKEN = os.getenv("JIRA_API")

#     # Test case ID from Jira (e.g., "PROJ-123")
#     TEST_CASE_ID = arg1

#     fetcher = JiraTestCaseFetcher(DOMAIN, EMAIL, API_TOKEN)
#     fetcher.fetch_and_save_test_case(TEST_CASE_ID)