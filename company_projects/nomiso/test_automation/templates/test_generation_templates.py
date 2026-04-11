"""Advanced test generation prompt templates using sophisticated prompting techniques."""

from typing import Any, Dict, List
from .base_templates import (
    ChainOfThoughtTemplate,
    FewShotTemplate,
    TreeOfThoughtsTemplate,
    RoleBasedTemplate,
    MetacognitiveTemplate,
)


class APITestTemplate(ChainOfThoughtTemplate):
    """Chain-of-Thought template for API test generation."""

    def __init__(self):
        template_content = """
You are an expert API test engineer with deep knowledge of REST API testing, HTTP protocols, and test automation frameworks.

Given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

Use Chain-of-Thought reasoning to generate comprehensive API test cases:

{{ reasoning_steps }}

Based on your step-by-step analysis, generate API test cases that cover:

1. **HTTP Methods & Endpoints**: Test all supported HTTP methods (GET, POST, PUT, DELETE, PATCH)
2. **Authentication & Authorization**: Test various auth scenarios including invalid tokens, expired sessions
3. **Input Validation**: Test boundary conditions, invalid data types, missing required fields
4. **Response Validation**: Verify status codes, response structure, data integrity
5. **Error Handling**: Test various error conditions and edge cases
6. **Performance**: Basic load and response time validation
7. **Security**: Test for common vulnerabilities (injection, XSS, etc.)

For each test case, include:
- Test name and description
- HTTP method and endpoint
- Request headers and body
- Expected response code and structure
- Assertions to validate
- Setup and teardown requirements

Output your response as valid JSON following this exact schema:
{
  "test_suite_name": "string",
  "framework": "string",
  "language": "string",
  "test_cases": [
    {
      "test_name": "string",
      "description": "string",
      "category": "string",
      "priority": "high|medium|low",
      "http_method": "string",
      "endpoint": "string",
      "headers": {},
      "request_body": {},
      "expected_status_code": "number",
      "expected_response": {},
      "assertions": ["string"],
      "setup": ["string"],
      "teardown": ["string"],
      "tags": ["string"]
    }
  ]
}
"""

        reasoning_steps = [
            "Analyze the application's API endpoints and identify all testable operations",
            "Categorize tests by HTTP methods and map each to specific business operations",
            "Identify authentication/authorization requirements and edge cases",
            "Design input validation tests covering boundary values, invalid types, and malformed data",
            "Plan response validation including status codes, headers, and payload structure",
            "Consider error scenarios like network failures, timeouts, and server errors",
            "Include security testing for common API vulnerabilities",
            "Design performance tests for response times and basic load scenarios",
        ]

        super().__init__("api_test_generation", template_content, reasoning_steps)

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
                            "category": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "http_method": {"type": "string"},
                            "endpoint": {"type": "string"},
                            "headers": {"type": "object"},
                            "request_body": {"type": "object"},
                            "expected_status_code": {"type": "number"},
                            "expected_response": {"type": "object"},
                            "assertions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "setup": {"type": "array", "items": {"type": "string"}},
                            "teardown": {"type": "array", "items": {"type": "string"}},
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "test_name",
                            "description",
                            "category",
                            "priority",
                        ],
                    },
                },
            },
            "required": ["test_suite_name", "framework", "language", "test_cases"],
        }


