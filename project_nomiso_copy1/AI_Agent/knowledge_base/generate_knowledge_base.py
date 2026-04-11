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
    Includes domain detection and categorization.
    """
    prompt = f"""
    You are a software architect and business analyst with expertise in domain-driven design. Analyze this Python file and extract COMPREHENSIVE information for building a detailed knowledge base.

    FILE PATH: {file_path}
    
    CODE CONTENT:
    {file_content}
    
    TASK: Analyze this Python file and provide a DETAILED structured analysis covering:
    
    1. **Domain Detection**: First, identify which business domain(s) this file belongs to:
       - Authentication & Authorization
       - User Management
       - Employee Management
       - Image/File Management
       - Database Operations
       - API/Web Services
       - Configuration Management
       - Testing & Validation
       - Data Processing
       - Business Logic
       - Security
       - Other (specify)
    
    2. **Business Purpose**: What business functionality does this file provide?
    3. **Architecture**: What design patterns and architectural elements are used?
    4. **Key Components**: 
       - Classes and their purposes (with detailed field analysis)
       - Functions and their business logic (with parameter details)
       - Data models and structures
       - API endpoints and routes
       - Database models and relationships
    5. **Dependencies**: What external libraries and modules are imported?
    6. **Business Rules**: What validation rules, constraints, and business logic exist?
    7. **Security Features**: Authentication, authorization, data protection?
    8. **Error Handling**: What error scenarios are handled?
    9. **Domain Knowledge**: What business domain concepts and entities are represented?
    10. **API Endpoints**: What REST endpoints are defined?
    11. **Database Operations**: What database operations are performed?
    12. **Configuration**: What configuration settings are used?
    13. **Testing**: What test cases or testing logic exists?
    14. **Domain-Specific Analysis**: Based on the identified domain, provide domain-specific insights
    
    IMPORTANT: Extract ALL details from the source code. Include specific function names, class names, 
    parameter types, return values, error handling patterns, business logic flows, and any other 
    implementation details that would help understand the complete functionality.
    
    CRITICAL: You must return ONLY valid JSON. No explanations, no markdown, no extra text.
    The response must start with {{ and end with }}.
    
    IMPORTANT: Your response will be parsed as JSON. Do not include any text before or after the JSON.
    Do not include markdown code blocks, explanations, or any other text.
    Start your response immediately with {{ and end with }}.
    
    OUTPUT FORMAT:
    {{
        "filename": "filename.py",
        "file_path": "path/to/file",
        "primary_domain": "Main business domain this file belongs to",
        "secondary_domains": ["domain2", "domain3"],
        "domain_confidence": 0.95,
        "business_purpose": "Detailed description of what this file does",
        "architecture": "Detailed description of architectural patterns and design",
        "classes": [
            {{
                "name": "ClassName",
                "purpose": "What this class represents",
                "business_logic": "Detailed business functionality",
                "domain_relevance": "How this class relates to the identified domain",
                "fields": ["field1", "field2"],
                "methods": ["method1", "method2"],
                "validation_rules": ["rule1", "rule2"],
                "inheritance": "parent_class",
                "relationships": ["related_class1", "related_class2"]
            }}
        ],
        "functions": [
            {{
                "name": "function_name",
                "purpose": "What this function does",
                "business_logic": "Detailed business functionality",
                "domain_relevance": "How this function relates to the identified domain",
                "parameters": ["param1: type", "param2: type"],
                "return_value": "What it returns and type",
                "error_handling": ["error1", "error2"],
                "dependencies": ["dep1", "dep2"]
            }}
        ],
        "api_endpoints": [
            {{
                "path": "/api/endpoint",
                "method": "GET/POST/PUT/DELETE",
                "purpose": "What this endpoint does",
                "domain_relevance": "How this endpoint relates to the identified domain",
                "parameters": ["param1", "param2"],
                "authentication": "required/optional",
                "business_logic": "What business logic it implements"
            }}
        ],
        "database_operations": [
            {{
                "operation": "CREATE/READ/UPDATE/DELETE",
                "table": "table_name",
                "purpose": "What this operation does",
                "domain_relevance": "How this operation relates to the identified domain",
                "business_logic": "Business rules applied"
            }}
        ],
        "dependencies": ["library1", "module2"],
        "business_rules": ["rule1", "rule2"],
        "security_features": ["feature1", "feature2"],
        "error_scenarios": ["scenario1", "scenario2"],
        "domain_concepts": ["concept1", "concept2"],
        "configuration": ["config1", "config2"],
        "testing": ["test1", "test2"],
        "domain_specific_insights": {{
            "domain_patterns": ["pattern1", "pattern2"],
            "domain_best_practices": ["practice1", "practice2"],
            "domain_constraints": ["constraint1", "constraint2"],
            "domain_relationships": ["relationship1", "relationship2"]
        }}
    }}
    """
    
    # Call our dedicated LLM function
    response = call_llm_for_knowledge_base(prompt)
    
    # Check if response is too large and might cause JSON parsing issues
    if len(response) > 25000:  # 25KB response threshold
        print(f"    ⚠️ Large response detected ({len(response)} chars), retrying with simplified analysis...")
        return analyze_large_file_with_llm(file_path, file_content)
    
    # Clean the response to remove any markdown formatting or extra text
    response = response.strip()
    
    # Remove markdown code blocks if present
    if response.startswith("```json"):
        response = response[7:]  # Remove ```json
    if response.startswith("```"):
        response = response[3:]   # Remove ```
    if response.endswith("```"):
        response = response[:-3]  # Remove trailing ```
    
    response = response.strip()
    
    # Parse the response - LLM must provide valid JSON
    try:
        # Try direct JSON parsing first
        return json.loads(response)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed for {file_path}: {e}")
        # Try to extract JSON from the response if it's wrapped in other text
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            json_content = response[json_start:json_end]
            try:
                return json.loads(json_content)
            except json.JSONDecodeError as e2:
                print(f"❌ JSON extraction also failed for {file_path}: {e2}")
                # LLM must provide valid JSON - no fallbacks
                raise Exception(f"LLM analysis failed for {file_path}: Invalid JSON response. LLM must provide valid JSON. Error: {e2}")
        else:
            raise Exception(f"LLM analysis failed for {file_path}: No JSON found in response. LLM must provide valid JSON.")

def analyze_project_structure_with_llm(src_folder: str, file_analyses: List[Dict]) -> Dict[str, Any]:
    """
    Use LLM to analyze the entire project structure and create a comprehensive knowledge base organized by domains.
    """
    # Create a domain-organized summary for the LLM
    domain_summary = {}
    file_summary = []
    
    for analysis in file_analyses:
        primary_domain = analysis.get("primary_domain", "Unknown")
        secondary_domains = analysis.get("secondary_domains", [])
        
        # Add to domain summary
        if primary_domain not in domain_summary:
            domain_summary[primary_domain] = {
                "files": [],
                "total_components": 0,
                "total_endpoints": 0,
                "total_db_operations": 0
            }
        
        domain_summary[primary_domain]["files"].append(analysis.get("filename", "Unknown"))
        domain_summary[primary_domain]["total_components"] += len(analysis.get("classes", [])) + len(analysis.get("functions", []))
        domain_summary[primary_domain]["total_endpoints"] += len(analysis.get("api_endpoints", []))
        domain_summary[primary_domain]["total_db_operations"] += len(analysis.get("database_operations", []))
        
        # Add to file summary
        file_summary.append({
            "filename": analysis.get("filename", "Unknown"),
            "primary_domain": primary_domain,
            "secondary_domains": secondary_domains,
            "business_purpose": analysis.get("business_purpose", "Unknown"),
            "key_components": len(analysis.get("classes", [])) + len(analysis.get("functions", [])),
            "api_endpoints": len(analysis.get("api_endpoints", [])),
            "database_operations": len(analysis.get("database_operations", []))
        })
    
    prompt = f"""
    You are a senior software architect and business analyst with expertise in domain-driven design. Analyze this Python project and create a comprehensive knowledge base organized by business domains.

    PROJECT OVERVIEW:
    Source folder: {src_folder}
    Total files analyzed: {len(file_analyses)}
    
    DOMAIN ORGANIZATION:
    {json.dumps(domain_summary, indent=2)}
    
    FILE SUMMARY WITH DOMAINS:
    {json.dumps(file_summary, indent=2)}
    
    TASK: Create a comprehensive project-level knowledge base that includes:
    
    1. **Project Overview**: High-level business purpose and domain
    2. **Architecture Summary**: Overall system design and patterns
    3. **Business Domain**: What business problems does this solve?
    4. **Domain Architecture**: How different domains interact and relate
    5. **Key Components**: Major modules organized by domain
    6. **Data Flow**: How data moves through the system across domains
    7. **Security Architecture**: Authentication, authorization, data protection
    8. **Integration Points**: External services, APIs, databases
    9. **Business Rules**: Core business logic and constraints
    10. **Domain Knowledge**: Business concepts, entities, and relationships
    11. **Deployment Considerations**: Infrastructure and deployment needs
    12. **Domain Relationships**: How different domains depend on each other
    
    CRITICAL: You must return ONLY valid JSON. No explanations, no markdown, no extra text.
    The response must start with {{ and end with }}.
    
    OUTPUT FORMAT:
    {{
        "project_overview": "High-level description",
        "business_domain": "What business domain this serves",
        "architecture_summary": "System design overview",
        "domain_architecture": {{
            "primary_domains": ["domain1", "domain2"],
            "domain_interactions": [
                {{
                    "from_domain": "domain1",
                    "to_domain": "domain2",
                    "interaction_type": "dependency/communication/data_flow",
                    "description": "How they interact"
                }}
            ]
        }},
        "key_components": [
            {{
                "name": "ComponentName",
                "domain": "domain_name",
                "purpose": "What it does",
                "responsibilities": ["resp1", "resp2"]
            }}
        ],
        "data_flow": "How data moves through the system across domains",
        "security_architecture": ["security1", "security2"],
        "integration_points": ["integration1", "integration2"],
        "business_rules": ["rule1", "rule2"],
        "domain_knowledge": ["concept1", "concept2"],
        "deployment_considerations": ["consideration1", "consideration2"],
        "domain_relationships": [
            {{
                "domain1": "domain_name",
                "domain2": "domain_name",
                "relationship_type": "dependency/collaboration/aggregation",
                "description": "How they relate"
            }}
        ]
    }}
    """
    
    # Call our dedicated LLM function
    response = call_llm_for_knowledge_base(prompt)
    
    # Clean the response to remove any markdown formatting or extra text
    response = response.strip()
    
    # Remove markdown code blocks if present
    if response.startswith("```json"):
        response = response[7:]  # Remove ```json
    if response.startswith("```"):
        response = response[3:]   # Remove ```
    if response.endswith("```"):
        response = response[:-3]  # Remove trailing ```
    
    response = response.strip()
    
    # Parse the response - LLM must provide valid JSON
    try:
        # Try direct JSON parsing first
        return json.loads(response)
    except json.JSONDecodeError as e:
        print(f"❌ Project-level JSON parsing failed: {e}")
        # Try to extract JSON from the response if it's wrapped in other text
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            json_content = response[json_start:json_end]
            try:
                return json.loads(json_content)
            except json.JSONDecodeError as e2:
                print(f"❌ Project-level JSON extraction also failed: {e2}")
                # LLM must provide valid JSON - no fallbacks
                raise Exception(f"Project-level LLM analysis failed: Invalid JSON response. LLM must provide valid JSON. Error: {e2}")
        else:
            raise Exception("Project-level LLM analysis failed: No JSON found in response. LLM must provide valid JSON.")

def analyze_large_file_with_llm(file_path: str, file_content: str) -> Dict[str, Any]:
    """
    Analyze large files with a simplified prompt to avoid JSON parsing issues.
    """
    # Take first 20KB and last 5KB of the file for analysis - smaller sample for better JSON
    content_length = len(file_content)
    if content_length > 25000:
        # For very large files, analyze beginning and end
        beginning = file_content[:20000]
        ending = file_content[-5000:]
        sample_content = f"BEGINNING OF FILE:\n{beginning}\n\n... [MIDDLE SECTION OMITTED] ...\n\nEND OF FILE:\n{ending}"
    else:
        sample_content = file_content
    
    prompt = f"""
    You are a software architect analyzing a large Python file. Provide a CONCISE analysis focusing on key components.

    FILE PATH: {file_path}
    FILE SIZE: {content_length} characters
    
    CODE CONTENT (SAMPLE):
    {sample_content}
    
    TASK: Provide a CONCISE analysis covering:
    1. **Primary Domain**: What business domain does this file belong to?
    2. **Business Purpose**: What does this file do?
    3. **Key Components**: Main classes and functions (names only)
    4. **API Endpoints**: Main endpoints if any
    5. **Dependencies**: Key imports
    
    CRITICAL: Return ONLY valid JSON. Keep response SHORT and CONCISE to avoid parsing errors.
    Use brief descriptions and minimal arrays.
    
    OUTPUT FORMAT:
    {{
        "filename": "filename.py",
        "file_path": "path/to/file",
        "primary_domain": "Main domain",
        "secondary_domains": [],
        "domain_confidence": 0.8,
        "business_purpose": "Brief description",
        "architecture": "Brief description",
        "classes": [{{"name": "ClassName", "purpose": "Brief purpose"}}],
        "functions": [{{"name": "function_name", "purpose": "Brief purpose"}}],
        "api_endpoints": [{{"path": "/api/endpoint", "method": "GET"}}],
        "database_operations": [],
        "dependencies": ["dep1", "dep2"],
        "business_rules": [],
        "security_features": [],
        "error_scenarios": [],
        "domain_concepts": [],
        "configuration": [],
        "testing": [],
        "domain_specific_insights": {{"domain_patterns": [], "domain_best_practices": [], "domain_constraints": [], "domain_relationships": []}},
        "analysis_note": "Simplified analysis due to large file size"
    }}
    """
    
    response = call_llm_for_knowledge_base(prompt)
    
    # Clean the response to remove any markdown formatting or extra text
    response = response.strip()
    
    # Remove markdown code blocks if present
    if response.startswith("```json"):
        response = response[7:]  # Remove ```json
    if response.startswith("```"):
        response = response[3:]   # Remove ```
    if response.endswith("```"):
        response = response[:-3]  # Remove trailing ```
    
    response = response.strip()
    
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        print(f"❌ Large file analysis failed: {e}")
        # LLM must provide valid JSON - no fallbacks
        raise Exception(f"Large file LLM analysis failed for {file_path}: Invalid JSON response. LLM must provide valid JSON. Error: {e}")



def organize_by_domain(file_analyses: List[Dict]) -> Dict[str, Any]:
    """
    Organize file analyses by their primary domains for better knowledge base structure.
    """
    domain_organization = {}
    
    for analysis in file_analyses:
        primary_domain = analysis.get("primary_domain", "Unknown")
        secondary_domains = analysis.get("secondary_domains", [])
        
        # Initialize domain if not exists
        if primary_domain not in domain_organization:
            domain_organization[primary_domain] = {
                "domain_info": {
                    "name": primary_domain,
                    "description": f"Domain for {primary_domain} related functionality",
                    "file_count": 0,
                    "total_components": 0,
                    "total_endpoints": 0,
                    "total_db_operations": 0
                },
                "files": [],
                "components": {
                    "classes": [],
                    "functions": [],
                    "api_endpoints": [],
                    "database_operations": []
                },
                "domain_concepts": set(),
                "business_rules": set(),
                "security_features": set(),
                "dependencies": set()
            }
        
        # Update domain statistics
        domain_org = domain_organization[primary_domain]
        domain_org["domain_info"]["file_count"] += 1
        domain_org["domain_info"]["total_components"] += len(analysis.get("classes", [])) + len(analysis.get("functions", []))
        domain_org["domain_info"]["total_endpoints"] += len(analysis.get("api_endpoints", []))
        domain_org["domain_info"]["total_db_operations"] += len(analysis.get("database_operations", []))
        
        # Add file to domain
        domain_org["files"].append({
            "filename": analysis.get("filename", "Unknown"),
            "file_path": analysis.get("file_path", "Unknown"),
            "business_purpose": analysis.get("business_purpose", "Unknown"),
            "secondary_domains": secondary_domains,
            "domain_confidence": analysis.get("domain_confidence", 0.0)
        })
        
        # Add components to domain
        domain_org["components"]["classes"].extend(analysis.get("classes", []))
        domain_org["components"]["functions"].extend(analysis.get("functions", []))
        domain_org["components"]["api_endpoints"].extend(analysis.get("api_endpoints", []))
        domain_org["components"]["database_operations"].extend(analysis.get("database_operations", []))
        
        # Add domain concepts, business rules, security features, and dependencies
        domain_org["domain_concepts"].update(analysis.get("domain_concepts", []))
        domain_org["business_rules"].update(analysis.get("business_rules", []))
        domain_org["security_features"].update(analysis.get("security_features", []))
        domain_org["dependencies"].update(analysis.get("dependencies", []))
    
    # Convert sets to lists for JSON serialization
    for domain_name, domain_data in domain_organization.items():
        domain_data["domain_concepts"] = list(domain_data["domain_concepts"])
        domain_data["business_rules"] = list(domain_data["business_rules"])
        domain_data["security_features"] = list(domain_data["security_features"])
        domain_data["dependencies"] = list(domain_data["dependencies"])
    
    return domain_organization

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
                    
                    # Check if file is too large and might cause JSON parsing issues
                    if len(file_content) > 15000:  # 15KB threshold - reduced for better JSON generation
                        print(f"    ⚠️ Large file detected ({len(file_content)} chars), using simplified analysis...")
                        analysis = analyze_large_file_with_llm(file_path, file_content)
                    else:
                        # Analyze file with LLM - must succeed
                        analysis = analyze_file_with_llm(file_path, file_content)
                    
                    file_analyses.append(analysis)
                    print(f"    ✅ Completed: {file}")
                    
                except Exception as e:
                    print(f"    ❌ LLM analysis failed for {file}: {e}")
                    # LLM must provide valid analysis - no fallbacks
                    raise Exception(f"LLM analysis failed for {file}. Cannot proceed without LLM analysis.")
    
    print(f"\n✅ File analysis completed: {len(file_analyses)} files processed")
    
    # Step 2: Generate project-level knowledge base with LLM
    print(f"\n Step 2: Generating project-level knowledge base with {llm_name}...")
    try:
        project_knowledge_base = analyze_project_structure_with_llm(source_folder, file_analyses)
        print("✅ Project-level analysis completed")
    except Exception as e:
        print(f"❌ Project-level LLM analysis failed: {e}")
        # LLM must provide valid analysis - no fallbacks
        raise Exception(f"Project-level LLM analysis failed. Cannot proceed without LLM analysis.")
    
    # Step 3: Add detailed file analyses to the knowledge base
    print(f"\n📋 Step 3: Adding detailed file analyses...")
    project_knowledge_base["file_analyses"] = file_analyses
    print(f"✅ Added {len(file_analyses)} detailed file analyses")
    
    # Step 3.5: Organize file analyses by domain
    print(f"\n🏗️ Step 3.5: Organizing knowledge base by domains...")
    domain_organized_analyses = organize_by_domain(file_analyses)
    project_knowledge_base["domain_organized_analyses"] = domain_organized_analyses
    print(f"✅ Organized analyses into {len(domain_organized_analyses)} domains")
    
    # Step 4: Save results
    print(f"\n💾 Step 4: Saving knowledge base...")
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
    
        # Print summary
        print(f"\n📊 KNOWLEDGE BASE SUMMARY:")
        print(f"   - LLM Used: {llm_name}")
        print(f"   - Total files analyzed: {len(file_analyses)}")
        print(f"   - Project domain: {project_knowledge_base.get('business_domain', 'Unknown')}")
        print(f"   - Key components: {len(project_knowledge_base.get('key_components', []))}")
        print(f"   - Security features: {len(project_knowledge_base.get('security_architecture', []))}")
        print(f"   - Business rules: {len(project_knowledge_base.get('business_rules', []))}")
        print(f"   - Domain concepts: {len(project_knowledge_base.get('domain_knowledge', []))}")
        
        # Print domain organization summary
        domain_org = project_knowledge_base.get('domain_organized_analyses', {})
        print(f"\n🏗️ DOMAIN ORGANIZATION:")
        for domain_name, domain_data in domain_org.items():
            domain_info = domain_data.get('domain_info', {})
            print(f"   - {domain_name}: {domain_info.get('file_count', 0)} files, {domain_info.get('total_components', 0)} components")
        
        print(f"\n🎯 DOMAIN-DRIVEN ANALYSIS COMPLETED!")
        print(f"   - Files categorized by business domains")
        print(f"   - Domain-specific insights extracted")
        print(f"   - Cross-domain relationships identified")
        print(f"   - Complete source code understanding captured")
        
    except Exception as e:
        print(f"❌ Error saving knowledge base: {e}")
        raise

if __name__ == "__main__":
    # Fix the path: go up two levels from knowledge_base to reach root, then into backend
    source_path = "../../backend"
    
    if not os.path.exists(source_path):
        print(f"❌ Source folder not found: {source_path}")
        print("Please ensure the backend folder exists relative to this script.")
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
        print("The system requires LLM analysis to work. All output must be generated by LLM only.")
        print("Please check your LLM configuration and ensure it can provide valid JSON responses.")
        exit(1)
