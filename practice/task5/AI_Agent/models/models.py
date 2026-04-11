"""
Core data models and enums for the AI-Powered Unit Test Case Generation System.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class UnitComponentType(Enum):
    """Enumeration of unit component types for template selection."""
    PURE_FUNCTION = "pure_function"
    BUSINESS_LOGIC = "business_logic"
    VALIDATION_COMPONENT = "validation_component"
    DATA_TRANSFORMATION = "data_transformation"
    STATE_MANAGEMENT = "state_management"
    ALGORITHM = "algorithm"


class TestingPattern(Enum):
    """Enumeration of testing patterns for template selection."""
    STATE_VERIFICATION = "state_verification"
    BEHAVIOR_VALIDATION = "behavior_validation"
    INPUT_OUTPUT_TESTING = "input_output_testing"
    EXCEPTION_HANDLING = "exception_handling"
    BOUNDARY_TESTING = "boundary_testing"


@dataclass
class CodeUnit:
    """Represents a testable code unit extracted from the knowledge base."""
    name: str
    file_path: str
    component_type: UnitComponentType
    signature: str
    dependencies: List[str]
    return_type: str
    parameters: List[Dict[str, Any]]
    business_logic: str
    error_conditions: List[str]


@dataclass
class UserStory:
    """Represents a user story input for test generation."""
    title: str
    description: str
    acceptance_criteria: List[str]
    priority: str
    complexity: str
    selected_template: Optional[str] = None


class UnitTestTemplate(BaseModel):
    """Comprehensive unit test template structure."""
    template_name: str
    component_type: UnitComponentType
    testing_pattern: TestingPattern
    setup_code: str
    test_structure: str
    mock_configuration: str
    assertion_examples: List[str]
    coverage_guidelines: str


class GeneratedTest(BaseModel):
    """Represents a generated unit test case."""
    test_name: str
    target_unit: str
    setup_code: str
    input_parameters: Dict[str, Any]
    expected_output: Any
    assertions: List[str]
    mock_requirements: List[str]
    test_category: str
    test_steps: Optional[List[str]] = None


class TestSuite(BaseModel):
    """Complete test suite output."""
    template_selection: str
    unit_mapping: List[Dict[str, str]]
    test_cases: List[GeneratedTest]
    mock_specifications: Dict[str, str]
    coverage_analysis: str


class TestGenerationRequest(BaseModel):
    """Request model for test generation."""
    user_story: str
    codebase_path: Optional[str] = None
    test_framework: Optional[str] = "pytest"
    include_mocks: bool = True
    include_coverage: bool = True
    selected_template: Optional[str] = "prompt_1"


class TestGenerationResponse(BaseModel):
    """Response model for test generation."""
    success: bool
    test_suite: Optional[TestSuite] = None
    error_message: Optional[str] = None
    generation_time: Optional[float] = None
