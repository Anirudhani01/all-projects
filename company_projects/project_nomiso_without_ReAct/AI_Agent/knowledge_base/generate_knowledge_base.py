import os
import json
import sys
import datetime
from pathlib import Path
from typing import Dict, List, Any
import requests  # Add this import

# Fix the import path: go up one level from knowledge_base to AI_Agent, then into test_case_generator
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'test_case_generator'))

# Import the specific functions we need
try:
    from test_case import openai_client, gemini_enabled, genai
except ImportError:
    print("❌ Could not import LLM clients from test_case.py")
    sys.exit(1)

def call_llm_for_knowledge_base(prompt: str) -> str:
    """
    Dedicated LLM function for knowledge base generation.
    Tries OpenAI -> Gemini -> Local Ollama Server, but returns the first successful response.
    """
    
    # Try OpenAI first
    if openai_client:
        try:
            print("⚡ Using OpenAI GPT...")
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Software Architect and Business Analyst. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            output_text = response.choices[0].message.content
            print(f"📝 OpenAI response length: {len(output_text)} characters")
            return output_text
            
        except Exception as e:
            print(f"❌ OpenAI call failed: {e}")
    
    # Try Gemini second
    if gemini_enabled:
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
                {"role": "system", "content": "You are a Software Architect and Business Analyst. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
            "stream": False
        }
        
        # Make the HTTP request to your local Ollama server with increased timeout
        response = requests.post(
            "http://192.168.0.155:1234/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=300  # Increased to 5 minutes
        )
        
        if response.status_code == 200:
            result = response.json()
            output_text = result["choices"][0]["message"]["content"]
            print(f"📝 Local Ollama response length: {len(output_text)} characters")
            return output_text
        else:
            print(f"❌ Local Ollama server error: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Local Ollama server request timed out (5 minutes)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Local Ollama server connection failed: {e}")
    except Exception as e:
        print(f"❌ Local Ollama call failed: {e}")
    
    raise Exception("All LLM calls failed")

def analyze_file_with_llm(file_path: str, file_content: str) -> Dict[str, Any]:
    """
    Use LLM to analyze a single Python file and extract comprehensive information for knowledge base.
    """
    prompt = f"""
    You are a software architect and business analyst. Analyze this Python file and extract comprehensive information for building a knowledge base.

    FILE PATH: {file_path}
    
    CODE CONTENT:
    {file_content}
    
    TASK: Analyze this Python file and provide a structured analysis covering:
    
    1. **Business Purpose**: What business functionality does this file provide?
    2. **Architecture**: What design patterns and architectural elements are used?
    3. **Key Components**: 
       - Classes and their purposes
       - Functions and their business logic
       - Data models and structures
    4. **Dependencies**: What external libraries and modules are imported?
    5. **Business Rules**: What validation rules, constraints, and business logic exist?
    6. **Security Features**: Authentication, authorization, data protection?
    7. **Error Handling**: What error scenarios are handled?
    8. **Domain Knowledge**: What business domain concepts and entities are represented?
    
    CRITICAL: You must return ONLY valid JSON. No explanations, no markdown, no extra text.
    The response must start with {{ and end with }}.
    
    OUTPUT FORMAT:
    {{
        "filename": "filename.py",
        "file_path": "path/to/file",
        "business_purpose": "Description of what this file does",
        "architecture": "Description of architectural patterns",
        "classes": [
            {{
                "name": "ClassName",
                "purpose": "What this class represents",
                "business_logic": "Business functionality",
                "fields": ["field1", "field2"],
                "validation_rules": ["rule1", "rule2"]
            }}
        ],
        "functions": [
            {{
                "name": "function_name",
                "purpose": "What this function does",
                "business_logic": "Business functionality",
                "parameters": ["param1", "param2"],
                "return_value": "What it returns",
                "error_handling": ["error1", "error2"]
            }}
        ],
        "dependencies": ["library1", "module2"],
        "business_rules": ["rule1", "rule2"],
        "security_features": ["feature1", "feature2"],
        "error_scenarios": ["scenario1", "scenario2"],
        "domain_concepts": ["concept1", "concept2"]
    }}
    """
    
    # Call our dedicated LLM function
    response = call_llm_for_knowledge_base(prompt)
    
    # Parse the response
    try:
        # Try direct JSON parsing first
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from the response if it's wrapped in other text
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            json_content = response[json_start:json_end]
            try:
                return json.loads(json_content)
            except json.JSONDecodeError as e:
                raise Exception(f"LLM analysis failed for {file_path}: Invalid JSON response. Error: {e}")
        else:
            raise Exception(f"LLM analysis failed for {file_path}: No JSON found in response")