class UnitTestTemplate(FewShotTemplate):
    """Few-shot learning template for unit test generation."""

    def __init__(self):
        template_content = """
You are a senior software engineer and testing expert specializing in unit test design and test-driven development.

Here are examples of excellent unit tests to guide your thinking:

{% for example in examples %}
Example {{ loop.index }}:
Function: {{ example.function_name }}
Test: {{ example.test_code }}
Explanation: {{ example.explanation }}

{% endfor %}

Now, given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

Generate comprehensive unit test cases following these principles:
1. Test one specific behavior per test
2. Use descriptive test names that explain what is being tested
3. Follow AAA pattern (Arrange, Act, Assert)
4. Include edge cases and boundary conditions
5. Test both positive and negative scenarios
6. Mock external dependencies appropriately
7. Ensure tests are fast, reliable, and independent

Focus on testing:
- Business logic functions
- Data validation and transformation
- Error handling and exception cases
- Boundary conditions and edge cases
- State management and side effects

Output as JSON following the schema format.
"""

        examples = [
            {
                "function_name": "validate_email",
                "test_code": """
def test_validate_email_with_valid_email_returns_true():
    # Arrange
    valid_email = "user@example.com"
    
    # Act
    result = validate_email(valid_email)
    
    # Assert
    assert result is True

def test_validate_email_with_invalid_format_returns_false():
    # Arrange
    invalid_email = "invalid-email"
    
    # Act
    result = validate_email(invalid_email)
    
    # Assert
    assert result is False
""",
                "explanation": "Tests both valid and invalid email scenarios with clear naming and AAA pattern",
            },
            {
                "function_name": "calculate_discount",
                "test_code": """
def test_calculate_discount_with_premium_customer_applies_20_percent():
    # Arrange
    order_total = Decimal('100.00')
    customer = Customer(type='premium')
    
    # Act
    discount = calculate_discount(order_total, customer)
    
    # Assert
    assert discount == Decimal('20.00')

def test_calculate_discount_with_zero_amount_returns_zero():
    # Arrange
    order_total = Decimal('0.00')
    customer = Customer(type='regular')
    
    # Act
    discount = calculate_discount(order_total, customer)
    
    # Assert
    assert discount == Decimal('0.00')
""",
                "explanation": "Tests business logic with different customer types and edge case of zero amount",
            },
        ]

        super().__init__("unit_test_generation", template_content, examples)

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
                            "function_under_test": {"type": "string"},
                            "test_type": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "test_code": {"type": "string"},
                            "setup_code": {"type": "string"},
                            "teardown_code": {"type": "string"},
                            "mocks": {"type": "array", "items": {"type": "string"}},
                            "assertions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["test_name", "description", "test_code"],
                    },
                },
            },
            "required": ["test_suite_name", "framework", "language", "test_cases"],
        }


class WebUITestTemplate(TreeOfThoughtsTemplate):
    """Tree-of-Thoughts template for WebUI test generation."""

    def __init__(self):
        template_content = """
You are an expert UI/UX test engineer with extensive experience in web application testing, Selenium, and user journey validation.

Using Tree-of-Thoughts reasoning, explore multiple paths for comprehensive UI testing:

{{ exploration_paths }}

Given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

Generate WebUI test cases covering:

1. **User Journey Testing**: Complete end-to-end user workflows
2. **Element Interaction**: Clicks, form inputs, navigation, file uploads
3. **Visual Validation**: Layout, responsiveness, cross-browser compatibility
4. **Accessibility Testing**: WCAG compliance, keyboard navigation, screen readers
5. **Performance**: Page load times, resource loading, JavaScript execution
6. **Error Handling**: Invalid inputs, network errors, JavaScript errors
7. **Security**: XSS prevention, CSRF protection, input sanitization

For each test case include:
- Test scenario and user story
- Page objects and locators
- Step-by-step actions
- Expected outcomes and assertions
- Browser compatibility requirements
- Accessibility checks

Output as JSON following the schema format.
"""

        exploration_paths = [
            "Path 1: User Authentication Flow - Login, logout, password reset, session management",
            "Path 2: Core Business Operations - Product browsing, cart management, checkout process",
            "Path 3: Form Interactions - Data entry, validation, submission, error handling",
            "Path 4: Navigation and Routing - Menu navigation, breadcrumbs, deep links, back/forward",
            "Path 5: Responsive Design - Mobile, tablet, desktop layouts and interactions",
            "Path 6: Accessibility Features - Keyboard navigation, screen reader compatibility, focus management",
            "Path 7: Error Scenarios - Network failures, invalid inputs, JavaScript errors, timeouts",
            "Path 8: Performance Aspects - Page load speed, resource optimization, lazy loading",
        ]

        super().__init__("webui_test_generation", template_content, exploration_paths)

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
                            "user_story": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "page_url": {"type": "string"},
                            "locators": {"type": "object"},
                            "test_steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "step": {"type": "string"},
                                        "action": {"type": "string"},
                                        "element": {"type": "string"},
                                        "data": {"type": "string"},
                                        "expected_result": {"type": "string"},
                                    },
                                },
                            },
                            "assertions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "browser_compatibility": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "accessibility_checks": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["test_name", "description", "test_steps"],
                    },
                },
            },
            "required": ["test_suite_name", "framework", "language", "test_cases"],
        }


