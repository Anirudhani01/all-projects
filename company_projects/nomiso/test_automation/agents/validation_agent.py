"""Validation agent for test case quality and accuracy checking."""

import json
import time
from typing import Any, Dict, List, Optional
from pathlib import Path

from .base_agent import BaseAgent, AgentResult
from ..llm import LLMProvider


class ValidationAgent(BaseAgent):
    """Agent responsible for validating generated test cases."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """Initialize the validation agent."""
        super().__init__("ValidationAgent", llm_provider)
        self.validation_rules = self._load_validation_rules()

    async def execute(self, input_data: Dict[str, Any], **kwargs) -> AgentResult:
        """Execute test case validation.

        Args:
            input_data: Dictionary containing:
                - generated_tests: Generated test cases from TestGenerationAgent
                - validation_config: Optional validation configuration
                - strict_mode: Boolean for strict validation
            **kwargs: Additional configuration

        Returns:
            AgentResult with validation results
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
            generated_tests = input_data["generated_tests"]
            validation_config = input_data.get("validation_config", {})
            strict_mode = validation_config.get("strict_mode", False)

            validation_results = {}
            overall_errors = []
            overall_warnings = []

            # Validate each category
            for category, test_data in generated_tests.items():
                if "error" in test_data:
                    validation_results[category] = {
                        "status": "skipped",
                        "reason": "Generation failed",
                    }
                    continue

                category_result = await self._validate_category(
                    category, test_data, validation_config
                )
                validation_results[category] = category_result

                if category_result["errors"]:
                    overall_errors.extend(
                        [f"{category}: {err}" for err in category_result["errors"]]
                    )

                if category_result["warnings"]:
                    overall_warnings.extend(
                        [f"{category}: {warn}" for warn in category_result["warnings"]]
                    )

            # Calculate overall metrics
            metrics = self._calculate_validation_metrics(validation_results)

            # AI-powered quality assessment if LLM available
            quality_assessment = None
            if self.llm:
                quality_assessment = await self._ai_quality_assessment(
                    generated_tests, validation_results
                )

            execution_time = time.time() - start_time
            success = metrics["overall_score"] >= (0.8 if strict_mode else 0.6)

            return self._create_result(
                success=success,
                data={
                    "validation_results": validation_results,
                    "metrics": metrics,
                    "quality_assessment": quality_assessment,
                    "summary": {
                        "total_categories": len(validation_results),
                        "passed_categories": metrics["categories_passed"],
                        "failed_categories": metrics["categories_failed"],
                        "overall_score": metrics["overall_score"],
                        "recommendation": "PASS" if success else "FAIL",
                    },
                },
                errors=overall_errors if strict_mode else [],
                warnings=overall_warnings + (overall_errors if not strict_mode else []),
                execution_time=execution_time,
                metadata={
                    "validation_config": validation_config,
                    "strict_mode": strict_mode,
                    "validation_rules_version": "1.0",
                },
            )

        except Exception as e:
            return self._create_result(
                success=False,
                data={},
                errors=[f"Validation failed: {str(e)}"],
                execution_time=time.time() - start_time,
            )

    async def _validate_category(
        self, category: str, test_data: Dict[str, Any], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate test cases for a specific category."""
        errors = []
        warnings = []
        scores = {}

        # Check if test_cases exist
        if "test_cases" not in test_data:
            errors.append("Missing test_cases structure")
            return {
                "status": "failed",
                "errors": errors,
                "warnings": warnings,
                "scores": scores,
            }

        test_cases_data = test_data["test_cases"]

        # Validate structure
        structure_score = self._validate_structure(
            test_cases_data, category, errors, warnings
        )
        scores["structure"] = structure_score

        # Validate content quality
        content_score = self._validate_content_quality(
            test_cases_data, category, errors, warnings
        )
        scores["content_quality"] = content_score

        # Validate completeness
        completeness_score = self._validate_completeness(
            test_cases_data, category, errors, warnings
        )
        scores["completeness"] = completeness_score

        # Validate category-specific requirements
        category_score = self._validate_category_specific(
            test_cases_data, category, errors, warnings
        )
        scores["category_specific"] = category_score

        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)
        scores["overall"] = overall_score

        status = "passed" if overall_score >= 0.7 and not errors else "failed"

        return {
            "status": status,
            "errors": errors,
            "warnings": warnings,
            "scores": scores,
            "test_count": len(test_cases_data.get("test_cases", [])),
        }

    def _validate_structure(
        self,
        test_data: Dict[str, Any],
        category: str,
        errors: List[str],
        warnings: List[str],
    ) -> float:
        """Validate test case structure."""
        score = 1.0

        # Check required top-level fields
        required_fields = ["test_suite_name", "framework", "language", "test_cases"]
        for field in required_fields:
            if field not in test_data:
                errors.append(f"Missing required field: {field}")
                score -= 0.25

        # Validate test cases array
        test_cases = test_data.get("test_cases", [])
        if not isinstance(test_cases, list):
            errors.append("test_cases must be an array")
            score -= 0.5
        elif len(test_cases) == 0:
            warnings.append("No test cases generated")
            score -= 0.2
        else:
            # Validate individual test case structure
            for i, test_case in enumerate(test_cases):
                if not isinstance(test_case, dict):
                    errors.append(f"Test case {i} is not a valid object")
                    score -= 0.1
                    continue

                # Check for required test case fields
                required_test_fields = ["test_name", "description"]
                for field in required_test_fields:
                    if field not in test_case:
                        warnings.append(f"Test case {i} missing {field}")
                        score -= 0.05

        return max(0.0, score)

    def _validate_content_quality(
        self,
        test_data: Dict[str, Any],
        category: str,
        errors: List[str],
        warnings: List[str],
    ) -> float:
        """Validate content quality of test cases."""
        score = 1.0
        test_cases = test_data.get("test_cases", [])

        if not test_cases:
            return 0.0

        for i, test_case in enumerate(test_cases):
            # Check test name quality
            test_name = test_case.get("test_name", "")
            if len(test_name) < 10:
                warnings.append(f"Test case {i} has very short name")
                score -= 0.05
            elif len(test_name) > 100:
                warnings.append(f"Test case {i} has very long name")
                score -= 0.02

            # Check description quality
            description = test_case.get("description", "")
            if len(description) < 20:
                warnings.append(f"Test case {i} has insufficient description")
                score -= 0.05

            # Check for meaningful assertions/validations
            assertions = test_case.get("assertions", [])
            expected_results = test_case.get("expected_results", [])
            if not assertions and not expected_results:
                warnings.append(f"Test case {i} lacks validation criteria")
                score -= 0.1

        return max(0.0, score)

    def _validate_completeness(
        self,
        test_data: Dict[str, Any],
        category: str,
        errors: List[str],
        warnings: List[str],
    ) -> float:
        """Validate completeness of test coverage."""
        score = 1.0
        test_cases = test_data.get("test_cases", [])

        if not test_cases:
            return 0.0

        # Check for variety in test types
        priorities = set()
        test_types = set()

        for test_case in test_cases:
            priority = test_case.get("priority", "medium")
            priorities.add(priority)

            test_type = test_case.get("test_type", category)
            test_types.add(test_type)

        # Should have multiple priorities
        if len(priorities) < 2:
            warnings.append("Limited priority diversity in test cases")
            score -= 0.1

        # Category-specific completeness checks
        expected_minimums = {
            "api": 5,
            "unit": 8,
            "webui": 4,
            "mobileui": 4,
            "edge_cases": 6,
            "performance": 3,
            "positive": 5,
            "negative": 5,
            "happy_path": 3,
            "functional": 6,
            "e2e": 3,
        }

        min_expected = expected_minimums.get(category, 3)
        if len(test_cases) < min_expected:
            warnings.append(
                f"Only {len(test_cases)} test cases for {category}, expected at least {min_expected}"
            )
            score -= 0.2

        return max(0.0, score)

    def _validate_category_specific(
        self,
        test_data: Dict[str, Any],
        category: str,
        errors: List[str],
        warnings: List[str],
    ) -> float:
        """Validate category-specific requirements."""
        score = 1.0
        test_cases = test_data.get("test_cases", [])

        if category == "api":
            score = self._validate_api_tests(test_cases, errors, warnings)
        elif category == "webui":
            score = self._validate_webui_tests(test_cases, errors, warnings)
        elif category == "mobileui":
            score = self._validate_mobile_tests(test_cases, errors, warnings)
        elif category == "performance":
            score = self._validate_performance_tests(test_cases, errors, warnings)
        elif category == "edge_cases":
            score = self._validate_edge_case_tests(test_cases, errors, warnings)

        return max(0.0, score)

    def _validate_api_tests(
        self, test_cases: List[Dict], errors: List[str], warnings: List[str]
    ) -> float:
        """Validate API-specific test requirements."""
        score = 1.0

        http_methods = set()
        status_codes = set()

        for test_case in test_cases:
            # Check for HTTP method
            method = test_case.get("http_method")
            if method:
                http_methods.add(method.upper())
            else:
                warnings.append(
                    f"API test '{test_case.get('test_name')}' missing HTTP method"
                )
                score -= 0.1

            # Check for expected status code
            status_code = test_case.get("expected_status_code")
            if status_code:
                status_codes.add(status_code)
            else:
                warnings.append(
                    f"API test '{test_case.get('test_name')}' missing expected status code"
                )
                score -= 0.1

        # Should test multiple HTTP methods
        if len(http_methods) < 2:
            warnings.append("API tests should cover multiple HTTP methods")
            score -= 0.15

        # Should test various status codes
        if len(status_codes) < 3:
            warnings.append("API tests should cover various HTTP status codes")
            score -= 0.1

        return score

    def _validate_webui_tests(
        self, test_cases: List[Dict], errors: List[str], warnings: List[str]
    ) -> float:
        """Validate WebUI-specific test requirements."""
        score = 1.0

        has_user_interactions = False
        has_navigation = False
        has_form_tests = False

        for test_case in test_cases:
            test_steps = test_case.get("test_steps", [])

            for step in test_steps:
                if isinstance(step, dict):
                    action = step.get("action", "").lower()
                    if action in ["click", "input", "select"]:
                        has_user_interactions = True
                    if "navigate" in action or "goto" in action:
                        has_navigation = True
                    if action in ["input", "submit", "form"]:
                        has_form_tests = True

        if not has_user_interactions:
            warnings.append("WebUI tests should include user interactions")
            score -= 0.2

        if not has_navigation:
            warnings.append("WebUI tests should include navigation scenarios")
            score -= 0.15

        return score

    def _validate_mobile_tests(
        self, test_cases: List[Dict], errors: List[str], warnings: List[str]
    ) -> float:
        """Validate mobile-specific test requirements."""
        score = 1.0

        has_gestures = False
        has_orientation = False
        has_platform_specific = False

        for test_case in test_cases:
            gestures = test_case.get("gestures", [])
            if gestures:
                has_gestures = True

            test_steps = test_case.get("test_steps", [])
            for step in test_steps:
                if isinstance(step, dict):
                    if "orientation" in str(step).lower():
                        has_orientation = True

            platform = test_case.get("platform", "")
            if platform in ["iOS", "Android"]:
                has_platform_specific = True

        if not has_gestures:
            warnings.append("Mobile tests should include gesture interactions")
            score -= 0.2

        if not has_platform_specific:
            warnings.append("Mobile tests should specify target platforms")
            score -= 0.15

        return score

    def _validate_performance_tests(
        self, test_cases: List[Dict], errors: List[str], warnings: List[str]
    ) -> float:
        """Validate performance-specific test requirements."""
        score = 1.0

        has_load_pattern = False
        has_objectives = False

        for test_case in test_cases:
            if "load_pattern" in test_case:
                has_load_pattern = True

            if "performance_objectives" in test_case:
                has_objectives = True

        if not has_load_pattern:
            warnings.append("Performance tests should define load patterns")
            score -= 0.3

        if not has_objectives:
            warnings.append("Performance tests should define performance objectives")
            score -= 0.3

        return score

    def _validate_edge_case_tests(
        self, test_cases: List[Dict], errors: List[str], warnings: List[str]
    ) -> float:
        """Validate edge case test requirements."""
        score = 1.0

        edge_types = set()

        for test_case in test_cases:
            edge_type = test_case.get("edge_case_type", "")
            if edge_type:
                edge_types.add(edge_type)

        if len(edge_types) < 3:
            warnings.append(
                "Edge case tests should cover multiple types of edge conditions"
            )
            score -= 0.2

        return score

    async def _ai_quality_assessment(
        self, generated_tests: Dict[str, Any], validation_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Use AI to assess test quality."""
        if not self.llm:
            return None

        try:
            prompt = f"""
Analyze the following generated test cases and validation results for quality assessment:

Generated Tests Summary:
{json.dumps({k: {"test_count": len(v.get("test_cases", {}).get("test_cases", [])), 
               "category": k} for k, v in generated_tests.items() if "error" not in v}, indent=2)}

Validation Results:
{json.dumps(validation_results, indent=2)}

Provide a quality assessment including:
1. Overall test coverage adequacy
2. Test case design quality
3. Potential gaps or improvements
4. Recommendation (EXCELLENT/GOOD/FAIR/POOR)

Respond in JSON format:
{{
  "overall_quality": "EXCELLENT|GOOD|FAIR|POOR",
  "coverage_assessment": "string",
  "design_quality": "string", 
  "improvement_suggestions": ["string"],
  "confidence_score": 0.0-1.0
}}
"""

            response = await self.llm.generate_structured(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "overall_quality": {
                            "type": "string",
                            "enum": ["EXCELLENT", "GOOD", "FAIR", "POOR"],
                        },
                        "coverage_assessment": {"type": "string"},
                        "design_quality": {"type": "string"},
                        "improvement_suggestions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "confidence_score": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                        },
                    },
                },
                temperature=0.3,
            )

            return json.loads(response.content)

        except Exception as e:
            return {"error": f"AI assessment failed: {str(e)}"}

    def _calculate_validation_metrics(
        self, validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall validation metrics."""
        total_categories = len(validation_results)
        passed_categories = sum(
            1
            for result in validation_results.values()
            if result.get("status") == "passed"
        )
        failed_categories = total_categories - passed_categories

        # Calculate average scores
        all_scores = []
        for result in validation_results.values():
            if "scores" in result and "overall" in result["scores"]:
                all_scores.append(result["scores"]["overall"])

        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

        return {
            "total_categories": total_categories,
            "categories_passed": passed_categories,
            "categories_failed": failed_categories,
            "pass_rate": (
                passed_categories / total_categories if total_categories > 0 else 0.0
            ),
            "overall_score": overall_score,
            "average_scores": {
                "structure": sum(
                    r.get("scores", {}).get("structure", 0)
                    for r in validation_results.values()
                )
                / total_categories,
                "content_quality": sum(
                    r.get("scores", {}).get("content_quality", 0)
                    for r in validation_results.values()
                )
                / total_categories,
                "completeness": sum(
                    r.get("scores", {}).get("completeness", 0)
                    for r in validation_results.values()
                )
                / total_categories,
            },
        }

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules configuration."""
        return {
            "min_test_cases_per_category": {
                "api": 5,
                "unit": 8,
                "webui": 4,
                "mobileui": 4,
                "edge_cases": 6,
                "performance": 3,
                "positive": 5,
                "negative": 5,
                "happy_path": 3,
                "functional": 6,
                "e2e": 3,
            },
            "required_fields": {
                "all": ["test_name", "description"],
                "api": ["http_method", "expected_status_code"],
                "webui": ["test_steps"],
                "performance": ["load_pattern", "performance_objectives"],
            },
            "quality_thresholds": {
                "overall_score_pass": 0.7,
                "structure_score_pass": 0.8,
                "content_quality_pass": 0.7,
                "completeness_pass": 0.6,
            },
        }

    async def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Validate input data for validation agent."""
        errors = []

        if "generated_tests" not in input_data:
            errors.append("Missing required field: generated_tests")

        generated_tests = input_data.get("generated_tests", {})
        if not isinstance(generated_tests, dict):
            errors.append("generated_tests must be a dictionary")
        elif not generated_tests:
            errors.append("generated_tests is empty")

        return errors
