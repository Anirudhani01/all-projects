from enum import Enum

class PromptsDesign(Enum):
   

    TEST_CASE_GENERATION_SYSTEM_PROMPT = f"""
    You are an experienced QUALITY ASSURANCE (QA) ENGINEER with expertise in designing detailed, structured, and comprehensive test cases. Stick to user story.
    Your task is to analyze the provided `USER_STORY`, `BUSINESS_CONTEXT` and generate clear, structured test cases. They can include any credentials in it except user password.
    """

    TEST_CASE_GENERATION_FLOW_PROMPT = f"""
    TASK:
    1. Analyze the `USER_STORY  and `BUSINESS_CONTEXT` to understand core functionality and expected user behavior.
    2. Identify relevant USER JOURNEYS ONLY from the current position based on the given `USER_STORY` and do not consider previous scenarios.
    3. For each USER JOURNEY, use `BUSINESS_CONTEXT` as a knowledge base to generate comprehensive test cases covering all "<--test_case_type-->".
    4. Structure each test case clearly and logically as follows:
        - Test Case Description: Concise explanation of the test case's purpose.
        - Test Steps: Sequential actions, each building logically on the current position of user. Assume that previous steps and conditions are taken care of. 
        - Expected Output: Expected result after the test step but only for event triggered by user. Provide the best expected outcome, rather than multiple options.
    5. Do NOT create test cases already present in `EXISTING_TESTCASES`.
    6. Arrange all test cases and steps in a logical sequence reflecting the user journey and you can not include urls which are random and usernames but not the passwords.
    7. Never forget to add test scenario starting page mentioned in ACCEPTANCE_CRITERIA. 
    8. DO NOT break down one single test scenario into multiple test scenarios. 
   

    **OUTPUT FORMAT (JSON):**
    {{
        "test_cases": [
            {{
                "test_case_description": "<Concise test case description>",
                "test_steps": [
                    {{
                        "step_number": 1,
                        "test_step": "<Description of the test step>",
                        "expected_output": "<Expected result after execution of test step>"
                    }}
                ]
            }}
        ]
    }}

    **USER_STORY:** ```<--user_story-->```
    **ACCEPTANCE_CRITERIA**: ```<--acceptance_criteria-->```
    **EXISTING_TESTCASES:** ```<--existing_testcases-->```
    **BUSINESS_CONTEXT:** ```<--business_context-->``` 
    
    **OUTPUT:**
    """
