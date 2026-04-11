"""
Gemini API integration for the AI-Powered Unit Test Case Generation System.
Uses Google's Gemini model for intelligent test generation.
"""

import json
import os
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GeminiIntegration:
    """Integration with Google Gemini API for AI-powered test generation."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY in .env file or pass it directly.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        
    def is_available(self) -> bool:
        """Check if Gemini API is available and configured."""
        try:
            # Test with a simple prompt
            response = self.model.generate_content("Hello")
            return response.text is not None
        except Exception:
            return False
    
    def generate_test_cases(self, user_story: str, code_units: list, template_info: dict) -> Dict[str, Any]:
        """Generate test cases using Gemini API."""
        
        # Create a comprehensive prompt for the model
        prompt = self._create_test_generation_prompt(user_story, code_units, template_info)
        
        try:
            # Generate content using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.9,
                    max_output_tokens=2048
                )
            )
            
            if response.text:
                # Parse the generated response
                return self._parse_generated_response(response.text)
            else:
                return {
                    "success": False,
                    "error": "No response generated from Gemini",
                    "generated_tests": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calling Gemini API: {str(e)}",
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
        """Parse the generated response from Gemini."""
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
        """Get information about the Gemini model."""
        try:
            return {
                "model_name": self.model_name,
                "api_key_configured": bool(self.api_key),
                "model_available": True,
                "provider": "Google Gemini"
            }
        except Exception as e:
            return {"error": f"Error getting model info: {str(e)}"}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Gemini API."""
        try:
            response = self.model.generate_content("Test connection")
            if response.text:
                return {
                    "connected": True,
                    "model_available": True,
                    "model_name": self.model_name,
                    "provider": "Google Gemini"
                }
            else:
                return {
                    "connected": False,
                    "error": "No response from model"
                }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
