# acceptance_criteria_checker.py

from typing import List, Dict
import json  # Added for string parsing
from pathlib import Path  # Added for file path handling
import requests  # Add this import
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- LLM Clients Initialization ---
# Try to initialize OpenAI
openai_client = None
try:
    from openai import OpenAI

    if os.getenv("OPENAI_API_KEY"):
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except ImportError:
    pass

# Try to initialize Gemini
gemini_enabled = False
genai = None
try:
    import google.generativeai as genai

    if os.getenv("GOOGLE_API_KEY"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        gemini_enabled = True
except ImportError:
    pass


# Placeholder function for LLM verification
def verify_with_llm(test_case: str, acceptance_criteria: str) -> bool:
    """
    Simulate LLM verification.
    Replace this function with actual LLM API call.

    Returns True if test_case satisfies acceptance_criteria, else False
    """
    # Example naive check: test case contains a keyword from acceptance criteria
    # Replace with actual LLM prompt call
    return all(
        keyword.lower() in test_case.lower()
        for keyword in acceptance_criteria.split(",")
    )


def call_llm_for_validation(prompt: str) -> str:
    """
    Dedicated LLM function for validation tasks.
    Tries OpenAI -> Gemini -> Local Ollama Server.
    """

    # Try OpenAI first
    if openai_client:
        try:
            print("⚡ Using OpenAI GPT...")
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Software Testing Expert. Return only the requested format.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            output_text = response.choices[0].message.content
            print(f"📝 OpenAI response length: {len(output_text)} characters")
            return output_text

        except Exception as e:
            print(f"❌ OpenAI call failed: {e}")

    # Try Gemini second
    if gemini_enabled and genai:
        try:
            print("⚡ Using Google Gemini...")
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            output_text = response.text
            print(f"📝 Gemini response length: {len(output_text)} characters")
            return output_text

        except Exception as e:
            print(f"❌ Gemini call failed: {e}")

    # Try Local Ollama Server (HTTP API)
    try:
        print("⚡ Using Local Ollama Server (openai/gpt-oss-20b)...")

        # Prepare the request payload
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Software Testing Expert. Return only the requested format.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
            "stream": False,
        }

        # Make the HTTP request to your local Ollama server with increased timeout
        response = requests.post(
            "http://192.168.0.155:1234/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=300,  # Increased to 5 minutes
        )

        if response.status_code == 200:
            result = response.json()
            output_text = result["choices"][0]["message"]["content"]
            print(f"📝 Local Ollama response length: {len(output_text)} characters")
            return output_text
        else:
            print(
                f"❌ Local Ollama server error: {response.status_code} - {response.text}"
            )

    except requests.exceptions.Timeout:
        print("❌ Local Ollama server request timed out (5 minutes)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Local Ollama server connection failed: {e}")
    except Exception as e:
        print(f"❌ Local Ollama call failed: {e}")

    raise Exception("All LLM calls failed")


def verify_test_case_with_llm(
    test_case: Dict[str, str], acceptance_criteria: str
) -> bool:
    """
    Use LLM to verify if a test case satisfies the acceptance criteria.
    """

    # Create a detailed prompt for LLM verification
    llm_prompt = f"""
You are a software testing expert. Your task is to determine whether a given test case satisfies the provided acceptance criteria.

ACCEPTANCE CRITERIA:
{acceptance_criteria}

TEST CASE:
- Scenario: {test_case.get('scenario', 'N/A')}
- Steps: {test_case.get('steps', 'N/A')}
- Expected Result: {test_case.get('expected', 'N/A')}

ANALYSIS INSTRUCTIONS:
1. Carefully read and understand the acceptance criteria.
2. Analyze the test case scenario, steps, and expected result.
3. Determine whether the test case effectively verifies that the acceptance criteria are met.
4. Check if the test case covers all key requirements and expected outcomes.
5. Flag missing coverage, ambiguity, or misalignment (internally, do not output these flags).

RESPONSE FORMAT:
- Return ONLY a single Boolean value:
    - "True" → if the test case satisfies the acceptance criteria.
    - "False" → if the test case does not satisfy the acceptance criteria.
- Do NOT include any additional text, explanation, or formatting.

RULES:
- Your output must be strictly "True" or "False".
- Avoid any extra commentary; the response should be machine-readable for automated pipelines.
"""

    # Use LLM for verification
    response = call_llm_for_validation(llm_prompt)

    # Parse LLM response
    if isinstance(response, str):
        result = response.strip().lower()
        return "true" in result

    # If LLM fails, raise error
    raise Exception(
        f"LLM verification failed for test case '{test_case.get('scenario', 'Unknown')}': Invalid response format"
    )


