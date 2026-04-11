"""
Test Executor Module
Executes generated test scripts and collects results.
Includes WebDriver management utilities.
"""

import sys
import subprocess
import time
import logging
import glob
from pathlib import Path
from typing import List
from dataclasses import dataclass, field


@dataclass
class ExecutionResult:
    """Represents the result of test execution."""
    test_case_id: str
    success: bool
    execution_time: float
    script_path: Path
    error_message: str = ""
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    
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


class TestExecutor:
    """Executes generated test scripts and collects results."""
    
    def __init__(self, logger: logging.Logger):
        """Initialize test executor."""
        self.logger = logger
    
    def execute_test_script(self, script_path: Path, test_case_id: str) -> ExecutionResult:
        """Execute a test script and return results."""
        start_time = time.time()
        
        # Get screenshots before execution (baseline)
        screenshots_before = set(glob.glob("screenshots/*.png"))
        
        try:
            self.logger.info(f"Executing test script: {script_path}")
            
            # Execute the Python script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=120  # Reduced to 2 minutes for faster execution
            )
            
            execution_time = time.time() - start_time
            success = result.returncode == 0
            
            # Collect new screenshots created during execution
            screenshots_after = set(glob.glob("screenshots/*.png"))
            new_screenshots = list(screenshots_after - screenshots_before)
            
            # Filter screenshots for this test case
            test_screenshots = [
                ss for ss in new_screenshots 
                if test_case_id.lower() in Path(ss).name.lower() or 
                   any(keyword in Path(ss).name.lower() for keyword in ["step_", "error_", "final_"])
            ]
            
            # Collect logs
            logs = []
            if result.stdout:
                logs.append(f"STDOUT: {result.stdout}")
            if result.stderr:
                logs.append(f"STDERR: {result.stderr}")
            
            return ExecutionResult(
                test_case_id=test_case_id,
                success=success,
                execution_time=execution_time,
                script_path=script_path,
                error_message=result.stderr if not success else "",
                logs=logs,
                screenshots=test_screenshots
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            # Still collect any screenshots that were taken before timeout
            screenshots_after = set(glob.glob("screenshots/*.png"))
            new_screenshots = list(screenshots_after - screenshots_before)
            test_screenshots = [
                ss for ss in new_screenshots 
                if test_case_id.lower() in Path(ss).name.lower() or 
                   any(keyword in Path(ss).name.lower() for keyword in ["step_", "error_", "final_"])
            ]
            
            return ExecutionResult(
                test_case_id=test_case_id,
                success=False,
                execution_time=execution_time,
                script_path=script_path,
                error_message="Test execution timed out",
                screenshots=test_screenshots
            )
        except Exception as e:
            execution_time = time.time() - start_time
            # Still collect any screenshots that were taken before error
            screenshots_after = set(glob.glob("screenshots/*.png"))
            new_screenshots = list(screenshots_after - screenshots_before)
            test_screenshots = [
                ss for ss in new_screenshots 
                if test_case_id.lower() in Path(ss).name.lower() or 
                   any(keyword in Path(ss).name.lower() for keyword in ["step_", "error_", "final_"])
            ]
            
            return ExecutionResult(
                test_case_id=test_case_id,
                success=False,
                execution_time=execution_time,
                script_path=script_path,
                error_message=str(e),
                screenshots=test_screenshots
            )
    
    # save_script method removed - use ScriptWriter from test_framework instead
    
