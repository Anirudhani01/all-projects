import json
from pathlib import Path
import subprocess
import os
from dotenv import load_dotenv
import re
import requests  # Add this import

# Updated LangChain imports (current structure)
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel  # ✅ BaseModel is from pydantic, not langchain
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback
from typing import List, Optional

# Load environment variables
load_dotenv()

# --- LLM Clients ---
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# --- Conditional Initialization ---
openai_client = None
if os.getenv("OPENAI_API_KEY") and OpenAI:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

gemini_enabled = False
if os.getenv("GOOGLE_API_KEY") and genai:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini_enabled = True

def extract_json_from_text(text: str) -> list:
    """Extract JSON array from text that might contain extra content."""
    if not text or len(text.strip()) == 0:
        return []
    
    print(f"🔍 Analyzing response content: {len(text)} characters")
    
    # Strategy 1: Try direct JSON parsing first
    try:
        parsed = json.loads(text.strip())
        if isinstance(parsed, list) and len(parsed) > 0:
            print(f"✅ Direct JSON parsing successful: {len(parsed)} items")
            return parsed
    except json.JSONDecodeError as e:
        print(f"⚠️ Direct JSON parsing failed: {e}")
    
    # Strategy 2: Look for JSON array markers with better validation
    json_start = text.find('[')
    json_end = text.rfind(']') + 1
    
    if json_start != -1 and json_end != 0:
        json_content = text[json_start:json_end]
        print(f"🔍 Found potential JSON array: {len(json_content)} characters")
        
        try:
            parsed = json.loads(json_content)
            if isinstance(parsed, list) and len(parsed) > 0:
                print(f"✅ JSON array extraction successful: {len(parsed)} items")
                return parsed
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON array parsing failed: {e}")
            
            # Strategy 3: Try to fix common escape character issues
            try:
                # Fix common escape character problems
                fixed_content = json_content
                
                # Fix double-escaped quotes
                fixed_content = fixed_content.replace('\\"', '"')
                fixed_content = fixed_content.replace('\\\\', '\\')
                
                # Fix newlines and tabs
                fixed_content = fixed_content.replace('\\n', '\n')
                fixed_content = fixed_content.replace('\\t', '\t')
                
                parsed = json.loads(fixed_content)
                if isinstance(parsed, list) and len(parsed) > 0:
                    print(f"✅ JSON extraction with escape fixing successful: {len(parsed)} items")
                    return parsed
            except json.JSONDecodeError as e2:
                print(f"⚠️ JSON escape fixing failed: {e2}")
    
    # Strategy 4: Look for JSON object markers (single test case)
    json_obj_start = text.find('{')
    json_obj_end = text.rfind('}') + 1
    
    if json_obj_start != -1 and json_obj_end != 0:
        json_obj_content = text[json_obj_start:json_obj_end]
        print(f"🔍 Found potential JSON object: {len(json_obj_content)} characters")
        
        try:
            parsed = json.loads(json_obj_content)
            if isinstance(parsed, dict):
                print(f"✅ JSON object extraction successful: 1 item")
                return [parsed]
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON object parsing failed: {e}")
    
    # Strategy 5: Look for JSON in code blocks
    code_block_pattern = r'```(?:json)?\s*\n(.*?)\n```'
    code_matches = re.findall(code_block_pattern, text, re.DOTALL)
    
    for match in code_matches:
        print(f"🔍 Found JSON in code block: {len(match)} characters")
        try:
            parsed = json.loads(match.strip())
            if isinstance(parsed, list) and len(parsed) > 0:
                print(f"✅ Code block JSON extraction successful: {len(parsed)} items")
                return parsed
        except json.JSONDecodeError as e:
            print(f"⚠️ Code block JSON parsing failed: {e}")
    
    # Strategy 6: Look for JSON-like content with regex (improved)
    json_like_pattern = r'\{[^{}]*"[^"]*"[^{}]*\}'
    json_like_matches = re.findall(json_like_pattern, text, re.DOTALL)
    
    if json_like_matches:
        print(f"🔍 Found {len(json_like_matches)} JSON-like objects")
        test_cases = []
        
        for match in json_like_matches:
            try:
                # Try to fix the JSON-like content
                fixed_match = match
                # Add missing quotes around keys if needed
                fixed_match = re.sub(r'(\w+):', r'"\1":', fixed_match)
                
                parsed = json.loads(fixed_match)
                if isinstance(parsed, dict):
                    test_cases.append(parsed)
                    print(f"🔍 Found JSON-like content: {len(fixed_match)} characters")
            except json.JSONDecodeError:
                continue
        
        if test_cases:
            print(f"✅ JSON-like extraction successful: {len(test_cases)} items")
            return test_cases
    
    # Strategy 7: If JSON parsing fails, try text extraction
    test_cases = parse_text_output(text)
    if test_cases:
        print(f"📝 Extracted {len(test_cases)} test cases from structured text")
        return test_cases
    
    print("❌ All JSON extraction strategies failed")
    return []