class MobileUITestTemplate(RoleBasedTemplate):
    """Role-based template for Mobile UI test generation."""

    def __init__(self):
        template_content = """
You are {{ role }} with expertise in {{ expertise }}.

Your mission is to create comprehensive mobile UI test cases that ensure excellent user experience across different devices, operating systems, and usage scenarios.

Given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

As a mobile testing expert, focus on:

1. **Platform-Specific Testing**: iOS and Android specific behaviors and UI patterns
2. **Device Variations**: Different screen sizes, resolutions, and hardware capabilities
3. **Gestures and Interactions**: Tap, swipe, pinch, long press, multi-touch
4. **Orientation Changes**: Portrait/landscape mode transitions
5. **Performance on Mobile**: Battery usage, memory consumption, CPU utilization
6. **Network Conditions**: Wi-Fi, cellular, offline scenarios, poor connectivity
7. **Mobile-Specific Features**: Camera, GPS, push notifications, biometric authentication
8. **App Lifecycle**: Background/foreground transitions, app termination/restoration

Consider mobile-specific challenges:
- Touch targets and accessibility
- Loading times on slower networks
- Battery optimization
- Security on mobile devices
- App store compliance

Output comprehensive test cases as JSON following the schema format.
"""

        role = "Senior Mobile QA Engineer and UX Specialist"
        expertise = [
            "iOS and Android testing frameworks",
            "Mobile app automation (Appium, Espresso, XCUITest)",
            "Device fragmentation testing",
            "Mobile performance optimization",
            "Touch interface design patterns",
            "Mobile accessibility standards",
            "Network simulation and testing",
            "Mobile security testing",
        ]

        super().__init__("mobile_ui_test_generation", template_content, role, expertise)

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_suite_name": {"type": "string"},
                "framework": {"type": "string"},
                "language": {"type": "string"},
                "platform": {
                    "type": "string",
                    "enum": ["iOS", "Android", "Cross-platform"],
                },
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "test_name": {"type": "string"},
                            "description": {"type": "string"},
                            "platform": {"type": "string"},
                            "device_requirements": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "gestures": {"type": "array", "items": {"type": "string"}},
                            "test_steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "step": {"type": "string"},
                                        "action": {"type": "string"},
                                        "element": {"type": "string"},
                                        "gesture": {"type": "string"},
                                        "expected_result": {"type": "string"},
                                    },
                                },
                            },
                            "performance_metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "network_conditions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "accessibility_checks": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "test_name",
                            "description",
                            "platform",
                            "test_steps",
                        ],
                    },
                },
            },
            "required": [
                "test_suite_name",
                "framework",
                "language",
                "platform",
                "test_cases",
            ],
        }


class EdgeCaseTestTemplate(MetacognitiveTemplate):
    """Metacognitive template for Edge Case test generation."""

    def __init__(self):
        template_content = """
You are an expert test engineer specializing in edge case discovery and boundary testing with deep knowledge of software failure modes.

{{ reflection_questions }}

Given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

After reflecting on the questions above, generate comprehensive edge case tests covering:

1. **Boundary Value Analysis**: Min/max values, off-by-one errors, overflow/underflow
2. **Data Type Edge Cases**: Null values, empty strings, special characters, Unicode
3. **Concurrency Issues**: Race conditions, deadlocks, thread safety
4. **Resource Limitations**: Memory constraints, disk space, network timeouts
5. **State Transitions**: Invalid state changes, orphaned states
6. **Integration Points**: Service failures, external API errors, database connectivity
7. **Security Edge Cases**: Injection attacks, privilege escalation, data exposure
8. **Performance Edge Cases**: Memory leaks, CPU spikes, infinite loops

Focus on scenarios that typically cause production issues:
- Unexpected user behavior
- System resource exhaustion
- Network instability
- Data corruption scenarios
- Time-based edge cases (timezone, DST, leap years)

Output as JSON following the schema format.
"""

        reflection_questions = [
            "What are the most critical failure points in this system?",
            "Where do data boundaries exist and what happens at the extremes?",
            "What assumptions does the code make that could be violated?",
            "What external dependencies could fail and how?",
            "What concurrent operations could interfere with each other?",
            "What security vulnerabilities might exist at edge conditions?",
            "What happens when resources are exhausted?",
            "How does the system behave under extreme load or unusual timing?",
        ]

        super().__init__(
            "edge_case_test_generation", template_content, reflection_questions
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
                            "edge_case_type": {"type": "string"},
                            "risk_level": {
                                "type": "string",
                                "enum": ["critical", "high", "medium", "low"],
                            },
                            "boundary_conditions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "test_data": {"type": "object"},
                            "expected_behavior": {"type": "string"},
                            "failure_mode": {"type": "string"},
                            "preconditions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "test_steps": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "assertions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "mitigation_strategy": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "test_name",
                            "description",
                            "edge_case_type",
                            "risk_level",
                        ],
                    },
                },
            },
            "required": ["test_suite_name", "framework", "language", "test_cases"],
        }


