import json
from pathlib import Path
from src.logger.logger import AppLogger

class TestCaseImporter:
    def __init__(self, jira_client, project_key):
        self.logger = AppLogger(__name__).get_logger()
        self.jira_client = jira_client
        self.project_key = project_key
    
    def format_test_steps(self, test_steps):
        steps_formatted = "Test Steps\n\n"
        
        for step in test_steps:
            step_num = step.get("step_number", "")
            test_step = step.get("test_step", "")
            expected_output = step.get("expected_output", "")
            steps_formatted += f"step_number:{step_num}\ntest_step:{test_step}\nexpected_output:{expected_output}\n"
        
        return steps_formatted
    
    def create_test_case(self, test_case, user_story_id=None, test_type=None):
        description = test_case.get("test_case_description", "")
        test_steps = test_case.get("test_steps", [])

        steps_formatted = self.format_test_steps(test_steps)
        
        # Build complete description
        full_description = {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": description
                        }
                    ]
                }
            ]
        }
        
        if test_type:
            full_description["content"].append({
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "Test Type"}]
            })
            full_description["content"].append({
                "type": "paragraph",
                "content": [{"type": "text", "text": test_type}]
            })
        
        full_description["content"].append({
            "type": "codeBlock",
            "attrs": {"language": "text"},
            "content": [{"type": "text", "text": steps_formatted}]
        })
        
        summary = f"{test_type if test_type else 'Test'}: {description}"
        
        test_case_key = self.jira_client.create_test_case(
            self.project_key,
            summary,
            full_description,
            test_steps
        )
        
        if test_case_key and user_story_id:
            self.jira_client.link_test_case_to_story(test_case_key, user_story_id)
        
        return test_case_key
    
    def process_test_case_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            user_story = data.get("user_story", {})
            user_story_id = user_story.get("id")
            
            test_cases_by_type = data.get("test_cases_by_type", {})
            created_count = 0
            
            for test_type, test_cases_data in test_cases_by_type.items():
                test_cases = test_cases_data.get("test_cases", [])
                
                for test_case in test_cases:
                    test_case_key = self.create_test_case(
                        test_case,
                        user_story_id=user_story_id,
                        test_type=test_type
                    )
                    if test_case_key:
                        created_count += 1
            
            self.logger.info(f"Processed file {file_path}: created {created_count} test cases")
            return created_count
        except UnicodeDecodeError as ude:
            self.logger.error(f"Unicode decode error in {file_path}. Trying with different encodings...")

            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    self.logger.info(f"Attempting to read {file_path} with {encoding} encoding")
                    with open(file_path, 'r', encoding=encoding) as f:
                        data = json.load(f)

                    user_story = data.get("user_story", {})
                    user_story_id = user_story.get("id")
                    
                    test_cases_by_type = data.get("test_cases_by_type", {})
                    created_count = 0
                    
                    for test_type, test_cases_data in test_cases_by_type.items():
                        test_cases = test_cases_data.get("test_cases", [])
                        
                        for test_case in test_cases:
                            test_case_key = self.create_test_case(
                                test_case,
                                user_story_id=user_story_id,
                                test_type=test_type
                            )
                            if test_case_key:
                                created_count += 1
                    
                    self.logger.info(f"Successfully processed file {file_path} with {encoding} encoding: created {created_count} test cases")
                    return created_count
                except Exception as e:
                    self.logger.error(f"Error processing {file_path} with {encoding} encoding: {e}")
            
            self.logger.error(f"Failed to process {file_path} with all attempted encodings")
            return 
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            return 