def clean_and_validate_test_cases(test_cases: list) -> list:
    """Clean and validate test case data."""
    cleaned_cases = []
    
    for case in test_cases:
        if isinstance(case, dict):
            cleaned_case = {
                "scenario": str(case.get("scenario", "")).strip(),
                "steps": str(case.get("steps", "")).strip(),
                "expected": str(case.get("expected", "")).strip(),
                "type": str(case.get("type", "")).strip(),
                "status": "Pending"
            }
            
            # Validate required fields
            if (cleaned_case["scenario"] and 
                cleaned_case["steps"] and 
                cleaned_case["expected"] and 
                cleaned_case["type"]):
                cleaned_cases.append(cleaned_case)
    
    return cleaned_cases

# --- Helper: Call LLM dynamically ---
def call_llm(prompt: str, model_name: str = "openai/gpt-oss-20b") -> list:
    """
    Sends the prompt to LLM and returns structured test cases.
    Follows priority: OpenAI -> Gemini -> Local Ollama Server
    """
    
    # Try OpenAI first
    if openai_client:
        try:
            print("⚡ Using OpenAI GPT...")
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Test Case Generator. Generate exactly 6-8 test cases in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            output_text = response.choices[0].message.content
            print(f"📝 OpenAI response length: {len(output_text)} characters")
            
            # Extract and parse JSON
            test_cases = extract_json_from_text(output_text)
            if test_cases:
                cleaned_cases = clean_and_validate_test_cases(test_cases)
                if cleaned_cases:
                    print(f"✅ OpenAI generated {len(cleaned_cases)} valid test cases")
                    return cleaned_cases
            
        except Exception as e:
            print(f"❌ OpenAI call failed: {e}")
    
    # Try Gemini with multiple model names
    if gemini_enabled:
        gemini_models = ["gemini-1.5-flash"]
        
        for gemini_model in gemini_models:
            try:
                print(f"⚡ Using Google Gemini ({gemini_model})...")
                model = genai.GenerativeModel(gemini_model)
                response = model.generate_content(prompt)
                content = response.text
                print(f"📝 Gemini response length: {len(content)} characters")
                
                # Use the improved extract_json_from_text function
                test_cases = extract_json_from_text(content)
                if test_cases:
                    cleaned_cases = clean_and_validate_test_cases(test_cases)
                    if cleaned_cases:
                        print(f"✅ Gemini ({gemini_model}) generated {len(cleaned_cases)} valid test cases")
                        return cleaned_cases
                
                print(f"⚠️ Gemini ({gemini_model}) response parsing failed, trying next model...")
                
            except Exception as e:
                print(f"❌ Gemini ({gemini_model}) call failed: {e}")
                continue
        
        print("⚠️ All Gemini models failed, trying next LLM...")
    
    # Try Local Ollama Server (HTTP API)
    try:
        print(f"⚡ Using Local Ollama Server ({model_name})...")
        
        # Prepare the request payload
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a Test Case Generator. Generate exactly 6-8 test cases in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
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
            print(f"📝 Local Ollama response length: {len(output_text)} characters")
            
            # Extract and parse JSON
            test_cases = extract_json_from_text(output_text)
            if test_cases:
                cleaned_cases = clean_and_validate_test_cases(test_cases)
                if cleaned_cases:
                    print(f"✅ Local Ollama generated {len(cleaned_cases)} valid test cases")
                    return cleaned_cases
            
            # If JSON parsing fails, try text parsing
            test_cases = parse_text_output(output_text)
            if test_cases:
                print(f"✅ Local Ollama generated {len(test_cases)} test cases from text")
                return test_cases
            
        else:
            print(f"❌ Local Ollama server error: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Local Ollama server request timed out (5 minutes)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Local Ollama server connection failed: {e}")
    except Exception as e:
        print(f"❌ Local Ollama call failed: {e}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
    
    print("❌ All LLM calls failed. No test cases generated.")
    return []

# --- Helper: Parse plain text LLM output into list of dicts ---
def parse_text_output(text: str) -> list:
    """
    Converts plain text from LLM into structured test case dicts.
    Expects each test case separated by '---' with 4 lines: scenario, steps, expected, type
    """
    test_cases = []
    for block in text.split("---"):
        lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
        if len(lines) >= 4:
            test_cases.append({
                "scenario": lines[0],
                "steps": lines[1],
                "expected": lines[2],
                "type": lines[3],
                "status": "Pending"
            })
    return test_cases

# --- Main Function: Generate Test Cases ---
def generate_test_cases(user_story: str, analysis: str, template_path: str, knowledge_base_path: str) -> list:
    """
    Main function that follows the intended flow:
    1. Load knowledge base
    2. Load prompt template
    3. Combine user story + analysis + knowledge base + prompts
    4. Send to LLM for test case generation
    5. Return structured test cases
    """
    
    # --- Load knowledge base (domain context) ---
    kb_content = ""
    kb_file = Path(knowledge_base_path)
    if kb_file.exists():
        try:
            with open(kb_file, "r", encoding="utf-8") as f:
                kb_json = json.load(f)
            kb_content = json.dumps(kb_json, indent=2)
            print(f"✅ Knowledge base loaded: {kb_file}")
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            kb_content = "Domain knowledge is not available."
    else:
        print(f"⚠️ Knowledge base not found: {kb_file}")
        kb_content = "Domain knowledge is not available."

    # --- Load prompt template ---
    prompt_template = ""
    template_folder = Path(template_path)
    if template_folder.exists():
        # SPECIFICALLY LOAD test_case_generation_prompt.txt
        target_template = template_folder / "test_case_generation_prompt.txt"
        if target_template.exists():
            try:
                with open(target_template, "r", encoding="utf-8") as f:
                    prompt_template = f.read()
                print(f"✅ Target template loaded: {target_template}")
            except Exception as e:
                print(f"❌ Error loading target template: {e}")
                prompt_template = ""
        
        # Fallback if target template not found
        if not prompt_template:
            print(f"⚠️ Target template not found: {target_template}")
            template_files = list(template_folder.glob("*.txt"))
            if template_files:
                try:
                    with open(template_files[0], "r", encoding="utf-8") as f:
                        prompt_template = f.read()
                    print(f"⚠️ Fallback template loaded: {template_files[0]}")
                except Exception as e:
                    print(f"❌ Error loading fallback template: {e}")
                    prompt_template = "Generate multiple test cases (happy, negative, edge) in structured format."
            else:
                print("⚠️ No prompt template files found")
                prompt_template = "Generate multiple test cases (happy, negative, edge) in structured format."
    else:
        print(f"⚠️ Prompt template folder not found: {template_folder}")
        prompt_template = "Generate multiple test cases (happy, negative, edge) in structured format."

    # --- Combine everything into comprehensive LLM prompt ---
    # --- Comprehensive Test Case Generation Prompt ---
    llm_prompt = f"""
You are acting as a Senior Software QA Engineer specializing in test case design for enterprise applications. 
Your goal is to generate exhaustive, production-ready, and domain-aware test cases with the highest level of quality.

=== DOMAIN KNOWLEDGE (from source/project code) ===
{kb_content}

=== USER STORY ===
{user_story}

=== USER STORY ANALYSIS ===
{analysis}

=== INSTRUCTIONS ===
{prompt_template}

CRITICAL REQUIREMENTS:
- Generate ALL meaningful test cases covering every possible scenario related to this user story
- Include different types: Happy Path, Negative Cases, Edge Cases, and boundary conditions
- Make test cases SPECIFIC, DETAILED, and ACTIONABLE
- Use the domain knowledge to make scenarios realistic
- Return ONLY a valid JSON array (no extra text, comments, or explanations)
- Each test case object must include:
    - "scenario": clear description of what is being tested
    - "steps": step-by-step instructions
    - "expected": expected outcome
    - "type": Happy/Negative/Edge
    - "status": Pending

=== OUTPUT FORMAT ===
Return a JSON array of test case objects. Each test case must have:
{{
  "scenario": "Clear, descriptive test scenario",
  "steps": "Detailed step-by-step test execution",
  "expected": "Expected result or outcome",
  "type": "Happy|Negative|Edge|Security|Performance",
  "status": "Pending"
}}

=== EXAMPLE ===
[
  {{
    "scenario": "User successfully adds a product to cart",
    "steps": "1. Navigate to product page 2. Select product 3. Click 'Add to Cart' 4. Verify cart icon shows updated count",
    "expected": "Product is successfully added to the cart and cart count increases by 1",
    "type": "Happy",
    "status": "Pending"
  }}
]

=== FINAL INSTRUCTION ===
Now generate the COMPLETE and EXHAUSTIVE list of test cases for the given user story, 
strictly following the above rules and JSON format.
"""

    print("\n🚀 Sending comprehensive prompt to LLM...")
    print(f"📝 Prompt length: {len(llm_prompt)} characters")
    
    # --- Call LLM dynamically ---
    test_cases = call_llm(llm_prompt)

    # --- Final validation ---
    if test_cases:
        print(f"✅ Final result: {len(test_cases)} test cases generated")
        for i, tc in enumerate(test_cases, 1):
            print(f"   TC{i}: {tc.get('scenario', 'N/A')[:60]}...")
    else:
        print("❌ No test cases generated")
    
    return test_cases