# Performance Test Template using Self-Consistency Prompting
class PerformanceTestTemplate(ChainOfThoughtTemplate):
    """Performance test generation using Chain-of-Thought with self-consistency."""

    def __init__(self):
        template_content = """
You are a performance testing specialist with expertise in load testing, stress testing, and performance optimization.

Using systematic reasoning, analyze the application and generate performance test cases:

{{ reasoning_steps }}

Given the following context:
- Programming Language: {{ programming_language }}
- Testing Framework: {{ testing_framework }}
- Application Knowledge Base: {{ knowledge_base }}
- Test Scenarios: {{ test_scenarios }}

Generate performance test cases covering:

1. **Load Testing**: Normal expected load patterns
2. **Stress Testing**: Beyond normal capacity to find breaking points
3. **Spike Testing**: Sudden load increases
4. **Volume Testing**: Large amounts of data processing
5. **Endurance Testing**: Extended periods under normal load
6. **Scalability Testing**: System behavior as load increases
7. **Resource Utilization**: CPU, memory, disk, network usage
8. **Response Time Testing**: Latency under various conditions

For each test include:
- Performance objectives and SLAs
- Load patterns and user scenarios
- Metrics to measure and thresholds
- Resource monitoring requirements
- Test duration and ramp-up patterns

Output as JSON following the schema format.
"""

        reasoning_steps = [
            "Identify critical performance paths and bottlenecks in the application architecture",
            "Analyze expected user load patterns and peak usage scenarios",
            "Define performance requirements and acceptable thresholds for response times",
            "Design realistic load profiles that simulate actual user behavior",
            "Plan resource monitoring to identify performance constraints",
            "Create stress scenarios to find system breaking points and failure modes",
            "Design endurance tests to identify memory leaks and degradation over time",
            "Plan scalability tests to validate system growth and capacity planning",
        ]

        super().__init__(
            "performance_test_generation", template_content, reasoning_steps
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
                                "enum": [
                                    "load",
                                    "stress",
                                    "spike",
                                    "volume",
                                    "endurance",
                                    "scalability",
                                ],
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "load_pattern": {
                                "type": "object",
                                "properties": {
                                    "concurrent_users": {"type": "number"},
                                    "ramp_up_time": {"type": "string"},
                                    "test_duration": {"type": "string"},
                                    "think_time": {"type": "string"},
                                },
                            },
                            "performance_objectives": {
                                "type": "object",
                                "properties": {
                                    "response_time_p95": {"type": "string"},
                                    "throughput_rps": {"type": "number"},
                                    "error_rate_max": {"type": "string"},
                                    "cpu_utilization_max": {"type": "string"},
                                    "memory_utilization_max": {"type": "string"},
                                },
                            },
                            "test_scenarios": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "monitoring_metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "test_data_requirements": {"type": "string"},
                            "environment_requirements": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "test_name",
                            "description",
                            "test_type",
                            "load_pattern",
                            "performance_objectives",
                        ],
                    },
                },
            },
            "required": ["test_suite_name", "framework", "language", "test_cases"],
        }
