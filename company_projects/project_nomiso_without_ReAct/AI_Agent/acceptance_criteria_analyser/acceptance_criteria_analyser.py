import json
from pathlib import Path
import sys
import os

# Add parent directory to path to import from test_case_generator
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'test_case_generator'))
from test_case import setup_langchain_llms, call_langchain_llm

# Use your existing LangChain setup
def call_llm(prompt: str) -> str:
    """Use existing LangChain LLM integration"""
    llms = setup_langchain_llms()
    
    # Create a simple prompt template for acceptance criteria analysis
    from langchain.prompts import PromptTemplate
    prompt_template = PromptTemplate.from_template(prompt)
    
    # Call LLM using your existing system
    response = call_langchain_llm(prompt_template, llms)
    return str(response)

def analyze_acceptance_criteria(user_input: str) -> str:
    """
    Analyzes user-provided acceptance criteria using LLM.
    Returns structured insights about the criteria.
    """
    llm_prompt = f"""
    You are a software tester. Analyze the following acceptance criteria provided by the user.

    ACCEPTANCE CRITERIA:
    {user_input}

    TASK:
    - Extract what the criteria is about
    - What the user wants
    - What the expected outcome is
    - Make the analysis clear and structured

    OUTPUT FORMAT:
    Provide a JSON with:
    {{
        "criteria_summary": "...",
        "requirements": ["...", "..."],
        "expected_outcome": "..."
    }}
    """
    response = call_llm(llm_prompt)
    return response

def evaluate_test_cases(test_cases: list, analyzed_criteria: dict) -> list:
    """
    Evaluates test cases against analyzed acceptance criteria.
    Returns test cases with an added field: 'satisfies_criteria': True/False
    """
    satisfied_cases = []
    for case in test_cases:
        # Prepare a prompt to check if this test case satisfies criteria
        llm_prompt = f"""
        You are a software tester. Check if the following test case satisfies the acceptance criteria.

        ACCEPTANCE CRITERIA:
        {json.dumps(analyzed_criteria, indent=2)}

        TEST CASE:
        {json.dumps(case, indent=2)}

        TASK:
        Return "True" if this test case satisfies the criteria, otherwise "False".
        """
        result = call_llm(llm_prompt).strip().lower()
        satisfies = True if "true" in result else False
        case['satisfies_criteria'] = satisfies
        satisfied_cases.append(case)
    
    return satisfied_cases

if __name__ == "__main__":
    print("🚀 Acceptance Criteria Analyzer\n")

    # Step 1: Get acceptance criteria input
    user_criteria = input("Enter acceptance criteria: ").strip()
    if not user_criteria:
        print("❌ Acceptance criteria cannot be empty.")
        exit(1)

    # Step 2: Analyze the acceptance criteria via LLM
    print("\n⏳ Analyzing acceptance criteria...\n")
    analysis = analyze_acceptance_criteria(user_criteria)
    print("🔹 Analysis Output:\n")
    print(analysis)

    # Step 3: Optionally evaluate existing test cases
    test_cases_file = input("\nEnter path to JSON test cases file (or leave empty to skip evaluation): ").strip()
    if test_cases_file:
        test_cases_path = Path(test_cases_file)
        if not test_cases_path.exists():
            print(f"❌ File not found: {test_cases_file}")
            exit(1)
        
        with open(test_cases_path, "r", encoding="utf-8") as f:
            test_cases = json.load(f)
        
        print("\n⚡ Evaluating test cases against acceptance criteria...\n")
        analyzed_criteria_dict = json.loads(analysis) if isinstance(analysis, str) else analysis
        evaluated_cases = evaluate_test_cases(test_cases, analyzed_criteria_dict)
        
        # Save results
        results_file = test_cases_path.parent / "evaluated_test_cases.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(evaluated_cases, f, indent=2)
        
        print(f"✅ Evaluated test cases saved to: {results_file}")
