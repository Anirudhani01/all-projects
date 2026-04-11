from common.agent_state import AgentState
from central_logger.logger import get_logger
import subprocess
import os
import platform
from dotenv import load_dotenv

logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Validate project root
if "PROJECT_ROOT" not in os.environ:
    raise RuntimeError("Missing required env variable: PROJECT_ROOT")

project_root = os.environ["PROJECT_ROOT"]



def execute_test(state: AgentState) -> AgentState:
    """
    Execute the generated test using Gradle and capture results.
    Updates execution_passed, execution_errors, execution_error_summary, retry_count, 
    completed_methods, and manual/auto continuation flags in state.
    """
    logger.info(" Executing generated test")
    
    
    # Get current method being tested
    current_method = state.get("selected_method")
    
    # Increment retry count for current method
    state["retry_count"] = state.get("retry_count", 0) + 1

    
    
    state["project_root"] = project_root

    # Detect OS and select Gradle wrapper relative to project root
    gradle_cmd = "gradlew.bat" if platform.system() == "Windows" else "./gradlew"
    gradle_cmd = os.path.join(project_root, gradle_cmd)

    # Get test class name
    test_class_name = _get_test_class_name(state)
    if not test_class_name:
        logger.error(" Could not determine test class name")
        state["execution_passed"] = False
        state["execution_errors"] = ["Could not determine test class name"]
        # Track failed method
        if current_method:
            state["last_failed_method"] = current_method
        return state

    logger.info(f" Running test: {test_class_name} (Attempt {state['retry_count']})")

    cmd = [
        gradle_cmd, "test",
        f"--tests={test_class_name}",
        "--info",
        "--stacktrace",
        "--offline"
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300,  # 5 minutes
            check=False
        )

        # Save logs
        state["execution_logs"] = result.stdout

        if result.returncode == 0:
            logger.info(f" Test {test_class_name} passed")
            state["execution_passed"] = True
            state["execution_errors"] = []
            state.pop("execution_error_summary", None)

            # Clear failure tracking on success
            state.pop("last_failed_method", None)
            state["retry_count"] = 0  # Reset for next method

            # Update completed methods
            if current_method and current_method not in state.get("completed_methods", []):
                state.setdefault("completed_methods", []).append(current_method)

            # NO MORE MANUAL PROMPTS HERE - Let orchestration handle it

        else:
            logger.error(f" Test {test_class_name} failed (exit code: {result.returncode})")
            state["execution_passed"] = False
            state["execution_errors"] = [result.stdout]
            state["execution_error_summary"] = _extract_error_summary(result.stdout)
            
            # Track failed method
            if current_method:
                state["last_failed_method"] = current_method
                logger.info(f" Marked method '{current_method}' for retry")

    except subprocess.TimeoutExpired as e:
        logger.error(" Test execution timed out")
        state["execution_passed"] = False
        state["execution_errors"] = ["Test execution timed out after 300 seconds"]
        state["execution_error_summary"] = "Timeout"
        # Track failed method
        if current_method:
            state["last_failed_method"] = current_method

    except FileNotFoundError as e:
        logger.error(f" File not found error: {e}")
        state["execution_passed"] = False
        state["execution_errors"] = [f"FileNotFoundError: {str(e)}"]
        state["execution_error_summary"] = "Gradle wrapper or project root not found"
        # Track failed method
        if current_method:
            state["last_failed_method"] = current_method

    except Exception as e:
        logger.error(f" Error executing test: {e}")
        state["execution_passed"] = False
        state["execution_errors"] = [f"Execution error: {str(e)}"]
        state["execution_error_summary"] = str(e)
        # Track failed method
        if current_method:
            state["last_failed_method"] = current_method

    return state

# Helper functions remain unchanged
def _get_test_class_name(state: AgentState) -> str:
    test_file_path = state.get("test_file_path", "")
    if test_file_path:
        filename = os.path.basename(test_file_path)
        if filename.endswith(".java"):
            class_name = filename[:-5]
            package_name = _extract_package_name(state)
            return f"{package_name}.{class_name}" if package_name else class_name
    test_code = state.get("final_test_class") or state.get("test_class", "")
    if test_code:
        package_name = _extract_package_name(state)
        class_name = _extract_class_name(test_code)
        return f"{package_name}.{class_name}" if package_name and class_name else class_name
    return ""

def _extract_package_name(state: AgentState) -> str:
    test_code = state.get("final_test_class") or state.get("test_class", "")
    if not test_code:
        return ""
    for line in test_code.splitlines():
        line = line.strip()
        if line.startswith("package ") and line.endswith(";"):
            return line[8:-1]
    return ""

def _extract_class_name(code: str) -> str:
    for line in code.splitlines():
        line = line.strip()
        if "public class " in line:
            parts = line.split()
            try:
                class_idx = parts.index("class") + 1
                return parts[class_idx].rstrip("{")
            except (ValueError, IndexError):
                continue
    return ""

def _extract_error_summary(gradle_output: str) -> str:
    lines = gradle_output.splitlines()
    error_lines = [
        line for line in lines
        if any(pattern in line.lower() for pattern in [
            "failed", "error", "exception", "assertion",
            "could not resolve", "compilation failed", "test failed", "caused by"
        ])
    ]
    return "\n".join(error_lines[:10]) if error_lines else ""
