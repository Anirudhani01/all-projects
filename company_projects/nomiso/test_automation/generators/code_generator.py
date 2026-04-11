"""Code generator for creating test files from generated test cases."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from jinja2 import Template, Environment, DictLoader

from ..llm import LLMProvider


class CodeGenerator:
    """Generates actual test code files from test case specifications."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """Initialize code generator.

        Args:
            llm_provider: Optional LLM provider for dynamic code generation
        """
        self.llm = llm_provider
        self.templates = self._load_code_templates()

    def _load_code_templates(self) -> Environment:
        """Load code generation templates."""
        templates = {
            # Python pytest template
            "python_pytest": """
import pytest
import requests
import json
from datetime import datetime
from decimal import Decimal
{% if test_data.imports %}
{% for import_stmt in test_data.imports %}
{{ import_stmt }}
{% endfor %}
{% endif %}

class Test{{ test_data.test_suite_name | title | replace(' ', '') }}:
    \"\"\"{{ test_data.description | default('Generated test suite') }}\"\"\"
    
    {% if test_data.setup_class %}
    @classmethod
    def setup_class(cls):
        \"\"\"Set up test class.\"\"\"
        {% for setup_step in test_data.setup_class %}
        {{ setup_step }}
        {% endfor %}
    {% endif %}
    
    {% for test_case in test_data.test_cases %}
    def test_{{ test_case.test_name | lower | replace(' ', '_') | replace('-', '_') }}(self):
        \"\"\"{{ test_case.description }}\"\"\"
        {% if test_case.setup %}
        # Setup
        {% for setup_step in test_case.setup %}
        {{ setup_step }}
        {% endfor %}
        {% endif %}
        
        {% if test_case.test_type == 'api' %}
        # API Test Implementation
        {% if test_case.headers %}
        headers = {{ test_case.headers | tojson }}
        {% endif %}
        {% if test_case.request_body %}
        request_data = {{ test_case.request_body | tojson }}
        {% endif %}
        
        response = requests.{{ test_case.http_method | lower }}(
            url="{{ test_case.endpoint }}",
            {% if test_case.headers %}headers=headers,{% endif %}
            {% if test_case.request_body %}json=request_data,{% endif %}
        )
        
        # Assertions
        assert response.status_code == {{ test_case.expected_status_code }}
        {% if test_case.expected_response %}
        response_data = response.json()
        {% for key, value in test_case.expected_response.items() %}
        assert response_data.get("{{ key }}") == {{ value | tojson }}
        {% endfor %}
        {% endif %}
        
        {% elif test_case.test_type == 'unit' %}
        # Unit Test Implementation
        {% if test_case.test_code %}
        {{ test_case.test_code | indent(8) }}
        {% else %}
        # TODO: Implement test logic
        assert True  # Placeholder
        {% endif %}
        
        {% else %}
        # Generic Test Implementation
        {% for assertion in test_case.assertions %}
        # {{ assertion }}
        {% endfor %}
        assert True  # TODO: Implement assertions
        {% endif %}
        
        {% if test_case.teardown %}
        # Teardown
        {% for teardown_step in test_case.teardown %}
        {{ teardown_step }}
        {% endfor %}
        {% endif %}
    
    {% endfor %}
""",
            # JavaScript Jest template
            "javascript_jest": """
const request = require('supertest');
{% if test_data.imports %}
{% for import_stmt in test_data.imports %}
{{ import_stmt }}
{% endfor %}
{% endif %}

describe('{{ test_data.test_suite_name }}', () => {
    {% if test_data.setup_suite %}
    beforeAll(async () => {
        {% for setup_step in test_data.setup_suite %}
        {{ setup_step }};
        {% endfor %}
    });
    {% endif %}
    
    {% for test_case in test_data.test_cases %}
    {{ "it" if test_case.priority != "low" else "it.skip" }}('{{ test_case.description }}', async () => {
        {% if test_case.setup %}
        // Setup
        {% for setup_step in test_case.setup %}
        {{ setup_step }};
        {% endfor %}
        {% endif %}
        
        {% if test_case.test_type == 'api' %}
        // API Test Implementation
        const response = await request(app)
            .{{ test_case.http_method | lower }}('{{ test_case.endpoint }}')
            {% if test_case.headers %}
            {% for key, value in test_case.headers.items() %}
            .set('{{ key }}', '{{ value }}')
            {% endfor %}
            {% endif %}
            {% if test_case.request_body %}
            .send({{ test_case.request_body | tojson }})
            {% endif %};
        
        expect(response.status).toBe({{ test_case.expected_status_code }});
        {% if test_case.expected_response %}
        {% for key, value in test_case.expected_response.items() %}
        expect(response.body.{{ key }}).toBe({{ value | tojson }});
        {% endfor %}
        {% endif %}
        
        {% else %}
        // Generic Test Implementation
        {% for assertion in test_case.assertions %}
        // {{ assertion }}
        {% endfor %}
        expect(true).toBe(true); // TODO: Implement assertions
        {% endif %}
        
        {% if test_case.teardown %}
        // Teardown
        {% for teardown_step in test_case.teardown %}
        {{ teardown_step }};
        {% endfor %}
        {% endif %}
    });
    
    {% endfor %}
});
""",
            # Selenium WebDriver template
            "python_selenium": """
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
{% if test_data.imports %}
{% for import_stmt in test_data.imports %}
{{ import_stmt }}
{% endfor %}
{% endif %}

