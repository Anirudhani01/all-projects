"""
Ollama integration for the AI-Powered Unit Test Case Generation System.
Uses the phi3:mini model for intelligent test generation.
"""

import json
import time
from typing import Dict, Any, Optional
import requests


class OllamaIntegration:
    """Integration with Ollama for AI-powered test generation."""
    
    def __init__(self, model_name: str = "phi3:mini", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
    def is_available(self) -> bool:
        """Check if Ollama is available and the model is loaded."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model["name"] == self.model_name for model in models)
            return False
        except Exception:
            return False
    
    def generate_test_cases(self, user_story: str, code_units: list, template_info: dict) -> Dict[str, Any]:
        """Generate test cases using Ollama phi3:mini model."""
        
        # Create a comprehensive prompt for the model
        prompt = self._create_test_generation_prompt(user_story, code_units, template_info)
        
        try:
            # Call Ollama API
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 2048
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "")
                
                # Parse the generated response
                return self._parse_generated_response(generated_text)
            else:
                return {
                    "success": False,
                    "error": f"Ollama API error: {response.status_code}",
                    "generated_tests": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calling Ollama: {str(e)}",
                "generated_tests": []
            }
    
    def _create_test_generation_prompt(self, user_story: str, code_units: list, template_info: dict) -> str:
        """Create a comprehensive prompt for test generation."""
        
        prompt = f"""You are an expert unit testing engineer. Generate comprehensive unit test cases for the following user story and code units.

USER STORY:
{user_story}

SELECTED TEMPLATE:
{template_info.get('template_name', 'Business Logic Template')}
Component Type: {template_info.get('component_type', 'business_logic')}
Testing Pattern: {template_info.get('testing_pattern', 'behavior_validation')}

CODE UNITS TO TEST:
"""
        
        for unit in code_units:
            prompt += f"""
- {unit.name}:
  - File: {unit.file_path}
  - Type: {unit.component_type}
  - Signature: {unit.signature}
  - Dependencies: {', '.join(unit.dependencies)}
  - Business Logic: {unit.business_logic}
  - Error Conditions: {', '.join(unit.error_conditions)}
"""
        
        prompt += """

INSTRUCTIONS:
Generate comprehensive unit test cases following these guidelines:
1. Create positive, negative, boundary, and exception test cases for each code unit
2. Include proper setup, mocking, and assertions
3. Follow pytest conventions
4. Ensure proper isolation and dependency mocking
5. Include meaningful test names and descriptions

OUTPUT FORMAT:
Return a JSON object with this structure:
{
  "test_cases": [
    {
      "test_name": "test_function_name_positive_case",
      "target_unit": "function_name",
      "setup_code": "setup code here",
      "input_parameters": {"param1": "value1"},
      "expected_output": "expected result",
      "assertions": ["assertion1", "assertion2"],
      "mock_requirements": ["Mock dependency1", "Mock dependency2"],
      "test_category": "positive|negative|boundary|exception"
    }
  ],
  "mock_specifications": {
    "dependency_name": "mock fixture code here"
  },
  "coverage_analysis": "Coverage analysis text here"
}

Generate the test cases now:"""

        return prompt
    
    def _parse_generated_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the generated response from Ollama."""
        try:
            # Try to extract JSON from the response
            # Look for JSON content between ```json and ``` markers
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end != -1:
                    json_content = response_text[start:end].strip()
                    return json.loads(json_content)
            
            # Try to find JSON content in the response
            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
            
            # If no valid JSON found, return a structured error
            return {
                "success": False,
                "error": "Could not parse generated response as JSON",
                "raw_response": response_text,
                "generated_tests": []
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error parsing response: {str(e)}",
                "raw_response": response_text,
                "generated_tests": []
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        try:
            response = requests.get(f"{self.base_url}/api/show", 
                                 json={"name": self.model_name}, 
                                 timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get model info: {response.status_code}"}
        except Exception as e:
            return {"error": f"Error getting model info: {str(e)}"}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_found = any(model["name"] == self.model_name for model in models)
                
                return {
                    "connected": True,
                    "model_available": model_found,
                    "available_models": [model["name"] for model in models],
                    "target_model": self.model_name
                }
            else:
                return {
                    "connected": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
