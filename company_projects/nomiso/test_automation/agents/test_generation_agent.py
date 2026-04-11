"""Test generation agent using advanced prompting techniques."""

import time
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, AgentResult
from ..generators import TestGenerator
from ..llm import LLMProvider


class TestGenerationAgent(BaseAgent):
    """Agent responsible for generating test cases using LLM and prompt templates."""

    def __init__(self, llm_provider: LLMProvider):
        """Initialize the test generation agent."""
        super().__init__("TestGenerationAgent", llm_provider)
        self.test_generator = TestGenerator(
            llm_provider=llm_provider.provider_name, model=llm_provider.model
        )

    async def execute(self, input_data: Dict[str, Any], **kwargs) -> AgentResult:
        """Execute test case generation.

        Args:
            input_data: Dictionary containing:
                - programming_language: Target programming language
                - testing_framework: Testing framework to use
                - test_cases_file: Path to test scenarios JSON
                - categories: List of test categories to generate
                - knowledge_base_file: Optional knowledge base file
                - generation_config: Optional generation configuration
            **kwargs: Additional configuration

        Returns:
            AgentResult with generated test cases
        """
        start_time = time.time()

        # Validate input
        validation_errors = await self.validate_input(input_data)
        if validation_errors:
            return self._create_result(
                success=False,
                data={},
                errors=validation_errors,
                execution_time=time.time() - start_time,
            )

        try:
            programming_language = input_data["programming_language"]
            testing_framework = input_data["testing_framework"]
            test_cases_file = input_data["test_cases_file"]
            categories = input_data["categories"]
            knowledge_base_file = input_data.get("knowledge_base_file")
            generation_config = input_data.get("generation_config", {})

            results = {}
            warnings = []

            # Generate test cases for each category
            for category in categories:
                try:
                    category_result = await self.test_generator.generate_test_cases(
                        programming_language=programming_language,
                        testing_framework=testing_framework,
                        test_cases_file=test_cases_file,
                        category=category,
                        knowledge_base_file=knowledge_base_file,
                        **generation_config,
                    )

                    results[category] = category_result

                except Exception as e:
                    warnings.append(f"Failed to generate {category} tests: {str(e)}")
                    results[category] = {"error": str(e)}

            # Calculate statistics
            successful_categories = [
                cat for cat, result in results.items() if "error" not in result
            ]
            total_test_cases = sum(
                len(result.get("test_cases", {}).get("test_cases", []))
                for result in results.values()
                if "error" not in result
            )

            execution_time = time.time() - start_time

            return self._create_result(
                success=len(successful_categories) > 0,
                data={
                    "generated_tests": results,
                    "statistics": {
                        "total_categories": len(categories),
                        "successful_categories": len(successful_categories),
                        "failed_categories": len(categories)
                        - len(successful_categories),
                        "total_test_cases": total_test_cases,
                        "categories_generated": successful_categories,
                    },
                    "generation_metadata": {
                        "programming_language": programming_language,
                        "testing_framework": testing_framework,
                        "llm_provider": self.llm.provider_name,
                        "llm_model": self.llm.model,
                        "prompting_techniques_used": self._get_techniques_used(
                            categories
                        ),
                    },
                },
                warnings=warnings,
                execution_time=execution_time,
                metadata={
                    "generation_config": generation_config,
                    "input_files": {
                        "test_cases": test_cases_file,
                        "knowledge_base": knowledge_base_file,
                    },
                },
            )

        except Exception as e:
            return self._create_result(
                success=False,
                data={},
                errors=[f"Test generation failed: {str(e)}"],
                execution_time=time.time() - start_time,
            )

    async def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Validate input data for test generation."""
        errors = []

        required_fields = [
            "programming_language",
            "testing_framework",
            "test_cases_file",
            "categories",
        ]

        for field in required_fields:
            if field not in input_data:
                errors.append(f"Missing required field: {field}")

        # Validate categories
        if "categories" in input_data:
            categories = input_data["categories"]
            if not isinstance(categories, list) or not categories:
                errors.append("Categories must be a non-empty list")
            else:
                available_categories = self.test_generator.get_available_categories()
                invalid_categories = [
                    cat for cat in categories if cat not in available_categories
                ]
                if invalid_categories:
                    errors.append(f"Invalid categories: {invalid_categories}")

        # Validate file paths
        import os

        if "test_cases_file" in input_data:
            if not os.path.exists(input_data["test_cases_file"]):
                errors.append(
                    f"Test cases file not found: {input_data['test_cases_file']}"
                )

        if "knowledge_base_file" in input_data and input_data["knowledge_base_file"]:
            if not os.path.exists(input_data["knowledge_base_file"]):
                errors.append(
                    f"Knowledge base file not found: {input_data['knowledge_base_file']}"
                )

        return errors

    def _get_techniques_used(self, categories: List[str]) -> Dict[str, str]:
        """Get prompting techniques used for each category."""
        technique_map = {
            "api": "Chain-of-Thought (CoT)",
            "unit": "Few-Shot Learning",
            "webui": "Tree-of-Thoughts (ToT)",
            "mobileui": "Role-Based Prompting",
            "edge_cases": "Metacognitive Prompting",
            "performance": "Chain-of-Thought with Self-Consistency",
            "positive": "Few-Shot Learning",
            "negative": "Tree-of-Thoughts",
            "happy_path": "Role-Based Prompting",
            "functional": "Chain-of-Thought",
            "e2e": "Tree-of-Thoughts",
        }

        return {cat: technique_map.get(cat, "Standard Prompting") for cat in categories}

    async def generate_single_category(
        self,
        programming_language: str,
        testing_framework: str,
        test_cases_file: str,
        category: str,
        knowledge_base_file: Optional[str] = None,
        **generation_config,
    ) -> AgentResult:
        """Generate test cases for a single category.

        Convenience method for generating tests for one category.
        """
        input_data = {
            "programming_language": programming_language,
            "testing_framework": testing_framework,
            "test_cases_file": test_cases_file,
            "categories": [category],
            "knowledge_base_file": knowledge_base_file,
            "generation_config": generation_config,
        }

        return await self.execute(input_data)

    def get_supported_categories(self) -> List[str]:
        """Get list of supported test categories."""
        return self.test_generator.get_available_categories()

    def get_category_info(self, category: str) -> Optional[Dict[str, str]]:
        """Get information about a specific category."""
        return self.test_generator.get_category_info(category)

    async def validate_llm_connection(self) -> bool:
        """Validate LLM connection."""
        return await self.test_generator.validate_llm_connection()
