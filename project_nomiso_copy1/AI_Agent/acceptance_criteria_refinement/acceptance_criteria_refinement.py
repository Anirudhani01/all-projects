# acceptance_criteria_refinement.py

import json
import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import requests

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

def call_llm_for_refinement(prompt: str) -> str:
    """
    Dedicated LLM function for refinement tasks.
    Tries OpenAI -> Gemini -> Local Ollama Server.
    """
    
    # Try OpenAI first
    if openai_client:
        try:
            print("⚡ Using OpenAI GPT for refinement...")
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Software Testing Expert specializing in test case refinement and gap analysis. Return only the requested format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            output_text = response.choices[0].message.content
            print(f"📝 OpenAI refinement response length: {len(output_text)} characters")
            return output_text
            
        except Exception as e:
            print(f"❌ OpenAI refinement call failed: {e}")
    
    # Try Gemini second
    if gemini_enabled and genai:
        try:
            print("⚡ Using Google Gemini for refinement...")
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            output_text = response.text
            print(f"📝 Gemini refinement response length: {len(output_text)} characters")
            return output_text
                    
        except Exception as e:
            print(f"❌ Gemini refinement call failed: {e}")
    
    # Try Local Ollama Server (HTTP API)
    try:
        print("⚡ Using Local Ollama Server for refinement...")
        
        # Prepare the request payload
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": "You are a Software Testing Expert specializing in test case refinement and gap analysis. Return only the requested format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 4000,
            "stream": False
        }
        
        # Make the HTTP request to your local Ollama server
        response = requests.post(
            "http://192.168.0.155:1234/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            output_text = result["choices"][0]["message"]["content"]
            print(f"📝 Local Ollama refinement response length: {len(output_text)} characters")
            return output_text
        else:
            print(f"❌ Local Ollama server error: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Local Ollama server request timed out (5 minutes)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Local Ollama server connection failed: {e}")
    except Exception as e:
        print(f"❌ Local Ollama refinement call failed: {e}")
    
    raise Exception("All LLM calls failed for refinement")

def analyze_gaps_with_llm(test_cases: List[Dict], acceptance_criteria: str, validation_results: Dict) -> Dict:
    """
    Use LLM to analyze gaps between test cases and acceptance criteria.
    """
    
    llm_prompt = f"""
You are a software testing expert. Your task is to analyze gaps between the generated test cases and the acceptance criteria, providing a structured, actionable report.

ACCEPTANCE CRITERIA:
{acceptance_criteria}

CURRENT TEST CASES:
{json.dumps(test_cases, indent=2)}

VALIDATION RESULTS:
- Satisfaction Rate: {validation_results['summary']['satisfaction_rate']:.1%}
- Satisfied Test Cases: {len(validation_results['satisfied'])}
- Unsatisfied Test Cases: {len(validation_results['not_satisfied'])}

UNSATISFIED TEST CASES:
{json.dumps(validation_results['not_satisfied'], indent=2)}

TASK:
1. Identify missing criteria not covered by any test cases.
2. Highlight criteria that are weakly covered and specify what additional testing is needed.
3. Provide specific recommendations for new or improved test cases.
4. Categorize missing or weak coverage by test type (Happy, Negative, Edge) if applicable.

OUTPUT FORMAT (strict JSON):
{{
    "gap_analysis": {{
        "missing_criteria": [
            {{
                "criterion": "description of missing criterion",
                "reason": "why it's not covered",
                "test_type_needed": "Happy|Negative|Edge"
            }}
        ],
        "weak_coverage": [
            {{
                "criterion": "description of weakly covered criterion",
                "current_coverage": "what's currently tested",
                "improvement_needed": "what additional testing is needed"
            }}
        ],
        "recommendations": [
            "specific recommendation for new or improved test cases"
        ]
    }}
}}

RULES:
- Return ONLY the JSON response; do not include any extra text or commentary.
- Ensure all fields are filled where applicable; do not leave placeholders.
- Use clear, concise, professional language suitable for QA documentation.
"""

    
    try:
        response = call_llm_for_refinement(llm_prompt)
        
        # Extract JSON from response
        try:
            gap_analysis = json.loads(response)
            return gap_analysis
        except json.JSONDecodeError:
            # Try to extract JSON from within the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_content = response[json_start:json_end]
                gap_analysis = json.loads(json_content)
                return gap_analysis
            else:
                raise Exception("No valid JSON found in LLM response")
                
    except Exception as e:
        raise Exception(f"Gap analysis failed: {e}")

def generate_targeted_test_cases_with_llm(gap_analysis: Dict, user_story: str, knowledge_base: str) -> List[Dict]:
    """
    Use LLM to generate targeted test cases based on gap analysis.
    """
    
    llm_prompt = f"""
    You are a software testing expert. Generate targeted test cases to address the identified gaps.

    USER STORY:
    {user_story} 

    KNOWLEDGE BASE:
    {knowledge_base}

    GAP ANALYSIS:
    {json.dumps(gap_analysis, indent=2)}

    TASK:
    Generate ONLY the missing test cases needed to address the gaps identified in the analysis.
    Do NOT regenerate existing test cases, only add the missing ones.

    OUTPUT FORMAT (JSON array):
    [
        {{
            "scenario": "Clear, descriptive test scenario",
            "steps": "Detailed step-by-step test execution",
            "expected": "Expected result or outcome",
            "type": "Happy|Negative|Edge|Security|Performance",
            "status": "Pending",
            "targets_criterion": "which acceptance criterion this test case addresses"
        }}
    ]

    CRITICAL REQUIREMENTS:
    - Generate ONLY the missing test cases identified in the gap analysis
    - Each test case must directly address a specific missing criterion
    - Make test cases SPECIFIC and ACTIONABLE
    - Use the knowledge base to make scenarios realistic
    - Return ONLY a valid JSON array, no additional text

    Return ONLY the JSON array, no additional text or explanations.
    """
    
    try:
        response = call_llm_for_refinement(llm_prompt)
        
        # Extract JSON from response
        try:
            test_cases = json.loads(response)
            if isinstance(test_cases, list):
                return test_cases
            else:
                raise Exception("LLM response is not a list")
        except json.JSONDecodeError:
            # Try to extract JSON from within the response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end != 0:
                json_content = response[json_start:json_end]
                test_cases = json.loads(json_content)
                if isinstance(test_cases, list):
                    return test_cases
                else:
                    raise Exception("Extracted content is not a list")
            else:
                raise Exception("No valid JSON array found in LLM response")
                
    except Exception as e:
        raise Exception(f"Targeted test case generation failed: {e}")

def parse_refinement_output(llm_output: str) -> List[Dict]:
    """
    Parse the LLM output to extract refined test cases.
    """
    
    try:
        # Try direct JSON parsing
        test_cases = json.loads(llm_output)
        if isinstance(test_cases, list):
            return test_cases
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON array from within the response
    json_start = llm_output.find('[')
    json_end = llm_output.rfind(']') + 1
    
    if json_start != -1 and json_end != 0:
        json_content = llm_output[json_start:json_end]
        try:
            test_cases = json.loads(json_content)
            if isinstance(test_cases, list):
                return test_cases
        except json.JSONDecodeError:
            pass
    
    raise Exception("Could not parse test cases from LLM output")

def refine_test_cases_iteratively(
    test_cases: List[Dict], 
    acceptance_criteria: str, 
    user_story: str, 
    knowledge_base: str,
    validator_function,
    max_iterations: int = 5, 
    threshold: float = 0.9
) -> Tuple[List[Dict], float]:
    """
    Main refinement function that implements the ReAct cycle.
    
    Args:
        test_cases: Initial test cases
        acceptance_criteria: User-provided acceptance criteria
        user_story: Original user story
        knowledge_base: Domain knowledge
        validator_function: Function to validate test cases
        max_iterations: Maximum number of refinement loops
        threshold: Target satisfaction rate (default 90%)
    
    Returns:
        Tuple of (final_test_cases, final_satisfaction_rate)
    """
    
    current_test_cases = test_cases.copy()
    iteration = 0
    
    print(f"\n Starting iterative refinement loop (target: {threshold*100:.0f}% satisfaction)")
    print(f"📊 Initial test cases: {len(current_test_cases)}")
    
    while iteration < max_iterations:
        print(f"\n🔄 Iteration {iteration + 1}/{max_iterations}")
        print("=" * 60)
        
        # Step 1: Validation (Observation)
        print(" Step 1: Validating current test cases...")
        try:
            validation_results = validator_function(current_test_cases, acceptance_criteria)
            satisfaction_rate = validation_results['summary']['satisfaction_rate']
            print(f"📊 Current satisfaction rate: {satisfaction_rate:.1%}")
            
            if satisfaction_rate >= threshold:
                print(f"✅ Target satisfaction rate ({threshold*100:.0f}%) achieved!")
                return current_test_cases, satisfaction_rate
                
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            break
        
        # Step 2: Gap Analysis (Reflection)
        print("\n🤔 Step 2: Analyzing gaps...")
        try:
            gap_analysis = analyze_gaps_with_llm(current_test_cases, acceptance_criteria, validation_results)
            print("✅ Gap analysis completed")
            
            # Print gap analysis summary
            missing_criteria = gap_analysis.get('gap_analysis', {}).get('missing_criteria', [])
            weak_coverage = gap_analysis.get('gap_analysis', {}).get('weak_coverage', [])
            
            if missing_criteria:
                print(f"📋 Missing criteria identified: {len(missing_criteria)}")
                for i, criterion in enumerate(missing_criteria[:3], 1):  # Show first 3
                    print(f"   {i}. {criterion.get('criterion', 'N/A')}")
            
            if weak_coverage:
                print(f"📋 Weak coverage identified: {len(weak_coverage)}")
                
        except Exception as e:
            print(f"❌ Gap analysis failed: {e}")
            break
        
        # Step 3: Targeted Test Generation (Action)
        print("\n⚡ Step 3: Generating targeted test cases...")
        try:
            new_test_cases = generate_targeted_test_cases_with_llm(gap_analysis, user_story, knowledge_base)
            print(f"✅ Generated {len(new_test_cases)} targeted test cases")
            
            # Add new test cases to existing ones
            current_test_cases.extend(new_test_cases)
            print(f"📊 Total test cases after iteration: {len(current_test_cases)}")
            
        except Exception as e:
            print(f"❌ Targeted test generation failed: {e}")
            break
        
        iteration += 1
    
    # Final validation
    print(f"\n🔄 Refinement loop completed after {iteration} iterations")
    try:
        final_validation = validator_function(current_test_cases, acceptance_criteria)
        final_satisfaction = final_validation['summary']['satisfaction_rate']
        print(f" Final satisfaction rate: {final_satisfaction:.1%}")
        return current_test_cases, final_satisfaction
    except Exception as e:
        print(f"❌ Final validation failed: {e}")
        return current_test_cases, 0.0

def generate_refinement_report(
    initial_test_cases: List[Dict], 
    final_test_cases: List[Dict], 
    initial_satisfaction: float, 
    final_satisfaction: float,
    iterations: int
) -> str:
    """
    Generate a detailed report of the refinement process.
    """
    
    report = f"""
# Test Case Refinement Report

## Summary
- **Initial Test Cases**: {len(initial_test_cases)}
- **Final Test Cases**: {len(final_test_cases)}
- **Test Cases Added**: {len(final_test_cases) - len(initial_test_cases)}
- **Initial Satisfaction**: {initial_satisfaction:.1%}
- **Final Satisfaction**: {final_satisfaction:.1%}
- **Improvement**: {final_satisfaction - initial_satisfaction:+.1%}
- **Iterations**: {iterations}

## Refinement Process
The test cases were refined through an iterative process using LLM-powered gap analysis and targeted test case generation.

### Key Improvements
- **Gap Analysis**: Identified missing acceptance criteria coverage
- **Targeted Generation**: Created specific test cases for uncovered scenarios
- **Iterative Validation**: Continuously validated improvements

### Final Results
- **Total Test Cases**: {len(final_test_cases)}
- **Satisfaction Rate**: {final_satisfaction:.1%}
- **Coverage**: {'✅ Excellent' if final_satisfaction >= 0.9 else '⚠️ Needs Improvement' if final_satisfaction >= 0.7 else '❌ Poor'}

## New Test Cases Added
"""
    
    new_test_cases = final_test_cases[len(initial_test_cases):]
    for i, test_case in enumerate(new_test_cases, 1):
        report += f"""
### New Test Case {i}
- **Scenario**: {test_case.get('scenario', 'N/A')}
- **Type**: {test_case.get('type', 'N/A')}
- **Targets Criterion**: {test_case.get('targets_criterion', 'N/A')}
- **Steps**: {test_case.get('steps', 'N/A')}
- **Expected**: {test_case.get('expected', 'N/A')}
"""
    
    return report

# Example usage function
def run_refinement_example():
    """
    Example function showing how to use the refinement system.
    """
    
    # Example data
    acceptance_criteria = """
    1. User can view their current profile information including username, email, and account creation date
    2. User can update their email address while maintaining username uniqueness
    3. User can change their password with proper validation of current password
    4. System validates new email format and ensures it's not already in use
    5. System requires re-authentication for sensitive profile changes
    6. System maintains audit trail of profile modifications
    """
    
    initial_test_cases = [
        {
            "scenario": "View Profile Information - Happy Path",
            "steps": "1. Login with valid credentials 2. Navigate to profile page 3. View profile information",
            "expected": "Profile information is displayed correctly",
            "type": "Happy",
            "status": "Pending"
        }
    ]
    
    user_story = "As a registered user, I want to view and update my profile information so that I can keep my account details current and accurate."
    
    knowledge_base = "E-commerce backend with user management, profile updates, authentication, and audit logging capabilities."
    
    # Mock validator function (replace with your actual validator)
    def mock_validator(test_cases, criteria):
        return {
            'summary': {'satisfaction_rate': 0.3},
            'satisfied': test_cases[:1],
            'not_satisfied': test_cases[1:] if len(test_cases) > 1 else []
        }
    
    # Run refinement
    final_cases, final_satisfaction = refine_test_cases_iteratively(
        initial_test_cases, 
        acceptance_criteria, 
        user_story, 
        knowledge_base,
        mock_validator,
        max_iterations=3,
        threshold=0.8
    )
    
    print(f"\n🎉 Refinement completed!")
    print(f"Final satisfaction: {final_satisfaction:.1%}")
    print(f"Total test cases: {len(final_cases)}")

if __name__ == "__main__":
    run_refinement_example()