def analyze_project_structure_with_llm(src_folder: str, file_analyses: List[Dict]) -> Dict[str, Any]:
    """
    Use LLM to analyze the entire project structure and create a comprehensive knowledge base.
    """
    # Create a summary of all analyzed files
    file_summary = []
    for analysis in file_analyses:
        file_summary.append({
            "filename": analysis.get("filename", "Unknown"),
            "business_purpose": analysis.get("business_purpose", "Unknown"),
            "key_components": len(analysis.get("classes", [])) + len(analysis.get("functions", []))
        })
    
    prompt = f"""
    You are a senior software architect. Analyze this entire Python project and create a comprehensive knowledge base.

    PROJECT OVERVIEW:
    Source folder: {src_folder}
    Total files analyzed: {len(file_analyses)}
    
    INDIVIDUAL FILE ANALYSES:
    {json.dumps(file_summary, indent=2)}
    
    TASK: Create a comprehensive project-level knowledge base that includes:
    
    1. **Project Overview**: High-level business purpose and domain
    2. **Architecture Summary**: Overall system design and patterns
    3. **Business Domain**: What business problems does this solve?
    4. **Key Components**: Major modules and their relationships
    5. **Data Flow**: How data moves through the system
    6. **Security Architecture**: Authentication, authorization, data protection
    7. **Integration Points**: External services, APIs, databases
    8. **Business Rules**: Core business logic and constraints
    9. **Domain Knowledge**: Business concepts, entities, and relationships
    10. **Deployment Considerations**: Infrastructure and deployment needs
    
    CRITICAL: You must return ONLY valid JSON. No explanations, no markdown, no extra text.
    The response must start with {{ and end with }}.
    
    OUTPUT FORMAT:
    {{
        "project_overview": "High-level description",
        "business_domain": "What business domain this serves",
        "architecture_summary": "System design overview",
        "key_components": [
            {{
                "name": "ComponentName",
                "purpose": "What it does",
                "responsibilities": ["resp1", "resp2"]
            }}
        ],
        "data_flow": "How data moves through the system",
        "security_architecture": ["security1", "security2"],
        "integration_points": ["integration1", "integration2"],
        "business_rules": ["rule1", "rule2"],
        "domain_knowledge": ["concept1", "concept2"],
        "deployment_considerations": ["consideration1", "consideration2"],
        "file_analyses": {file_analyses}
    }}
    """
    
    # Call our dedicated LLM function
    response = call_llm_for_knowledge_base(prompt)
    
    # Parse the response
    try:
        # Try direct JSON parsing first
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from the response if it's wrapped in other text
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            json_content = response[json_start:json_end]
            try:
                return json.loads(json_content)
            except json.JSONDecodeError as e:
                raise Exception(f"Project-level LLM analysis failed: Invalid JSON response. Error: {e}")
        else:
            raise Exception("Project-level LLM analysis failed: No JSON found in response")

def get_llm_info() -> str:
    """
    Get information about which LLM is being used by checking environment variables.
    """
    try:
        # Check environment variables to see which LLM is configured
        if os.getenv("OPENAI_API_KEY"):
            return "OpenAI GPT (Configured)"
        elif os.getenv("GOOGLE_API_KEY"):
            return "Google Gemini (Configured)"
        else:
            return "Ollama (Local - Fallback)"
    except Exception as e:
        return f"LLM detection failed: {e}"

