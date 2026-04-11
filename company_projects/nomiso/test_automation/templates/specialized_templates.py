"""Specialized test templates for specific testing categories."""

from typing import Any, Dict, List
from .base_templates import (
    ChainOfThoughtTemplate,
    FewShotTemplate,
    TreeOfThoughtsTemplate,
    RoleBasedTemplate,
)


class PositiveTestTemplate(FewShotTemplate):
    """Few-shot template for positive test case generation."""

    def __init__(self):
        template_content = """
You are a test engineer focused on validating happy path scenarios and positive user experiences.

Here are examples of excellent positive test cases:

{% for example in examples %}
Example {{ loop.index }}:
Scenario: {{ example.scenario }}
Test Approach: {{ example.approach }}
Validation: {{ example.validation }}

{% endfor %}

Given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

Generate positive test cases that validate:

1. **Successful Operations**: Valid inputs producing expected outputs
2. **Business Rules**: Correct implementation of business logic
3. **User Workflows**: Smooth completion of user journeys
4. **Data Integrity**: Proper data creation, modification, and retrieval
5. **System Integration**: Successful communication between components
6. **Performance Within Limits**: Operations completing within acceptable time
7. **Security Compliance**: Authorized operations working correctly
8. **UI/UX Validation**: Interface responding correctly to valid interactions

Focus on:
- Valid input data sets
- Successful completion paths
- Expected system behaviors
- Positive user feedback scenarios
- Optimal performance conditions

Output as JSON following the schema format.
"""

        examples = [
            {
                "scenario": "User registration with valid data",
                "approach": "Test with properly formatted email, strong password, and all required fields completed",
                "validation": "Verify user account created, confirmation email sent, and user can login successfully",
            },
            {
                "scenario": "Product purchase workflow",
                "approach": "Test complete purchase flow with valid payment method and shipping address",
                "validation": "Verify order confirmation, payment processing, inventory update, and shipping notification",
            },
            {
                "scenario": "File upload with supported format",
                "approach": "Upload file within size limits and supported format (JPG, PNG, PDF)",
                "validation": "Verify file uploaded successfully, stored correctly, and accessible for download",
            },
        ]

        super().__init__("positive_test_generation", template_content, examples)

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_suite_name": {"type": "string"},
                "framework": {"type": "string"},
                "language": {"type": "string"},
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "test_name": {"type": "string"},
                            "description": {"type": "string"},
                            "test_type": {
                                "type": "string",
                                "enum": ["positive", "happy_path"],
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "user_story": {"type": "string"},
                            "preconditions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "test_inputs": {"type": "object"},
                            "expected_outputs": {"type": "object"},
                            "test_steps": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "success_criteria": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "business_value": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "test_name",
                            "description",
                            "test_type",
                            "expected_outputs",
                        ],
                    },
                },
            },
            "required": ["test_suite_name", "framework", "language", "test_cases"],
        }