class Test{{ test_data.test_suite_name | title | replace(' ', '') }}WebUI:
    \"\"\"{{ test_data.description | default('Generated WebUI test suite') }}\"\"\"
    
    @pytest.fixture(autouse=True)
    def setup_driver(self):
        \"\"\"Set up WebDriver instance.\"\"\"
        self.driver = webdriver.Chrome()  # Configure as needed
        self.wait = WebDriverWait(self.driver, 10)
        yield
        self.driver.quit()
    
    {% for test_case in test_data.test_cases %}
    def test_{{ test_case.test_name | lower | replace(' ', '_') | replace('-', '_') }}(self):
        \"\"\"{{ test_case.description }}\"\"\"
        {% if test_case.page_url %}
        self.driver.get("{{ test_case.page_url }}")
        {% endif %}
        
        {% for step in test_case.test_steps %}
        # {{ step.step }}
        {% if step.action == 'click' %}
        element = self.wait.until(EC.element_to_be_clickable((By.{{ step.locator_type | upper }}, "{{ step.locator }}")))
        element.click()
        {% elif step.action == 'input' %}
        element = self.wait.until(EC.presence_of_element_located((By.{{ step.locator_type | upper }}, "{{ step.locator }}")))
        element.clear()
        element.send_keys("{{ step.data }}")
        {% elif step.action == 'verify' %}
        element = self.wait.until(EC.presence_of_element_located((By.{{ step.locator_type | upper }}, "{{ step.locator }}")))
        assert element.text == "{{ step.expected_result }}"
        {% endif %}
        {% endfor %}
        
        {% for assertion in test_case.assertions %}
        # {{ assertion }}
        {% endfor %}
    
    {% endfor %}
""",
        }

        return Environment(loader=DictLoader(templates))

    async def generate_test_file(
        self,
        test_cases: Dict[str, Any],
        programming_language: str,
        testing_framework: str,
        output_file: Union[str, Path],
        template_override: Optional[str] = None,
    ) -> Path:
        """Generate a test file from test cases.

        Args:
            test_cases: Generated test cases dictionary
            programming_language: Target programming language
            testing_framework: Testing framework
            output_file: Output file path
            template_override: Optional custom template

        Returns:
            Path to generated test file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine template key
        template_key = self._get_template_key(
            programming_language, testing_framework, test_cases
        )

        if template_override:
            template = Template(template_override)
        else:
            template = self.templates.get_template(template_key)

        # Generate code
        code = template.render(test_data=test_cases)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"Generated test file: {output_path}")
        return output_path

    async def generate_multiple_files(
        self,
        test_results: Dict[str, Dict[str, Any]],
        programming_language: str,
        testing_framework: str,
        output_dir: Union[str, Path],
    ) -> List[Path]:
        """Generate multiple test files from test results.

        Args:
            test_results: Dictionary mapping categories to test cases
            programming_language: Target programming language
            testing_framework: Testing framework
            output_dir: Output directory

        Returns:
            List of generated file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []

        for category, result in test_results.items():
            if "error" in result:
                print(f"Skipping {category} due to error: {result['error']}")
                continue

            # Determine file extension
            ext = self._get_file_extension(programming_language)
            filename = f"test_{category}{ext}"
            output_file = output_dir / filename

            try:
                file_path = await self.generate_test_file(
                    test_cases=result["test_cases"],
                    programming_language=programming_language,
                    testing_framework=testing_framework,
                    output_file=output_file,
                )
                generated_files.append(file_path)

            except Exception as e:
                print(f"Failed to generate {category} test file: {e}")

        return generated_files

    async def generate_with_llm(
        self,
        test_cases: Dict[str, Any],
        programming_language: str,
        testing_framework: str,
        output_file: Union[str, Path],
        custom_requirements: Optional[str] = None,
    ) -> Path:
        """Generate test file using LLM for dynamic code generation.

        Args:
            test_cases: Generated test cases
            programming_language: Target programming language
            testing_framework: Testing framework
            output_file: Output file path
            custom_requirements: Custom code generation requirements

        Returns:
            Path to generated test file
        """
        if not self.llm:
            raise ValueError("LLM provider not configured for dynamic code generation")

        prompt = f"""
Generate complete {programming_language} test code using {testing_framework} framework.

Test Cases JSON:
{json.dumps(test_cases, indent=2)}

Requirements:
1. Generate complete, runnable test code
2. Include proper imports and setup
3. Follow {testing_framework} conventions
4. Add appropriate assertions
5. Include error handling and cleanup
6. Use best practices for {programming_language}
{f'7. Custom requirements: {custom_requirements}' if custom_requirements else ''}

Generate only the code, no explanations.
"""

        response = await self.llm.generate(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more consistent code
            max_tokens=4000,
        )

        # Clean up the response (remove markdown formatting if present)
        code = response.content
        if "```" in code:
            # Extract code from markdown blocks
            lines = code.split("\n")
            in_code_block = False
            code_lines = []

            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue

                if in_code_block:
                    code_lines.append(line)

            code = "\n".join(code_lines)

        # Write to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"Generated test file with LLM: {output_path}")
        return output_path

    def _get_template_key(
        self, language: str, framework: str, test_cases: Dict[str, Any]
    ) -> str:
        """Determine the appropriate template key."""
        language = language.lower()
        framework = framework.lower()

        # Check test case category to determine if UI testing
        if any(
            "webui" in str(test_cases).lower(),
            "selenium" in str(test_cases).lower(),
            any(tc.get("page_url") for tc in test_cases.get("test_cases", [])),
        ):
            return f"{language}_selenium"

        # Default mappings
        template_map = {
            ("python", "pytest"): "python_pytest",
            ("javascript", "jest"): "javascript_jest",
            ("typescript", "jest"): "javascript_jest",
        }

        return template_map.get((language, framework), "python_pytest")

    def _get_file_extension(self, language: str) -> str:
        """Get file extension for programming language."""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "csharp": ".cs",
            "go": ".go",
            "ruby": ".rb",
        }

        return extensions.get(language.lower(), ".py")