def verify_test_cases_batch_with_llm(
    test_cases: List[Dict[str, str]], acceptance_criteria: str
) -> List[bool]:
    """
    Use LLM to verify multiple test cases in a single call to reduce API usage.
    """

    # Create a batch prompt for all test cases
    test_cases_text = ""
    for i, tc in enumerate(test_cases, 1):
        test_cases_text += f"""
Test Case {i}:
- Scenario: {tc.get('scenario', 'N/A')}
- Steps: {tc.get('steps', 'N/A')}
- Expected Result: {tc.get('expected', 'N/A')}
"""

    llm_prompt = f"""
You are a software testing expert. Your task is to determine which test cases satisfy given acceptance criteria.

ACCEPTANCE CRITERIA:
{acceptance_criteria}

TEST CASES TO EVALUATE:
{test_cases_text}

ANALYSIS INSTRUCTIONS:
1. Read the acceptance criteria carefully
2. Analyze each test case scenario, steps, and expected result
3. Determine if each test case will verify that the acceptance criteria is met
4. Consider if the test case covers the key requirements and expected outcomes

RESPONSE FORMAT:
Return ONLY a JSON array of exactly {len(test_cases)} boolean values.
Example: [true, false, true, false, true, false, true, false]

Where:
- true = test case satisfies the acceptance criteria
- false = test case does not satisfy the acceptance criteria
- The order must match the test cases exactly (Test Case 1 = index 0, Test Case 2 = index 1, etc.)

CRITICAL: Return ONLY the JSON array, no other text.
"""

    # Use LLM for batch verification
    response = call_llm_for_validation(llm_prompt)

    # Parse LLM response with better validation
    try:
        # Try to extract JSON from string
        json_start = response.find("[")
        json_end = response.rfind("]") + 1
        if json_start != -1 and json_end != 0:
            json_content = response[json_start:json_end]
            result = json.loads(json_content)
            if isinstance(result, list) and len(result) == len(test_cases):
                # Validate that all items are booleans
                if all(isinstance(item, bool) for item in result):
                    return result
                else:
                    print(f"⚠️ Extracted list contains non-boolean values: {result}")
                    raise Exception("Invalid boolean format")
    except Exception as e:
        print(f"⚠️ String parsing failed: {e}")

    # If LLM fails, raise error
    raise Exception(
        f"LLM batch verification failed: Invalid response format. Expected {len(test_cases)} boolean values."
    )


def check_acceptance_criteria(
    test_cases: List[Dict[str, str]], acceptance_criteria: str
) -> Dict[str, List[Dict[str, str]]]:
    """
    Check which test cases satisfy the acceptance criteria using LLM batch processing.
    """
    satisfied = []
    not_satisfied = []

    print(f"🔍 Validating {len(test_cases)} test cases against acceptance criteria...")

    try:
        # Use batch verification to reduce API calls
        print("  🚀 Using batch LLM verification to optimize API usage...")
        verification_results = verify_test_cases_batch_with_llm(
            test_cases, acceptance_criteria
        )

        # Process results
        for i, (tc, is_satisfied) in enumerate(
            zip(test_cases, verification_results), 1
        ):
            print(
                f"  Checking test case {i}/{len(test_cases)}: {tc.get('scenario', 'Unknown')[:50]}..."
            )

            if is_satisfied:
                tc["satisfies_criteria"] = True
                satisfied.append(tc)
                print(f"    ✅ Satisfies criteria")
            else:
                tc["satisfies_criteria"] = False
                not_satisfied.append(tc)
                print(f"    ❌ Does not satisfy criteria")

    except Exception as e:
        print(f"    ❌ LLM batch verification failed: {e}")
        # If batch verification fails, try individual verification as fallback
        print("  🔄 Falling back to individual verification...")

        for i, tc in enumerate(test_cases, 1):
            print(
                f"  Checking test case {i}/{len(test_cases)}: {tc.get('scenario', 'Unknown')[:50]}..."
            )

            try:
                # Use individual verification
                if verify_test_case_with_llm(tc, acceptance_criteria):
                    tc["satisfies_criteria"] = True
                    satisfied.append(tc)
                    print(f"    ✅ Satisfies criteria")
                else:
                    tc["satisfies_criteria"] = False
                    not_satisfied.append(tc)
                    print(f"    ❌ Does not satisfy criteria")
            except Exception as e:
                print(f"    ❌ LLM verification failed: {e}")
                # If LLM fails, stop execution
                raise Exception(
                    f"LLM verification failed for test case {i}. Cannot proceed without LLM analysis."
                )

    return {
        "satisfied": satisfied,
        "not_satisfied": not_satisfied,
        "summary": {
            "total_test_cases": len(test_cases),
            "satisfied_count": len(satisfied),
            "not_satisfied_count": len(not_satisfied),
            "satisfaction_rate": (
                len(satisfied) / len(test_cases) if test_cases else 0.0
            ),  # Return as float, not string
        },
    }


def save_validation_results(results: Dict, output_path: Path) -> None:
    """
    Save validation results to a JSON file.
    """
    output_file = output_path / "acceptance_criteria_validation.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Validation results saved to: {output_file}")