class NegativeTestTemplate(TreeOfThoughtsTemplate):
    """Tree-of-Thoughts template for negative test case generation."""

    def __init__(self):
        template_content = """
You are a test engineer specializing in finding system weaknesses through negative testing scenarios.

Explore multiple paths for comprehensive negative testing:

{{ exploration_paths }}

Given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

Generate negative test cases that validate:

1. **Input Validation**: Invalid, malformed, or malicious inputs
2. **Error Handling**: System response to error conditions
3. **Security Vulnerabilities**: Unauthorized access attempts
4. **Resource Exhaustion**: System behavior under resource constraints
5. **Boundary Violations**: Values outside acceptable ranges
6. **State Corruption**: Invalid state transitions or corrupted data
7. **Integration Failures**: External service unavailability or errors
8. **Concurrency Issues**: Race conditions and deadlock scenarios

Focus on:
- Invalid data formats and types
- Missing required information
- Unauthorized operations
- System limit violations
- Malicious input attempts
- Error recovery scenarios

Output as JSON following the schema format.
"""

        exploration_paths = [
            "Path 1: Input Validation Failures - Invalid formats, missing fields, type mismatches",
            "Path 2: Authentication & Authorization Violations - Unauthorized access, privilege escalation",
            "Path 3: Business Rule Violations - Invalid operations, constraint violations",
            "Path 4: System Resource Exhaustion - Memory limits, disk space, connection pools",
            "Path 5: Data Integrity Attacks - SQL injection, XSS, data corruption attempts",
            "Path 6: Network and Integration Failures - Service timeouts, connection errors",
            "Path 7: State Management Issues - Invalid transitions, orphaned records",
            "Path 8: Boundary and Limit Testing - Overflow conditions, size violations",
        ]

        super().__init__(
            "negative_test_generation", template_content, exploration_paths
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_suite_name": {"type": "string"},
                "framework": {"type": "string"},
                "language": {"type": "string"},
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "test_name": {"type": "string"},
                            "description": {"type": "string"},
                            "test_type": {
                                "type": "string",
                                "enum": ["negative", "error_handling"],
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "attack_vector": {"type": "string"},
                            "invalid_inputs": {"type": "object"},
                            "expected_error": {"type": "string"},
                            "error_code": {"type": "string"},
                            "security_impact": {"type": "string"},
                            "test_steps": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "error_validation": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "recovery_steps": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "test_name",
                            "description",
                            "test_type",
                            "expected_error",
                        ],
                    },
                },
            },
            "required": ["test_suite_name", "framework", "language", "test_cases"],
        }


class HappyPathTestTemplate(RoleBasedTemplate):
    """Role-based template for happy path test generation."""

    def __init__(self):
        template_content = """
You are {{ role }} with expertise in {{ expertise }}.

Your goal is to create comprehensive happy path test scenarios that validate the core user journeys and business processes work seamlessly under ideal conditions.

Given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

As a user experience expert, design happy path tests that cover:

1. **Primary User Journeys**: Complete workflows from start to finish
2. **Core Business Processes**: Key operations that drive business value
3. **Optimal User Experience**: Smooth, intuitive interactions
4. **Integration Points**: Seamless data flow between components
5. **Performance Baselines**: Operations completing within expected times
6. **Data Consistency**: Accurate data handling throughout workflows
7. **User Satisfaction**: Positive feedback and successful outcomes
8. **Business Goals**: Achievement of intended business objectives

Focus on scenarios where:
- Users have valid permissions and data
- System resources are adequate
- Network conditions are optimal
- All dependencies are available
- Data is well-formed and complete

Create tests that business stakeholders can easily understand and validate.

Output as JSON following the schema format.
"""

        role = "Senior Business Analyst and UX Researcher"
        expertise = [
            "User journey mapping and optimization",
            "Business process analysis",
            "User experience design principles",
            "Acceptance criteria definition",
            "Stakeholder communication",
            "Business value validation",
            "Customer satisfaction metrics",
            "Process efficiency analysis",
        ]

        super().__init__(
            "happy_path_test_generation", template_content, role, expertise
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_suite_name": {"type": "string"},
                "framework": {"type": "string"},
                "language": {"type": "string"},
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "test_name": {"type": "string"},
                            "description": {"type": "string"},
                            "user_persona": {"type": "string"},
                            "business_goal": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "user_journey": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "optimal_conditions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "success_metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "business_value": {"type": "string"},
                            "test_steps": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "expected_outcomes": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "user_satisfaction_criteria": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "test_name",
                            "description",
                            "user_persona",
                            "business_goal",
                        ],
                    },
                },
            },
            "required": ["test_suite_name", "framework", "language", "test_cases"],
        }


