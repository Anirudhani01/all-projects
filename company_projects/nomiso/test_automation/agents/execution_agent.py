"""Execution agent for running generated tests and collecting results."""

import asyncio
import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base_agent import BaseAgent, AgentResult
from ..generators import CodeGenerator
from ..llm import LLMProvider


class ExecutionAgent(BaseAgent):
    """Agent responsible for executing generated test cases and collecting results."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """Initialize the execution agent."""
        super().__init__("ExecutionAgent", llm_provider)
        self.code_generator = CodeGenerator(llm_provider)

    async def execute(self, input_data: Dict[str, Any], **kwargs) -> AgentResult:
        """Execute generated test cases.

        Args:
            input_data: Dictionary containing:
                - validated_tests: Validated test cases from ValidationAgent
                - programming_language: Target programming language
                - testing_framework: Testing framework to use
                - execution_config: Optional execution configuration
                - output_directory: Directory for test files and reports
            **kwargs: Additional configuration

        Returns:
            AgentResult with execution results and test reports
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
            validated_tests = input_data["validated_tests"]
            programming_language = input_data["programming_language"]
            testing_framework = input_data["testing_framework"]
            execution_config = input_data.get("execution_config", {})
            output_directory = Path(
                input_data.get("output_directory", "test_execution")
            )

            # Create output directory
            output_directory.mkdir(parents=True, exist_ok=True)

            execution_results = {}
            overall_stats = {
                "total_categories": 0,
                "executed_categories": 0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "execution_time": 0.0,
            }

            # Process each validated category
            for category, validation_result in validated_tests.items():
                if validation_result.get("status") != "passed":
                    execution_results[category] = {
                        "status": "skipped",
                        "reason": "Validation failed",
                        "validation_status": validation_result.get("status"),
                    }
                    continue

                overall_stats["total_categories"] += 1

                # Execute tests for this category
                category_result = await self._execute_category(
                    category,
                    validation_result,
                    programming_language,
                    testing_framework,
                    output_directory,
                    execution_config,
                )

                execution_results[category] = category_result

                if category_result["status"] == "executed":
                    overall_stats["executed_categories"] += 1
                    overall_stats["total_tests"] += category_result["test_stats"][
                        "total"
                    ]
                    overall_stats["passed_tests"] += category_result["test_stats"][
                        "passed"
                    ]
                    overall_stats["failed_tests"] += category_result["test_stats"][
                        "failed"
                    ]
                    overall_stats["skipped_tests"] += category_result["test_stats"][
                        "skipped"
                    ]
                    overall_stats["execution_time"] += category_result["execution_time"]

            # Generate comprehensive test report
            test_report = await self._generate_test_report(
                execution_results, overall_stats, output_directory
            )

            execution_time = time.time() - start_time
            success = (
                overall_stats["executed_categories"] > 0
                and overall_stats["failed_tests"] == 0
            )

            return self._create_result(
                success=success,
                data={
                    "execution_results": execution_results,
                    "overall_statistics": overall_stats,
                    "test_report": test_report,
                    "output_directory": str(output_directory),
                    "pass_rate": overall_stats["passed_tests"]
                    / max(overall_stats["total_tests"], 1),
                },
                warnings=(
                    [] if success else [f"{overall_stats['failed_tests']} tests failed"]
                ),
                execution_time=execution_time,
                metadata={
                    "execution_config": execution_config,
                    "programming_language": programming_language,
                    "testing_framework": testing_framework,
                },
            )

        except Exception as e:
            return self._create_result(
                success=False,
                data={},
                errors=[f"Execution failed: {str(e)}"],
                execution_time=time.time() - start_time,
            )

    async def _execute_category(
        self,
        category: str,
        validation_result: Dict[str, Any],
        programming_language: str,
        testing_framework: str,
        output_directory: Path,
        execution_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute tests for a specific category."""
        try:
            # Extract test data from validation result
            # We need to reconstruct the test data structure
            test_data = validation_result.get("test_data")
            if not test_data:
                return {
                    "status": "failed",
                    "error": "No test data available",
                    "execution_time": 0.0,
                }

            # Generate test file
            test_file_path = await self._generate_test_file(
                category,
                test_data,
                programming_language,
                testing_framework,
                output_directory,
            )

            # Execute the test file
            execution_start = time.time()
            execution_result = await self._run_tests(
                test_file_path, testing_framework, execution_config
            )
            execution_time = time.time() - execution_start

            # Parse test results
            test_stats = self._parse_test_results(execution_result, testing_framework)

            return {
                "status": "executed",
                "test_file": str(test_file_path),
                "execution_time": execution_time,
                "test_stats": test_stats,
                "execution_output": execution_result,
                "command_exit_code": execution_result.get("returncode", 0),
            }

        except Exception as e:
            return {"status": "failed", "error": str(e), "execution_time": 0.0}

    async def _generate_test_file(
        self,
        category: str,
        test_data: Dict[str, Any],
        programming_language: str,
        testing_framework: str,
        output_directory: Path,
    ) -> Path:
        """Generate test file for execution."""
        # Get file extension
        extensions = {"python": ".py", "javascript": ".js", "typescript": ".ts"}
        ext = extensions.get(programming_language.lower(), ".py")

        test_file_path = output_directory / f"test_{category}{ext}"

        # Generate test file using CodeGenerator
        await self.code_generator.generate_test_file(
            test_cases=test_data,
            programming_language=programming_language,
            testing_framework=testing_framework,
            output_file=test_file_path,
        )

        return test_file_path

    async def _run_tests(
        self,
        test_file_path: Path,
        testing_framework: str,
        execution_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run the test file and capture results."""
        # Determine test command based on framework
        command = self._build_test_command(
            test_file_path, testing_framework, execution_config
        )

        try:
            # Run the test command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=test_file_path.parent,
            )

            stdout, stderr = await process.communicate()

            return {
                "command": command,
                "returncode": process.returncode,
                "stdout": stdout.decode("utf-8", errors="ignore"),
                "stderr": stderr.decode("utf-8", errors="ignore"),
            }

        except Exception as e:
            return {
                "command": command,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
            }

    def _build_test_command(
        self,
        test_file_path: Path,
        testing_framework: str,
        execution_config: Dict[str, Any],
    ) -> str:
        """Build the test execution command."""
        framework = testing_framework.lower()

        if framework == "pytest":
            cmd = f"python -m pytest {test_file_path} -v --tb=short"
            if execution_config.get("generate_html_report"):
                report_path = (
                    test_file_path.parent / f"{test_file_path.stem}_report.html"
                )
                cmd += f" --html={report_path} --self-contained-html"
            if execution_config.get("generate_junit_xml"):
                xml_path = test_file_path.parent / f"{test_file_path.stem}_results.xml"
                cmd += f" --junit-xml={xml_path}"

        elif framework == "jest":
            cmd = f"npx jest {test_file_path} --verbose"
            if execution_config.get("generate_html_report"):
                cmd += " --coverage --coverageReporters=html"

        elif framework == "unittest":
            cmd = f"python -m unittest {test_file_path.stem} -v"

        else:
            # Generic Python execution
            cmd = f"python {test_file_path}"

        return cmd

    def _parse_test_results(
        self, execution_result: Dict[str, Any], testing_framework: str
    ) -> Dict[str, Any]:
        """Parse test execution results."""
        stdout = execution_result.get("stdout", "")
        stderr = execution_result.get("stderr", "")
        returncode = execution_result.get("returncode", 0)

        # Initialize stats
        stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0}

        # Parse based on framework
        framework = testing_framework.lower()

        if framework == "pytest":
            stats = self._parse_pytest_results(stdout, stderr)
        elif framework == "jest":
            stats = self._parse_jest_results(stdout, stderr)
        elif framework == "unittest":
            stats = self._parse_unittest_results(stdout, stderr)
        else:
            # Generic parsing - look for common patterns
            if returncode == 0:
                stats["passed"] = 1
                stats["total"] = 1
            else:
                stats["failed"] = 1
                stats["total"] = 1

        return stats

    def _parse_pytest_results(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse pytest output."""
        stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0}

        # Look for pytest summary line
        for line in stdout.split("\n"):
            if "passed" in line or "failed" in line or "error" in line:
                # Parse lines like "2 passed, 1 failed in 0.03s"
                import re

                passed_match = re.search(r"(\d+) passed", line)
                if passed_match:
                    stats["passed"] = int(passed_match.group(1))

                failed_match = re.search(r"(\d+) failed", line)
                if failed_match:
                    stats["failed"] = int(failed_match.group(1))

                error_match = re.search(r"(\d+) error", line)
                if error_match:
                    stats["errors"] = int(error_match.group(1))

                skipped_match = re.search(r"(\d+) skipped", line)
                if skipped_match:
                    stats["skipped"] = int(skipped_match.group(1))

        stats["total"] = (
            stats["passed"] + stats["failed"] + stats["errors"] + stats["skipped"]
        )
        return stats

    def _parse_jest_results(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse Jest output."""
        stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0}

        # Look for Jest summary
        for line in stdout.split("\n"):
            if "Tests:" in line:
                import re

                passed_match = re.search(r"(\d+) passed", line)
                if passed_match:
                    stats["passed"] = int(passed_match.group(1))

                failed_match = re.search(r"(\d+) failed", line)
                if failed_match:
                    stats["failed"] = int(failed_match.group(1))

                skipped_match = re.search(r"(\d+) skipped", line)
                if skipped_match:
                    stats["skipped"] = int(skipped_match.group(1))

        stats["total"] = stats["passed"] + stats["failed"] + stats["skipped"]
        return stats

    def _parse_unittest_results(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse unittest output."""
        stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "errors": 0}

        # Look for unittest summary
        for line in stderr.split("\n"):
            if "Ran" in line and "test" in line:
                import re

                match = re.search(r"Ran (\d+) test", line)
                if match:
                    stats["total"] = int(match.group(1))

            if "FAILED" in line:
                failure_match = re.search(r"failures=(\d+)", line)
                if failure_match:
                    stats["failed"] = int(failure_match.group(1))

                error_match = re.search(r"errors=(\d+)", line)
                if error_match:
                    stats["errors"] = int(error_match.group(1))

        stats["passed"] = stats["total"] - stats["failed"] - stats["errors"]
        return stats

    async def _generate_test_report(
        self,
        execution_results: Dict[str, Any],
        overall_stats: Dict[str, Any],
        output_directory: Path,
    ) -> Dict[str, Any]:
        """Generate comprehensive test execution report."""
        report_data = {
            "execution_summary": overall_stats,
            "category_results": execution_results,
            "recommendations": [],
            "detailed_analysis": {},
        }

        # Analyze results and generate recommendations
        if overall_stats["failed_tests"] > 0:
            failure_rate = overall_stats["failed_tests"] / overall_stats["total_tests"]
            if failure_rate > 0.2:
                report_data["recommendations"].append(
                    "High failure rate detected. Review test implementation and requirements."
                )

        if overall_stats["executed_categories"] < overall_stats["total_categories"]:
            skipped = (
                overall_stats["total_categories"] - overall_stats["executed_categories"]
            )
            report_data["recommendations"].append(
                f"{skipped} categories were skipped due to validation issues."
            )

        # Identify problematic categories
        for category, result in execution_results.items():
            if result.get("status") == "failed":
                report_data["detailed_analysis"][category] = {
                    "issue": "Execution failed",
                    "error": result.get("error", "Unknown error"),
                }
            elif result.get("status") == "executed":
                test_stats = result.get("test_stats", {})
                if test_stats.get("failed", 0) > 0:
                    report_data["detailed_analysis"][category] = {
                        "issue": "Test failures",
                        "failed_count": test_stats["failed"],
                        "failure_rate": test_stats["failed"]
                        / max(test_stats["total"], 1),
                    }

        # Save report to file
        report_file = output_directory / "test_execution_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, default=str)

        # Generate HTML report if LLM is available
        html_report = None
        if self.llm:
            html_report = await self._generate_html_report(
                report_data, output_directory
            )

        return {
            "report_file": str(report_file),
            "html_report": html_report,
            "summary": report_data["execution_summary"],
            "recommendations": report_data["recommendations"],
        }

    async def _generate_html_report(
        self, report_data: Dict[str, Any], output_directory: Path
    ) -> Optional[str]:
        """Generate HTML test report using LLM."""
        try:
            prompt = f"""
Generate an HTML test execution report based on the following data:

{json.dumps(report_data, indent=2, default=str)}

Create a comprehensive, professional HTML report that includes:
1. Executive summary with key metrics
2. Category-wise test results
3. Failure analysis and recommendations
4. Visual elements (use CSS for styling)
5. Responsive design

The report should be self-contained with embedded CSS.
"""

            response = await self.llm.generate(
                prompt=prompt, temperature=0.3, max_tokens=4000
            )

            # Save HTML report
            html_file = output_directory / "test_execution_report.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(response.content)

            return str(html_file)

        except Exception as e:
            return f"HTML report generation failed: {str(e)}"

    async def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Validate input data for execution agent."""
        errors = []

        required_fields = [
            "validated_tests",
            "programming_language",
            "testing_framework",
        ]
        for field in required_fields:
            if field not in input_data:
                errors.append(f"Missing required field: {field}")

        validated_tests = input_data.get("validated_tests", {})
        if not isinstance(validated_tests, dict):
            errors.append("validated_tests must be a dictionary")
        elif not validated_tests:
            errors.append("validated_tests is empty")

        return errors
