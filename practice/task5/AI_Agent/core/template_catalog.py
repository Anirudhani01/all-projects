
"""
Template catalog for unit test generation with intelligent template selection.
"""

from typing import Dict, List
from models.models import UnitTestTemplate, UnitComponentType, TestingPattern, UserStory


class TemplateCatalog:
    """Catalog of available unit test templates with intelligent selection."""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, UnitTestTemplate]:
        """Initialize the template catalog with predefined templates."""
        return {
            "pure_function": UnitTestTemplate(
                template_name="Pure Function Template",
                component_type=UnitComponentType.PURE_FUNCTION,
                testing_pattern=TestingPattern.INPUT_OUTPUT_TESTING,
                setup_code="""
def test_{function_name}_with_valid_inputs():
    \"\"\"Test {function_name} with various valid input combinations.\"\"\"
    # Arrange
    {setup_code}
    
    # Act
    result = {function_name}({input_params})
    
    # Assert
    {assertions}
""",
                test_structure="Input/Output validation with multiple test scenarios",
                mock_configuration="No mocking required for pure functions",
                assertion_examples=[
                    "assert result == expected_value",
                    "assert isinstance(result, expected_type)",
                    "assert result is not None"
                ],
                coverage_guidelines="Test all input combinations, edge cases, and return types"
            ),
            
            "business_logic": UnitTestTemplate(
                template_name="Business Logic Template",
                component_type=UnitComponentType.BUSINESS_LOGIC,
                testing_pattern=TestingPattern.BEHAVIOR_VALIDATION,
                setup_code="""
def test_{function_name}_business_rules():
    \"\"\"Test {function_name} business logic and rule validation.\"\"\"
    # Arrange
    {setup_code}
    
    # Act
    result = {function_name}({input_params})
    
    # Assert
    {assertions}
""",
                test_structure="Business rule validation with multiple scenarios",
                mock_configuration="Mock external dependencies and database calls",
                assertion_examples=[
                    "assert result.status == expected_status",
                    "assert result.validation_passed is True",
                    "assert len(result.errors) == 0"
                ],
                coverage_guidelines="Test all business rules, validation logic, and error conditions"
            ),
            
            "validation_component": UnitTestTemplate(
                template_name="Validation Component Template",
                component_type=UnitComponentType.VALIDATION_COMPONENT,
                testing_pattern=TestingPattern.INPUT_OUTPUT_TESTING,
                setup_code="""
def test_{function_name}_validation_scenarios():
    \"\"\"Test {function_name} input validation and error handling.\"\"\"
    # Arrange
    {setup_code}
    
    # Act & Assert
    {assertions}
""",
                test_structure="Input validation with positive and negative test cases",
                mock_configuration="Mock external validation services if needed",
                assertion_examples=[
                    "with pytest.raises(ValidationError):",
                    "assert result.is_valid is True",
                    "assert result.error_message == expected_error"
                ],
                coverage_guidelines="Test valid inputs, invalid inputs, edge cases, and error messages"
            ),
            
            "data_transformation": UnitTestTemplate(
                template_name="Data Transformation Template",
                component_type=UnitComponentType.DATA_TRANSFORMATION,
                testing_pattern=TestingPattern.STATE_VERIFICATION,
                setup_code="""
def test_{function_name}_data_transformation():
    \"\"\"Test {function_name} data processing and transformation logic.\"\"\"
    # Arrange
    {setup_code}
    
    # Act
    result = {function_name}({input_params})
    
    # Assert
    {assertions}
""",
                test_structure="Data transformation verification with before/after state",
                mock_configuration="Mock data sources and external APIs",
                assertion_examples=[
                    "assert result.transformed_data == expected_output",
                    "assert result.original_data == input_data",
                    "assert result.transformation_successful is True"
                ],
                coverage_guidelines="Test data integrity, transformation accuracy, and error handling"
            ),
            
            "state_management": UnitTestTemplate(
                template_name="State Management Template",
                component_type=UnitComponentType.STATE_MANAGEMENT,
                testing_pattern=TestingPattern.STATE_VERIFICATION,
                setup_code="""
def test_{function_name}_state_changes():
    \"\"\"Test {function_name} state manipulation and verification.\"\"\"
    # Arrange
    {setup_code}
    
    # Act
    result = {function_name}({input_params})
    
    # Assert
    {assertions}
""",
                test_structure="State verification before and after method execution",
                mock_configuration="Mock database state and external state services",
                assertion_examples=[
                    "assert initial_state != final_state",
                    "assert result.state == expected_state",
                    "assert state_transition_valid is True"
                ],
                coverage_guidelines="Test state transitions, state validation, and state persistence"
            ),
            
            "algorithm": UnitTestTemplate(
                template_name="Algorithm Template",
                component_type=UnitComponentType.ALGORITHM,
                testing_pattern=TestingPattern.INPUT_OUTPUT_TESTING,
                setup_code="""
def test_{function_name}_algorithm_correctness():
    \"\"\"Test {function_name} algorithmic logic and computational accuracy.\"\"\"
    # Arrange
    {setup_code}
    
    # Act
    result = {function_name}({input_params})
    
    # Assert
    {assertions}
""",
                test_structure="Algorithm correctness with mathematical verification",
                mock_configuration="Mock computational dependencies if needed",
                assertion_examples=[
                    "assert result == expected_calculation",
                    "assert abs(result - expected_value) < tolerance",
                    "assert algorithm_complexity <= expected_complexity"
                ],
                coverage_guidelines="Test algorithm correctness, edge cases, and performance characteristics"
            )
        }
    
    def select_template(self, user_story: UserStory, code_units: List['CodeUnit']) -> UnitTestTemplate:
        """Intelligently select the optimal template based on story and code analysis."""
        # Analyze story complexity and requirements
        complexity_score = self._analyze_story_complexity(user_story)
        unit_types = [unit.component_type for unit in code_units]
        
        # Template selection logic based on component types
        if UnitComponentType.PURE_FUNCTION in unit_types:
            return self.templates["pure_function"]
        elif UnitComponentType.BUSINESS_LOGIC in unit_types:
            return self.templates["business_logic"]
        elif UnitComponentType.VALIDATION_COMPONENT in unit_types:
            return self.templates["validation_component"]
        elif UnitComponentType.DATA_TRANSFORMATION in unit_types:
            return self.templates["data_transformation"]
        elif UnitComponentType.STATE_MANAGEMENT in unit_types:
            return self.templates["state_management"]
        elif UnitComponentType.ALGORITHM in unit_types:
            return self.templates["algorithm"]
        else:
            # Default to business logic template
            return self.templates["business_logic"]
    
    def _analyze_story_complexity(self, user_story: UserStory) -> int:
        """Analyze user story complexity for template selection."""
        complexity_score = 0
        
        # Analyze description length and complexity
        if len(user_story.description) > 200:
            complexity_score += 2
        elif len(user_story.description) > 100:
            complexity_score += 1
        
        # Analyze acceptance criteria complexity
        complexity_score += len(user_story.acceptance_criteria)
        
        # Analyze priority impact
        if user_story.priority == "high":
            complexity_score += 1
        
        return complexity_score
    
    def get_template_by_type(self, component_type: UnitComponentType) -> UnitTestTemplate:
        """Get template by specific component type."""
        for template in self.templates.values():
            if template.component_type == component_type:
                return template
        return self.templates["business_logic"]  # Default fallback
    
    def list_available_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())