class FunctionalTestTemplate(ChainOfThoughtTemplate):
    """Chain-of-Thought template for functional test generation."""

    def __init__(self):
        template_content = """
You are a functional testing expert with deep knowledge of requirements validation and feature verification.

Using systematic reasoning to create comprehensive functional tests:

{{ reasoning_steps }}

Given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

Generate functional test cases that validate:

1. **Feature Functionality**: Each feature works as specified
2. **Requirements Compliance**: Implementation matches requirements
3. **Business Logic**: Correct implementation of business rules
4. **Data Processing**: Accurate data transformation and calculation
5. **User Interface**: UI elements behave as expected
6. **Integration**: Proper interaction between system components
7. **Workflow Validation**: Process flows work correctly
8. **Configuration**: System responds to configuration changes

For each test case include:
- Requirement or feature being tested
- Test conditions and input data
- Expected behavior and outputs
- Acceptance criteria validation
- Dependencies and prerequisites

Output as JSON following the schema format.
"""

        reasoning_steps = [
            "Analyze functional requirements and identify all testable features",
            "Map each requirement to specific test scenarios covering different conditions",
            "Design test data that covers normal, boundary, and exceptional cases",
            "Plan validation steps that verify both functional and non-functional aspects",
            "Consider integration points and dependencies between features",
            "Identify configuration scenarios that affect feature behavior",
            "Plan user interface validation for interactive features",
            "Ensure coverage of all acceptance criteria and business rules",
        ]

        super().__init__(
            "functional_test_generation", template_content, reasoning_steps
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_suite_name": {"type": "string"},
                "framework": {"type": "string"},
                "language": {"type": "string"},
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "test_name": {"type": "string"},
                            "description": {"type": "string"},
                            "requirement_id": {"type": "string"},
                            "feature_name": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "test_type": {
                                "type": "string",
                                "enum": ["functional", "integration", "component"],
                            },
                            "preconditions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "test_inputs": {"type": "object"},
                            "test_steps": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "expected_results": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "acceptance_criteria": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "configuration": {"type": "object"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "test_name",
                            "description",
                            "feature_name",
                            "expected_results",
                        ],
                    },
                },
            },
            "required": ["test_suite_name", "framework", "language", "test_cases"],
        }


class E2ETestTemplate(TreeOfThoughtsTemplate):
    """Tree-of-Thoughts template for end-to-end test generation."""

    def __init__(self):
        template_content = """
You are an end-to-end testing specialist focused on validating complete user workflows across the entire system.

Explore multiple paths for comprehensive E2E testing:

{{ exploration_paths }}

Given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

Generate end-to-end test cases that validate:

1. **Complete User Workflows**: Full business processes from start to finish
2. **System Integration**: All components working together
3. **Data Flow**: Information passing correctly through all layers
4. **Cross-Browser/Platform**: Consistency across different environments
5. **Real-World Scenarios**: Realistic user behavior patterns
6. **Performance**: Acceptable response times for complete workflows
7. **Error Recovery**: System resilience during workflow execution
8. **Business Value**: Actual delivery of business outcomes

Focus on:
- Critical business processes
- Multi-system integrations
- User journey completeness
- Data consistency across systems
- Real-world usage patterns
- Performance under realistic loads

Output as JSON following the schema format.
"""

        exploration_paths = [
            "Path 1: Customer Journey - Registration, browsing, purchase, support, retention",
            "Path 2: Business Operations - Inventory management, order processing, fulfillment",
            "Path 3: Administrative Workflows - User management, reporting, configuration",
            "Path 4: Integration Scenarios - Payment processing, shipping, notifications",
            "Path 5: Data Lifecycle - Creation, modification, synchronization, archival",
            "Path 6: Security Workflows - Authentication, authorization, audit trails",
            "Path 7: Error Handling - Recovery from failures, data consistency maintenance",
            "Path 8: Performance Scenarios - High load conditions, concurrent user operations",
        ]

        super().__init__("e2e_test_generation", template_content, exploration_paths)

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_suite_name": {"type": "string"},
                "framework": {"type": "string"},
                "language": {"type": "string"},
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "test_name": {"type": "string"},
                            "description": {"type": "string"},
                            "business_process": {"type": "string"},
                            "user_roles": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "systems_involved": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "workflow_steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "step_name": {"type": "string"},
                                        "system": {"type": "string"},
                                        "action": {"type": "string"},
                                        "expected_result": {"type": "string"},
                                        "data_validation": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                    },
                                },
                            },
                            "success_criteria": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "performance_requirements": {"type": "object"},
                            "rollback_scenarios": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "environment_requirements": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "test_name",
                            "description",
                            "business_process",
                            "workflow_steps",
                        ],
                    },
                },
            },
            "required": ["test_suite_name", "framework", "language", "test_cases"],
        }
