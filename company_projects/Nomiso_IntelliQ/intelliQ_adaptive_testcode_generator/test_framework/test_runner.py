"""
Test Runner Module

Orchestrates the complete test execution workflow including test generation,
script writing, execution, and reporting. This provides a high-level interface
for running test automation workflows.
"""

import time
import datetime
import logging
import os
from typing import List, Dict, Union, Optional
from pathlib import Path
import json

from .base_generator import AITestCaseCodeGenerator
from .test_context import TestContext
from .script_writer import ScriptWriter


class ExecutionResult:
    """Represents the result of test execution."""
    
    def __init__(self, test_case_id: str, success: bool, execution_time: float,
                 script_path: Path, error_message: str = "", 
                 screenshots: List[str] = None, logs: List[str] = None):
        self.test_case_id = test_case_id
        self.success = success
        self.execution_time = execution_time
        self.script_path = script_path
        self.error_message = error_message
        self.screenshots = screenshots or []
        self.logs = logs or []
    
    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON serialization."""
        return {
            'test_case_id': self.test_case_id,
            'success': self.success,
            'execution_time': self.execution_time,
            'script_path': str(self.script_path),
            'error_message': self.error_message,
            'screenshots': self.screenshots,
            'logs': self.logs
        }


class TestRunner:
    """
    Orchestrates the complete test automation workflow.
    
    This class provides a high-level interface for running test cases through
    the complete pipeline: generation, writing, execution, and reporting.
    """
    
    def __init__(self, context: TestContext, generator: AITestCaseCodeGenerator = None):
        """
        Initialize the test runner.
        
        Args:
            context (TestContext): Test execution context
            generator (AITestCaseCodeGenerator): Code generator instance
        """
        self.context = context
        self.generator = generator
        self.script_writer = ScriptWriter(context)
        self.logger = context.get_logger(__name__)
        
        if not generator:
            self.logger.warning("No generator provided - will need to set generator before running tests")
    
    def set_generator(self, generator: AITestCaseCodeGenerator) -> None:
        """
        Set the code generator to use.
        
        Args:
            generator (AITestCaseCodeGenerator): Code generator instance
        """
        self.generator = generator
        self.logger.info(f"Generator set to: {generator.get_framework_name()}")
    
    def run_single_test(self, test_case: Dict, previous_test_cases: List[Dict] = None) -> ExecutionResult:
        """
        Run a single test case through the complete pipeline.
        
        Args:
            test_case (Dict): Test case data
            previous_test_cases (List[Dict]): Previous test cases for context
            
        Returns:
            ExecutionResult: Result of the test execution
        """
        if not self.generator:
            raise ValueError("No code generator available - use set_generator() first")
        
        test_case_id = test_case.get('test_case_id', 'unknown')
        start_time = time.time()
        
        try:
            self.logger.info(f"Running test case: {test_case_id}")
            
            # Step 1: Generate script code
            self.logger.debug(f"Generating script for: {test_case_id}")
            script_code = self.generator.generate_script(test_case, self.context, previous_test_cases)
            
            if not script_code.strip():
                raise RuntimeError("Generated script code is empty")
            
            # Step 2: Write script to file
            self.logger.debug(f"Writing script for: {test_case_id}")
            script_path = self.script_writer.save_script(script_code, test_case_id)
            
            # Step 3: Execute the script (if enabled)
            enable_execution = os.getenv('ENABLE_SCRIPT_EXECUTION', 'true').lower() == 'true'
            
            if enable_execution:
                self.logger.debug(f"Executing script: {script_path}")
                result = self._execute_script(script_path, test_case_id)
                
                execution_time = time.time() - start_time
                result.execution_time = execution_time
                
                self.logger.info(f"Test case {test_case_id} {'PASSED' if result.success else 'FAILED'} "
                               f"in {execution_time:.2f} seconds")
                return result
            else:
                # Script generated but not executed
                execution_time = time.time() - start_time
                self.logger.info(f"Test case {test_case_id} script generated (execution disabled) "
                               f"in {execution_time:.2f} seconds")
                
                return ExecutionResult(
                    test_case_id=test_case_id,
                    success=True,  # Generation successful
                    execution_time=execution_time,
                    script_path=script_path,
                    error_message="",
                    screenshots=[],
                    logs=[f"Script generated at: {script_path}"]
                )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Test case {test_case_id} failed: {str(e)}")
            
            return ExecutionResult(
                test_case_id=test_case_id,
                success=False,
                execution_time=execution_time,
                script_path=self.context.get_script_path(test_case_id),
                error_message=str(e)
            )
    
    def run_multiple_tests(self, test_cases: List[Dict]) -> List[ExecutionResult]:
        """
        Run multiple test cases with context continuity.
        
        Args:
            test_cases (List[Dict]): List of test cases to execute
            
        Returns:
            List[ExecutionResult]: Results of all test executions
        """
        if not self.generator:
            raise ValueError("No code generator available - use set_generator() first")
        
        self.logger.info(f"Running {len(test_cases)} test cases")
        
        results = []
        processed_test_cases = []  # Accumulate for context
        
        for i, test_case in enumerate(test_cases):
            try:
                test_case_id = test_case.get('test_case_id', f'test_{i}')
                
                # Update locators if in dynamic mode
                if self.context.locator_extraction_mode == 'dynamic':
                    locators = self.generator.extract_locators(test_case, self.context)
                    self.context.update_locators(locators)
                
                # Run the test with previous context
                result = self.run_single_test(test_case, processed_test_cases.copy())
                results.append(result)
                
                # Add to processed list for future context (only if successful)
                if result.success:
                    processed_test_cases.append({
                        'test_case_id': test_case['test_case_id'],
                        'test_case_description': test_case.get('test_case_description', ''),
                        'test_steps': test_case.get('test_steps', []),
                        'flow_index': test_case.get('flow_index', 1),
                        'test_case_type': test_case.get('test_case_type', 'positive')
                    })
                
            except Exception as e:
                self.logger.error(f"Failed to process test case {i}: {str(e)}")
                
                # Create error result
                error_result = ExecutionResult(
                    test_case_id=test_case.get('test_case_id', f'test_{i}'),
                    success=False,
                    execution_time=0.0,
                    script_path=Path(""),
                    error_message=str(e)
                )
                results.append(error_result)
        
        self.logger.info(f"Completed {len(test_cases)} test cases. "
                        f"Passed: {sum(1 for r in results if r.success)}, "
                        f"Failed: {sum(1 for r in results if not r.success)}")
        
        return results
    
    def run_from_json(self, json_input: Union[str, List[Dict], Path]) -> List[ExecutionResult]:
        """
        Run test cases from JSON input.
        
        Args:
            json_input (Union[str, List[Dict], Path]): JSON data or file path
            
        Returns:
            List[ExecutionResult]: Results of all test executions
        """
        try:
            test_cases = self._load_test_cases_from_json(json_input)
            return self.run_multiple_tests(test_cases)
            
        except Exception as e:
            self.logger.error(f"Failed to run tests from JSON: {str(e)}")
            raise
    
    def generate_report(self, results: List[ExecutionResult]) -> Dict:
        """
        Generate execution report from test results.
        
        Args:
            results (List[ExecutionResult]): Test execution results
            
        Returns:
            Dict: Report data
        """
        timestamp = datetime.datetime.now()
        
        report_data = {
            'timestamp': timestamp.isoformat(),
            'framework': self.generator.get_framework_name() if self.generator else 'unknown',
            'total_tests': len(results),
            'passed_tests': sum(1 for r in results if r.success),
            'failed_tests': sum(1 for r in results if not r.success),
            'total_execution_time': sum(r.execution_time for r in results),
            'results': [r.to_dict() for r in results]
        }
        
        # Save report to file
        report_timestamp = timestamp.strftime('%Y%m%d_%H%M%S')
        report_path = self.context.get_report_path(report_timestamp)
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Test report generated: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save report: {str(e)}")
        
        return report_data
    
    def _execute_script(self, script_path: Path, test_case_id: str) -> ExecutionResult:
        """
        Execute a test script using the appropriate executor.
        
        Args:
            script_path (Path): Path to the script to execute
            test_case_id (str): Test case identifier
            
        Returns:
            ExecutionResult: Execution result
        """
        # Import the specific executor based on framework
        if self.context.test_framework == 'selenium':
            from ..selenium_script_generator.test_executor import TestExecutor
            executor = TestExecutor(self.logger)
            return executor.execute_test_script(script_path, test_case_id)
        else:
            # For future framework support
            raise NotImplementedError(f"Executor not implemented for framework: {self.context.test_framework}")
    
    def _load_test_cases_from_json(self, json_input: Union[str, List[Dict], Path]) -> List[Dict]:
        """
        Load test cases from JSON input and validate them.
        
        Args:
            json_input (Union[str, List[Dict], Path]): JSON data or file path
            
        Returns:
            List[Dict]: Validated test cases
        """
        try:
            # Handle different input types
            if isinstance(json_input, (str, Path)):
                with open(json_input, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = json_input
            
            # Validate and process test cases
            test_cases = []
            for test_data in data:
                # Basic validation
                test_case_id = test_data.get('test_case_id', '').strip()
                test_case_description = test_data.get('test_case_description', '').strip()
                
                if not test_case_id:
                    raise ValueError("Test case ID cannot be empty")
                if not test_case_description:
                    raise ValueError("Test case description cannot be empty")
                
                # Validate test steps
                raw_steps = test_data.get('test_steps', [])
                validated_steps = []
                
                for step_data in raw_steps:
                    if isinstance(step_data, dict):
                        step_number = step_data.get('step_number', 0)
                        step_description = step_data.get('step', '').strip()
                        expected_output = step_data.get('expected_output', '').strip()
                        
                        if not step_description:
                            raise ValueError(f"Step {step_number}: Step description cannot be empty")
                        if not expected_output:
                            raise ValueError(f"Step {step_number}: Expected output cannot be empty")
                        
                        validated_steps.append({
                            'step_number': step_number,
                            'step': step_description,
                            'expected_output': expected_output
                        })
                    else:
                        raise ValueError(f"Invalid step format: {step_data}")
                
                # Create validated test case
                test_case = {
                    'test_case_id': test_case_id,
                    'test_case_description': test_case_description,
                    'test_steps': validated_steps,
                    'test_case_type': test_data.get('test_case_type', 'positive'),
                    'flow_index': test_data.get('flow_index', 1),
                    'summary': test_data.get('summary', test_case_description)
                }
                
                test_cases.append(test_case)
            
            self.logger.info(f"Successfully loaded {len(test_cases)} test cases from JSON")
            return test_cases
            
        except Exception as e:
            raise ValueError(f"Failed to load test cases from JSON: {str(e)}")