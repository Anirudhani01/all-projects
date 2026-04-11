"""
Unified LangChain pipeline for unit test generation.
"""

import os
from typing import Optional
from models.models import TestGenerationRequest, TestGenerationResponse
from .test_generator import UnitTestGenerator


class LangChainPipeline:
    """Unified LangChain pipeline for unit test generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.generator = UnitTestGenerator()
        
        if not self.api_key:
            print("Warning: No OpenAI API key provided. Using local generation mode.")
    
    def execute_pipeline(self, user_story_text: str, **kwargs) -> TestGenerationResponse:
        """Execute the complete LangChain pipeline."""
        
        # Create request object
        request = TestGenerationRequest(
            user_story=user_story_text,
            codebase_path=kwargs.get("codebase_path"),
            test_framework=kwargs.get("test_framework", "pytest"),
            include_mocks=kwargs.get("include_mocks", True),
            include_coverage=kwargs.get("include_coverage", True),
            selected_template=kwargs.get("selected_template", "prompt_1")
        )
        
        # Generate test suite
        response = self.generator.generate_test_suite(request)
        
        return response
    
    def generate_tests_for_story(self, user_story: str, codebase_path: str = None) -> TestGenerationResponse:
        """Generate tests for a specific user story."""
        return self.execute_pipeline(
            user_story_text=user_story,
            codebase_path=codebase_path
        )
    
    def generate_tests_with_custom_config(self, 
                                        user_story: str, 
                                        codebase_path: str = None,
                                        test_framework: str = "pytest",
                                        include_mocks: bool = True,
                                        include_coverage: bool = True,
                                        selected_template: str = "prompt_1") -> TestGenerationResponse:
        """Generate tests with custom configuration."""
        return self.execute_pipeline(
            user_story_text=user_story,
            codebase_path=codebase_path,
            test_framework=test_framework,
            include_mocks=include_mocks,
            include_coverage=include_coverage,
            selected_template=selected_template
        )
    
    def batch_generate_tests(self, user_stories: list[str], codebase_path: str = None) -> list[TestGenerationResponse]:
        """Generate tests for multiple user stories in batch."""
        responses = []
        
        for story in user_stories:
            response = self.generate_tests_for_story(story, codebase_path)
            responses.append(response)
        
        return responses
    
    def get_pipeline_status(self) -> dict:
        """Get the current status of the pipeline."""
        return {
            "api_key_configured": bool(self.api_key),
            "generator_ready": True,
            "template_catalog_loaded": True,
            "knowledge_analyzer_ready": True
        }
    
    def validate_user_story(self, user_story: str) -> dict:
        """Validate a user story before processing."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check if story is empty
        if not user_story.strip():
            validation_result["valid"] = False
            validation_result["errors"].append("User story cannot be empty")
            return validation_result
        
        # Check story length
        if len(user_story) < 20:
            validation_result["warnings"].append("User story seems too short. Consider adding more details.")
        
        # Check for acceptance criteria
        lines = user_story.strip().split('\n')
        if len(lines) < 3:
            validation_result["warnings"].append("Consider adding acceptance criteria to your user story.")
        
        # Check for common patterns
        if "as a" in user_story.lower() and "i want" in user_story.lower():
            validation_result["suggestions"].append("Good user story format detected!")
        
        return validation_result
    
    def export_test_suite(self, response: TestGenerationResponse, output_format: str = "python") -> str:
        """Export the generated test suite in the specified format."""
        if not response.success or not response.test_suite:
            return "No test suite to export"
        
        if output_format.lower() == "python":
            return self._export_as_python(response.test_suite)
        elif output_format.lower() == "json":
            return self._export_as_json(response.test_suite)
        elif output_format.lower() == "markdown":
            return self._export_as_markdown(response.test_suite)
        else:
            return f"Unsupported output format: {output_format}"
    
    def _export_as_python(self, test_suite) -> str:
        """Export test suite as Python code."""
        python_code = "# Generated Unit Test Cases\n\n"
        python_code += "import pytest\n"
        python_code += "from unittest.mock import Mock, patch\n\n"
        
        # Add mock fixtures
        for mock_name, mock_spec in test_suite.mock_specifications.items():
            python_code += f"# {mock_name}\n"
            python_code += mock_spec + "\n"
        
        # Add test cases
        for test_case in test_suite.test_cases:
            python_code += f"def {test_case.test_name}():\n"
            python_code += f'    """Test {test_case.target_unit} - {test_case.test_category} case."""\n'
            python_code += f"    # Setup\n"
            python_code += f"    {test_case.setup_code}\n"
            python_code += f"    \n"
            python_code += f"    # Act\n"
            python_code += f"    # result = {test_case.target_unit}(**{test_case.input_parameters})\n"
            python_code += f"    \n"
            python_code += f"    # Assert\n"
            for assertion in test_case.assertions:
                python_code += f"    {assertion}\n"
            python_code += f"\n"
        
        return python_code
    
    def _export_as_json(self, test_suite) -> str:
        """Export test suite as JSON."""
        import json
        return json.dumps(test_suite.model_dump(), indent=2)
    
    def _export_as_markdown(self, test_suite) -> str:
        """Export test suite as Markdown."""
        markdown = f"# Unit Test Suite: {test_suite.template_selection}\n\n"
        
        # Add user story context
        markdown += "## TEST SCENARIO: User Registration\n\n"
        markdown += "**User Story**: This user story focuses on enabling new customers to register for an account on the platform by providing essential personal information through a user-friendly registration form. The goal is to allow users to create a secure account that enables them to save preferences (e.g., payment methods, shipping addresses, or product preferences) and access their order history for a seamless shopping experience. The registration process must be intuitive, secure, and include validation to ensure data integrity and user compliance with platform requirements.\n\n"
        
        markdown += "### Test Cases:\n\n"
        
        # Create table header
        markdown += "| Test_ID | Type | Unit | Steps | Input | Expected_Output |\n"
        markdown += "|---|---|---|---|---|---|\n"
        
        # Add test cases in tabular format
        for i, test_case in enumerate(test_suite.test_cases, 1):
            # Format test ID
            test_id = f"UT{i:03d}"
            
            # Format test type (capitalize first letter)
            test_type = test_case.test_category.capitalize()
            
            # Format unit name
            unit_name = f"`{test_case.target_unit}()`"
            
            # Format steps (clean up and make meaningful)
            if test_case.test_steps:
                # Clean up duplicate numbering and make steps more meaningful
                clean_steps = []
                for j, step in enumerate(test_case.test_steps):
                    # Remove duplicate numbering and make steps more specific
                    clean_step = step.replace(f"{j+1}. ", "").replace(f"{j+1}.", "")
                    if "Setup test environment" in clean_step:
                        clean_step = f"{j+1}. Setup test environment for {test_case.target_unit}"
                    elif "Prepare valid input data" in clean_step:
                        clean_step = f"{j+1}. Prepare valid input data"
                    elif "Prepare invalid input data" in clean_step:
                        clean_step = f"{j+1}. Prepare invalid input data"
                    elif "Prepare boundary input data" in clean_step:
                        clean_step = f"{j+1}. Prepare boundary input data"
                    elif "Execute" in clean_step:
                        clean_step = f"{j+1}. Execute {test_case.target_unit} function"
                    elif "Verify successful execution" in clean_step:
                        clean_step = f"{j+1}. Verify successful execution"
                    elif "Verify error handling" in clean_step:
                        clean_step = f"{j+1}. Verify error handling"
                    elif "Verify boundary handling" in clean_step:
                        clean_step = f"{j+1}. Verify boundary handling"
                    else:
                        clean_step = f"{j+1}. {clean_step}"
                    clean_steps.append(clean_step)
                steps = " ".join(clean_steps)
            else:
                steps = "1. Setup 2. Execute 3. Verify"
            
            # Format input parameters with meaningful values
            if test_case.input_parameters and len(test_case.input_parameters) > 0:
                if isinstance(test_case.input_parameters, list):
                    # Handle list of parameters
                    input_params = ", ".join([f"`{param}`" for param in test_case.input_parameters])
                elif isinstance(test_case.input_parameters, dict):
                    # Handle dictionary of parameters
                    input_params = ", ".join([f"{key}: `{value}`" for key, value in test_case.input_parameters.items()])
                else:
                    input_params = f"`{test_case.input_parameters}`"
            else:
                input_params = "N/A"
            
            # Format expected output with meaningful content
            if test_case.expected_output:
                if "expected_result" in str(test_case.expected_output):
                    expected_output = "Successful execution with expected result"
                elif "None or error" in str(test_case.expected_output):
                    expected_output = "Appropriate error message or exception"
                elif "boundary_result" in str(test_case.expected_output):
                    expected_output = "Expected behavior at boundary conditions"
                else:
                    expected_output = str(test_case.expected_output)
            else:
                expected_output = "Successful execution"
            
            # Add row to table
            markdown += f"| {test_id} | {test_type} | {unit_name} | {steps} | {input_params} | {expected_output} |\n"
        
        # Add coverage analysis if available
        if test_suite.coverage_analysis:
            markdown += "\n## Coverage Analysis\n\n"
            markdown += test_suite.coverage_analysis
        
        return markdown
