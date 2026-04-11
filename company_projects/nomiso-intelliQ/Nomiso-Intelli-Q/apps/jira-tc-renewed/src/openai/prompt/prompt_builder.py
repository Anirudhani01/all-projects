import os
from src.openai.prompt.prompts_structure import PromptsDesign
from src.story_parser.user_story_parser import UserStoryParser
from src.logger.logger import AppLogger  


class PromptBuilder:
    def __init__(self, parser: UserStoryParser):
        self.parser = parser
        self.logger = AppLogger(__name__).get_logger()
        self.logger.info("-------- PromptBuilder initialized with UserStoryParser --------")


    def get_test_case_generation_flow_prompt(self, existing_testcases: str = "", test_case_type: str = "") -> list[dict]:
        self.logger.info(f"Generating TEST_CASE_GENERATION_FLOW_PROMPT for test_case_type: '{test_case_type}'")
        template = PromptsDesign.TEST_CASE_GENERATION_FLOW_PROMPT.value
        user_story_text = self.parser.get_story_text()
        acceptance_criteria_list = self.parser.get_acceptance_criteria()
        acceptance_criteria_1 = acceptance_criteria_list[0] if acceptance_criteria_list else ""

        prompt = template
        prompt = prompt.replace("<--user_story-->", user_story_text)
        prompt = prompt.replace("<--acceptance_criteria-->", acceptance_criteria_1)
        prompt = prompt.replace("<--existing_testcases-->", existing_testcases)
        prompt = prompt.replace("<--test_case_type-->", test_case_type)
        try:

            base_dir = os.path.dirname(os.path.abspath(__file__))

            businees_path = ''
            if 'log in' in self.parser.get_story_text().lower():
                businees_path = r'login.txt'
            elif 'create product' in self.parser.get_story_text().lower():
                businees_path = r'Prod_creation.txt'
            else:
                businees_path = r'Prod_search.txt'

            businees_path = os.path.join(base_dir, businees_path)
            AppLogger(__name__).log_status(businees_path)

            with open(businees_path, 'r') as file:
                content = file.read()
                AppLogger(__name__).log_status(content)
                prompt = prompt.replace("<--business_context-->", content)
        except Exception as e:
            self.logger.warning("Business Context is not provided, so skipping it")


        self.logger.info("Prompt generated successfully")
        return [
            {'role': 'system', 'content': PromptsDesign.TEST_CASE_GENERATION_SYSTEM_PROMPT.value},
            {'role': 'user', 'content': prompt}
        ]


# Optional example usage if needed:
if False:
    parser = UserStoryParser("train/user_test1.json")
    parser.load_data()

    prompt_builder = PromptBuilder(parser)

    print("\n=== TEST_CASE_GENERATION_FLOW_PROMPT ===\n")
    for message in prompt_builder.get_test_case_generation_flow_prompt(existing_testcases="[]", test_case_type="Positive Test Cases"):
        print(f"Role: {message['role']}\nContent:\n{message['content']}\n{'-'*40}")
