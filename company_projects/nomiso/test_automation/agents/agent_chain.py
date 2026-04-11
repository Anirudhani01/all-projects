"""Agent chain for orchestrating the complete test automation workflow."""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, AgentResult
from .test_generation_agent import TestGenerationAgent
from .validation_agent import ValidationAgent
from .execution_agent import ExecutionAgent
from ..llm import LLMProvider, LLMFactory


class AgentChain:
    """Orchestrates the complete test automation workflow through agent chain."""

    def __init__(
        self, llm_provider: str = "ollama", model: Optional[str] = None, **llm_kwargs
    ):
        """Initialize the agent chain.

        Args:
            llm_provider: LLM provider name ('ollama' or 'openai')
            model: Model name (defaults based on provider)
            **llm_kwargs: Additional LLM configuration
        """
        self.llm = LLMFactory.create_provider(llm_provider, model, **llm_kwargs)

        # Initialize agents
        self.generation_agent = TestGenerationAgent(self.llm)
        self.validation_agent = ValidationAgent(self.llm)
        self.execution_agent = ExecutionAgent(self.llm)

        self.execution_history: List[Dict[str, Any]] = []

    async def run_complete_workflow(
        self,
        programming_language: str,
        testing_framework: str,
        test_cases_file: str,
        categories: List[str],
        knowledge_base_file: Optional[str] = None,
        output_directory: Optional[str] = None,
        workflow_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run the complete test automation workflow.

        Args:
            programming_language: Target programming language
            testing_framework: Testing framework to use
            test_cases_file: Path to test scenarios JSON
            categories: List of test categories to generate
            knowledge_base_file: Optional knowledge base file
            output_directory: Optional output directory
            workflow_config: Optional workflow configuration

        Returns:
            Complete workflow results
        """
        start_time = time.time()
        workflow_id = f"workflow_{int(start_time)}"

        if not output_directory:
            output_directory = f"test_automation_output_{int(start_time)}"

        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)

        workflow_result = {
            "workflow_id": workflow_id,
            "status": "running",
            "stages": {},
            "overall_metrics": {},
            "recommendations": [],
            "output_directory": str(output_path),
        }

        config = workflow_config or {}

        try:
            # Stage 1: Test Generation
            print("🤖 Stage 1: Generating test cases...")
            generation_result = await self._run_generation_stage(
                programming_language=programming_language,
                testing_framework=testing_framework,
                test_cases_file=test_cases_file,
                categories=categories,
                knowledge_base_file=knowledge_base_file,
                config=config.get("generation", {}),
            )

            workflow_result["stages"]["generation"] = {
                "status": "completed" if generation_result.success else "failed",
                "result": generation_result.dict(),
                "duration": generation_result.execution_time,
            }

            if not generation_result.success:
                workflow_result["status"] = "failed"
                workflow_result["error"] = "Test generation failed"
                return workflow_result

            # Stage 2: Validation
            print("✅ Stage 2: Validating generated test cases...")
            validation_result = await self._run_validation_stage(
                generated_tests=generation_result.data["generated_tests"],
                config=config.get("validation", {}),
            )

            workflow_result["stages"]["validation"] = {
                "status": "completed" if validation_result.success else "failed",
                "result": validation_result.dict(),
                "duration": validation_result.execution_time,
            }

            # Stage 3: Execution (optional, based on validation results)
            execute_tests = config.get("execution", {}).get("enabled", True)
            validation_pass_required = config.get("execution", {}).get(
                "require_validation_pass", False
            )

            if execute_tests and (
                not validation_pass_required or validation_result.success
            ):
                print("🚀 Stage 3: Executing test cases...")
                execution_result = await self._run_execution_stage(
                    validated_tests=validation_result.data["validation_results"],
                    programming_language=programming_language,
                    testing_framework=testing_framework,
                    output_directory=str(output_path),
                    config=config.get("execution", {}),
                )

                workflow_result["stages"]["execution"] = {
                    "status": "completed" if execution_result.success else "failed",
                    "result": execution_result.dict(),
                    "duration": execution_result.execution_time,
                }
            else:
                workflow_result["stages"]["execution"] = {
                    "status": "skipped",
                    "reason": (
                        "Validation failed"
                        if validation_pass_required and not validation_result.success
                        else "Execution disabled"
                    ),
                }

            # Calculate overall metrics and recommendations
            workflow_result.update(
                self._calculate_workflow_metrics(
                    workflow_result, generation_result, validation_result
                )
            )

            workflow_result["status"] = "completed"
            workflow_result["total_duration"] = time.time() - start_time

            # Save workflow results
            await self._save_workflow_results(workflow_result, output_path)

            # Record execution
            self.execution_history.append(workflow_result)

            return workflow_result

        except Exception as e:
            workflow_result["status"] = "failed"
            workflow_result["error"] = str(e)
            workflow_result["total_duration"] = time.time() - start_time
            return workflow_result

    async def _run_generation_stage(
        self,
        programming_language: str,
        testing_framework: str,
        test_cases_file: str,
        categories: List[str],
        knowledge_base_file: Optional[str],
        config: Dict[str, Any],
    ) -> AgentResult:
        """Run the test generation stage."""
        generation_input = {
            "programming_language": programming_language,
            "testing_framework": testing_framework,
            "test_cases_file": test_cases_file,
            "categories": categories,
            "knowledge_base_file": knowledge_base_file,
            "generation_config": config,
        }

        return await self.generation_agent.execute(generation_input)

    async def _run_validation_stage(
        self, generated_tests: Dict[str, Any], config: Dict[str, Any]
    ) -> AgentResult:
        """Run the validation stage."""
        validation_input = {
            "generated_tests": generated_tests,
            "validation_config": config,
        }

        return await self.validation_agent.execute(validation_input)

    async def _run_execution_stage(
        self,
        validated_tests: Dict[str, Any],
        programming_language: str,
        testing_framework: str,
        output_directory: str,
        config: Dict[str, Any],
    ) -> AgentResult:
        """Run the execution stage."""
        execution_input = {
            "validated_tests": validated_tests,
            "programming_language": programming_language,
            "testing_framework": testing_framework,
            "output_directory": output_directory,
            "execution_config": config,
        }

        return await self.execution_agent.execute(execution_input)

    def _calculate_workflow_metrics(
        self,
        workflow_result: Dict[str, Any],
        generation_result: AgentResult,
        validation_result: AgentResult,
    ) -> Dict[str, Any]:
        """Calculate overall workflow metrics and recommendations."""
        metrics = {
            "generation_success": generation_result.success,
            "validation_success": validation_result.success,
            "categories_processed": 0,
            "total_test_cases": 0,
            "validation_pass_rate": 0.0,
            "overall_score": 0.0,
        }

        recommendations = []

        # Extract generation metrics
        if generation_result.success:
            gen_stats = generation_result.data.get("statistics", {})
            metrics["categories_processed"] = gen_stats.get("successful_categories", 0)
            metrics["total_test_cases"] = gen_stats.get("total_test_cases", 0)

            if gen_stats.get("failed_categories", 0) > 0:
                recommendations.append(
                    f"{gen_stats['failed_categories']} categories failed generation. "
                    "Review input data and prompts."
                )

        # Extract validation metrics
        if validation_result.success:
            val_metrics = validation_result.data.get("metrics", {})
            metrics["validation_pass_rate"] = val_metrics.get("pass_rate", 0.0)
            metrics["overall_score"] = val_metrics.get("overall_score", 0.0)

            if metrics["validation_pass_rate"] < 0.8:
                recommendations.append(
                    "Low validation pass rate. Consider improving test case quality."
                )

            if metrics["overall_score"] < 0.7:
                recommendations.append(
                    "Overall test quality score is below threshold. Review generated tests."
                )

        # Execution metrics (if available)
        execution_stage = workflow_result["stages"].get("execution", {})
        if execution_stage.get("status") == "completed":
            exec_result = execution_stage["result"]["data"]
            metrics["execution_success"] = exec_result.get("success", False)
            metrics["test_pass_rate"] = exec_result.get("pass_rate", 0.0)

            if metrics["test_pass_rate"] < 0.9:
                recommendations.append(
                    "Test execution pass rate is low. Review test implementation."
                )

        return {"overall_metrics": metrics, "recommendations": recommendations}

    async def _save_workflow_results(
        self, workflow_result: Dict[str, Any], output_path: Path
    ) -> None:
        """Save complete workflow results to files."""
        import json

        # Save main workflow results
        workflow_file = output_path / "workflow_results.json"
        with open(workflow_file, "w", encoding="utf-8") as f:
            json.dump(workflow_result, f, indent=2, default=str)

        # Generate summary report
        summary = self._generate_workflow_summary(workflow_result)
        summary_file = output_path / "workflow_summary.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"\n📁 Workflow results saved to: {output_path}")
        print(f"📊 Summary report: {summary_file}")
        print(f"📄 Detailed results: {workflow_file}")

    def _generate_workflow_summary(self, workflow_result: Dict[str, Any]) -> str:
        """Generate a markdown summary of the workflow execution."""
        summary = f"""# Test Automation Workflow Summary

## Workflow Information
- **Workflow ID**: {workflow_result['workflow_id']}
- **Status**: {workflow_result['status']}
- **Total Duration**: {workflow_result.get('total_duration', 0):.2f} seconds
- **Output Directory**: {workflow_result['output_directory']}

## Stage Results

### 🤖 Test Generation
"""

        gen_stage = workflow_result["stages"].get("generation", {})
        if gen_stage:
            gen_result = gen_stage.get("result", {}).get("data", {})
            stats = gen_result.get("statistics", {})

            summary += f"""- **Status**: {gen_stage['status']}
- **Duration**: {gen_stage.get('duration', 0):.2f} seconds
- **Categories Processed**: {stats.get('total_categories', 0)}
- **Successful Categories**: {stats.get('successful_categories', 0)}
- **Total Test Cases Generated**: {stats.get('total_test_cases', 0)}

"""

        summary += "### ✅ Validation\n"
        val_stage = workflow_result["stages"].get("validation", {})
        if val_stage:
            val_result = val_stage.get("result", {}).get("data", {})
            metrics = val_result.get("metrics", {})

            summary += f"""- **Status**: {val_stage['status']}
- **Duration**: {val_stage.get('duration', 0):.2f} seconds
- **Validation Pass Rate**: {metrics.get('pass_rate', 0):.1%}
- **Overall Quality Score**: {metrics.get('overall_score', 0):.2f}

"""

        summary += "### 🚀 Execution\n"
        exec_stage = workflow_result["stages"].get("execution", {})
        if exec_stage.get("status") == "completed":
            exec_result = exec_stage.get("result", {}).get("data", {})
            stats = exec_result.get("overall_statistics", {})

            summary += f"""- **Status**: {exec_stage['status']}
- **Duration**: {exec_stage.get('duration', 0):.2f} seconds
- **Tests Executed**: {stats.get('total_tests', 0)}
- **Tests Passed**: {stats.get('passed_tests', 0)}
- **Tests Failed**: {stats.get('failed_tests', 0)}
- **Pass Rate**: {exec_result.get('pass_rate', 0):.1%}

"""
        elif exec_stage.get("status") == "skipped":
            summary += f"- **Status**: Skipped ({exec_stage.get('reason', 'Unknown reason')})\n\n"

        # Add overall metrics
        overall_metrics = workflow_result.get("overall_metrics", {})
        if overall_metrics:
            summary += f"""## Overall Metrics
- **Categories Processed**: {overall_metrics.get('categories_processed', 0)}
- **Total Test Cases**: {overall_metrics.get('total_test_cases', 0)}
- **Validation Success**: {overall_metrics.get('validation_success', False)}
- **Generation Success**: {overall_metrics.get('generation_success', False)}

"""

        # Add recommendations
        recommendations = workflow_result.get("recommendations", [])
        if recommendations:
            summary += "## Recommendations\n"
            for i, rec in enumerate(recommendations, 1):
                summary += f"{i}. {rec}\n"
            summary += "\n"

        summary += f"""## Conclusion
The test automation workflow has {'completed successfully' if workflow_result['status'] == 'completed' else 'failed'}. 
{"All stages executed without critical issues." if workflow_result['status'] == 'completed' else "Please review the errors and recommendations above."}
"""

        return summary

    async def run_generation_only(
        self,
        programming_language: str,
        testing_framework: str,
        test_cases_file: str,
        categories: List[str],
        knowledge_base_file: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Run only the test generation stage."""
        return await self._run_generation_stage(
            programming_language,
            testing_framework,
            test_cases_file,
            categories,
            knowledge_base_file,
            config or {},
        )

    async def run_validation_only(
        self, generated_tests: Dict[str, Any], config: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Run only the validation stage."""
        return await self._run_validation_stage(generated_tests, config or {})

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get workflow execution history."""
        return self.execution_history

    def get_agent_histories(self) -> Dict[str, List[AgentResult]]:
        """Get execution history for all agents."""
        return {
            "generation": self.generation_agent.get_execution_history(),
            "validation": self.validation_agent.get_execution_history(),
            "execution": self.execution_agent.get_execution_history(),
        }

    async def validate_setup(self) -> Dict[str, bool]:
        """Validate that all components are properly set up."""
        validation_results = {
            "llm_connection": False,
            "generation_agent": False,
            "validation_agent": False,
            "execution_agent": False,
        }

        try:
            # Test LLM connection
            validation_results["llm_connection"] = (
                await self.generation_agent.validate_llm_connection()
            )

            # Test agents (basic setup validation)
            validation_results["generation_agent"] = self.generation_agent is not None
            validation_results["validation_agent"] = self.validation_agent is not None
            validation_results["execution_agent"] = self.execution_agent is not None

        except Exception as e:
            print(f"Setup validation error: {e}")

        return validation_results