def generate_knowledge_base(source_folder: str, output_file: str = "knowledge_base.json"):
    """
    Generate comprehensive knowledge base using LLM analysis ONLY.
    """
    # Get LLM information
    llm_name = get_llm_info()
    
    print(f"🚀 Starting LLM-powered knowledge base generation...")
    print(f"🤖 Using LLM: {llm_name}")
    print(f"📁 Source folder: {source_folder}")
    
    # Step 1: Analyze individual files with LLM
    print(f"\n📋 Step 1: Analyzing individual files with {llm_name}...")
    file_analyses = []
    
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                print(f"  🔍 Analyzing: {file}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                    
                    # Analyze file with LLM - must succeed
                    analysis = analyze_file_with_llm(file_path, file_content)
                    file_analyses.append(analysis)
                    print(f"    ✅ Completed: {file}")
                    
                except Exception as e:
                    print(f"    ❌ LLM analysis failed for {file}: {e}")
                    # Stop execution if LLM fails - no fallbacks
                    raise Exception(f"LLM analysis failed for {file}. Cannot proceed without LLM analysis.")
    
    print(f"\n✅ File analysis completed: {len(file_analyses)} files processed")
    
    # Step 2: Generate project-level knowledge base with LLM
    print(f"\n Step 2: Generating project-level knowledge base with {llm_name}...")
    try:
        project_knowledge_base = analyze_project_structure_with_llm(source_folder, file_analyses)
        print("✅ Project-level analysis completed")
    except Exception as e:
        print(f"❌ Project-level LLM analysis failed: {e}")
        # Stop execution if LLM fails - no fallbacks
        raise Exception(f"Project-level LLM analysis failed. Cannot proceed without LLM analysis.")
    
    # Step 3: Save results
    print(f"\n💾 Step 3: Saving knowledge base...")
    try:
        # Add LLM information to the knowledge base
        project_knowledge_base["llm_generation_info"] = {
            "llm_used": llm_name,
            "generation_timestamp": str(datetime.datetime.now()),
            "total_files_analyzed": len(file_analyses),
            "generation_method": "LLM-only analysis (no fallbacks)",
            "purpose": "Knowledge base for understanding project structure and business logic"
        }
    
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(project_knowledge_base, f, indent=2)
    
        print(f"✅ Knowledge base saved: {output_file}")
    
    #Print summary
        print(f"\n📊 KNOWLEDGE BASE SUMMARY:")
        print(f"   - LLM Used: {llm_name}")
        print(f"   - Total files analyzed: {len(file_analyses)}")
        print(f"   - Project domain: {project_knowledge_base.get('business_domain', 'Unknown')}")
        print(f"   - Key components: {len(project_knowledge_base.get('key_components', []))}")
        print(f"   - Security features: {len(project_knowledge_base.get('security_architecture', []))}")
        print(f"   - Business rules: {len(project_knowledge_base.get('business_rules', []))}")
        print(f"   - Domain concepts: {len(project_knowledge_base.get('domain_knowledge', []))}")
        
    except Exception as e:
        print(f"❌ Error saving knowledge base: {e}")
        raise

if __name__ == "__main__":
    # Fix the path: go up two levels from knowledge_base to reach root, then into src
    source_path = "../../src"
    
    if not os.path.exists(source_path):
        print(f"❌ Source folder not found: {source_path}")
        print("Please ensure the src folder exists relative to this script.")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for: {os.path.abspath(source_path)}")
        exit(1)
    
    try:
        generate_knowledge_base(source_path, "knowledge_base.json")
        print("\n🎉 Knowledge base generation completed successfully!")
        print("📚 This knowledge base contains project structure, business logic, and domain knowledge.")
        print("🔍 Use it to understand your codebase and inform other AI processes.")
    except Exception as e:
        print(f"\n❌ Knowledge base generation failed: {e}")
        print("The system requires LLM analysis to work. Please check your LLM configuration.")
        exit(1)