def generate_validation_report(results: Dict, acceptance_criteria: str) -> str:
    """
    Generate a human-readable validation report.
    """
    summary = results.get("summary", {})

    report = "# Acceptance Criteria Validation Report\n\n"
    report += f"**Acceptance Criteria:**\n{acceptance_criteria}\n\n"
    report += f"**Summary:**\n"
    report += f"- Total Test Cases: {summary.get('total_test_cases', 0)}\n"
    report += f"- Satisfied: {summary.get('satisfied_count', 0)}\n"
    report += f"- Not Satisfied: {summary.get('not_satisfied_count', 0)}\n"
    report += f"- Satisfaction Rate: {summary.get('satisfaction_rate', '0%')}\n\n"

    if results.get("satisfied"):
        report += "## ✅ Satisfied Test Cases\n\n"
        for tc in results["satisfied"]:
            report += f"### {tc.get('scenario', 'Unknown')}\n"
            report += f"- **Steps:** {tc.get('steps', 'N/A')}\n"
            report += f"- **Expected:** {tc.get('expected', 'N/A')}\n\n"

    if results.get("not_satisfied"):
        report += "## ❌ Test Cases Not Satisfying Criteria\n\n"
        for tc in results["not_satisfied"]:
            report += f"### {tc.get('scenario', 'Unknown')}\n"
            report += f"- **Steps:** {tc.get('steps', 'N/A')}\n"
            report += f"- **Expected:** {tc.get('expected', 'N/A')}\n\n"

    return report


def print_validation_summary(validation_results: Dict, test_cases: List[Dict]) -> None:
    """
    Print a detailed summary of validation results including unsatisfied test cases.
    """
    summary = validation_results.get("summary", {})
    satisfied = validation_results.get("satisfied", [])
    not_satisfied = validation_results.get("not_satisfied", [])

    print(f"\n VALIDATION SUMMARY:")
    print(f"   - Total Test Cases: {summary.get('total_test_cases', 0)}")
    print(
        f"   - Satisfied: {len(satisfied)} ({summary.get('satisfaction_rate', '0%')})"
    )
    print(f"   - Not Satisfied: {len(not_satisfied)}")

    if not_satisfied:
        print(
            f"\n❌ UNSATISFIED TEST CASES ({len(not_satisfied)} out of {len(test_cases)}):"
        )
        print("=" * 80)

        for i, tc in enumerate(not_satisfied, 1):
            print(f"\n❌ TC{i}: {tc.get('scenario', 'Unknown')}")
            print(f"   Steps: {tc.get('steps', 'N/A')}")
            print(f"   Expected: {tc.get('expected', 'N/A')}")
            print(f"   Type: {tc.get('type', 'N/A')}")
            print("-" * 60)

    if satisfied:
        print(f"\n✅ SATISFIED TEST CASES ({len(satisfied)} out of {len(test_cases)}):")
        print("=" * 80)

        for i, tc in enumerate(satisfied, 1):
            print(f"\n✅ TC{i}: {tc.get('scenario', 'Unknown')}")
            print(f"   Steps: {tc.get('steps', 'N/A')}")
            print(f"   Expected: {tc.get('expected', 'N/A')}")
            print(f"   Type: {tc.get('type', 'N/A')}")
            print("-" * 60)

    print(f"\n🎯 RECOMMENDATIONS:")
    if len(not_satisfied) > len(satisfied):
        print("   ⚠️  Many test cases don't satisfy acceptance criteria.")
        print("   💡 Consider:")
        print("      - Reviewing acceptance criteria for clarity")
        print("      - Regenerating test cases with more specific prompts")
        print("      - Adding missing business scenarios")
    else:
        print("   ✅ Good test coverage of acceptance criteria!")


if __name__ == "__main__":
    print("🔍 Acceptance Criteria Checker\n")

    # Example usage
    test_cases = [
        {
            "scenario": "Add item to cart",
            "steps": "Click add to cart button for item",
            "expected": "Item appears in cart with quantity 1",
        },
        {
            "scenario": "Remove item from cart",
            "steps": "Click remove button for item",
            "expected": "Item is removed from cart",
        },
        {
            "scenario": "Checkout with empty cart",
            "steps": "Click checkout button",
            "expected": "Error message displayed: 'Cart is empty'",
        },
    ]

    acceptance_criteria = "Users should be able to add items to cart, remove items from cart, and see appropriate error messages when trying to checkout with an empty cart."

    print("📋 Acceptance Criteria:")
    print(acceptance_criteria)
    print("\n" + "=" * 80 + "\n")

    # Validate test cases
    result = check_acceptance_criteria(test_cases, acceptance_criteria)

    # Display results
    print("\n Validation Results:")
    print(f"✅ Satisfied: {len(result['satisfied'])}")
    print(f"❌ Not Satisfied: {len(result['not_satisfied'])}")
    print(f" Satisfaction Rate: {result['summary']['satisfaction_rate']}")

    # Generate and save report
    report = generate_validation_report(result, acceptance_criteria)
    print("\n📝 Generated Report:")
    print(report)
