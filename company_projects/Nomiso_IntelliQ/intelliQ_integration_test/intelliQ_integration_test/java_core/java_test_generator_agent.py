import os
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from common.agent_state import AgentState
from central_logger.logger import setup_logging, get_logger
from base_factory.test_generator_factory import BaseTestGeneratorAgent

# Import node functions
from java_core.nodes.parse_input import parse_input
from common.select_method import select_method
from common.analyze_method import analyze_method
from java_core.nodes.extract_dependencies import extract_dependencies
from common.flow_analyzer import flow_analyzer
from common.generate_test import generate_test
from common.save_test_file import save_test_file
from java_core.nodes.execute_test import execute_test

# Setup logging
setup_logging()
logger = get_logger(__name__)


class JavaTestGeneratorAgent(BaseTestGeneratorAgent):
    """Java-specific implementation of test generator agent - fully automated"""
    
    def __init__(self):
        """Initialize Java test generator agent in fully automated mode"""
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow with clean flow logic"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("parse_input", parse_input)
        workflow.add_node("select_method", self._auto_select_method)
        workflow.add_node("analyze_method", analyze_method)
        workflow.add_node("extract_dependencies", extract_dependencies)
        workflow.add_node("flow_analyzer", flow_analyzer)
        workflow.add_node("generate_test", generate_test)
        workflow.add_node("save_test_file", save_test_file)
        workflow.add_node("execute_test", self._execute_and_handle_completion)

        # Flow edges
        workflow.add_edge("parse_input", "select_method")

        # From select_method: either stop (if user stopped/all completed) or continue
        workflow.add_conditional_edges(
            "select_method",
            lambda state: (
                END  # Stop when user stopped or all methods completed
                if state.get("user_stopped") or state.get("all_methods_completed")
                else "analyze_method"  # Continue with selected method
            ),
            {END: END, "analyze_method": "analyze_method"},
        )

        workflow.add_edge("analyze_method", "extract_dependencies")
        workflow.add_edge("extract_dependencies", "flow_analyzer")
        workflow.add_edge("flow_analyzer", "generate_test")
        workflow.add_edge("generate_test", "save_test_file")
        workflow.add_edge("save_test_file", "execute_test")

        # From execute_test: retry if failed, or back to select_method if passed/max retries
        workflow.add_conditional_edges(
            "execute_test",
            lambda state: (
                "generate_test"  # Retry same method
                if not state.get("execution_passed") and state.get("retry_count", 0) < 3
                else (END if state.get("user_stopped") or state.get("all_methods_completed") 
                      else "select_method")  # Stop if limit reached or continue
            ),
            {"generate_test": "generate_test", "select_method": "select_method", END: END},
        )

        workflow.set_entry_point("parse_input")
        return workflow.compile()

    def _auto_select_method(self, state: AgentState) -> AgentState:
        """Auto-select the next unprocessed public method (fully automated)"""
        logger.info(" Auto-selecting method for test generation")
        methods = state.get("methods", [])
        completed_methods = state.get("completed_methods", [])
        skipped_methods = state.get("skipped_methods", [])

        remaining_methods = [m for m in methods if m["name"] not in completed_methods + skipped_methods]
        if not remaining_methods:
            logger.info(" All methods have been completed")
            state["all_methods_completed"] = True
            return state

        next_method = next((m for m in remaining_methods if "public" in m.get("modifiers", [])), remaining_methods[0])
        state["selected_method"] = next_method["name"]
        state["selected_method_info"] = next_method

        # Reset per-method state
        state["retry_count"] = 0
        state.pop("last_failed_method", None)
        state.pop("execution_logs", None)
        state.pop("execution_error_summary", None)

        state["should_continue"] = True

        total_methods = len(methods)
        completed_count = len(completed_methods)
        skipped_count = len(skipped_methods)
        print(
            f"\n Progress: {completed_count} completed, {skipped_count} skipped, "
            f"{len(remaining_methods)} remaining (out of {total_methods} total methods)"
        )
        print(f" Auto-processing method: {next_method['name']}")

        return state

    def _execute_and_handle_completion(self, state: AgentState) -> AgentState:
        """Execute test and handle completion logic (fully automated)"""
        # Execute the test
        state = execute_test(state)
        method_name = state.get("selected_method")

        # Handle successful test execution
        if state.get("execution_passed") and method_name:
            logger.info(f" Test {method_name} passed successfully")

            # Add completed method to the list immediately
            completed = state.setdefault("completed_methods", [])
            if method_name not in completed:
                completed.append(method_name)

            # CRITICAL: Clear all retry-related state for next method
            state["retry_count"] = 0
            state.pop("last_failed_method", None)
            state.pop("execution_logs", None)
            state.pop("execution_error_summary", None)
            state.pop("last_test_class", None)
            state.pop("previous_error", None)
            
            # Continue automatically to next method
            state["should_continue"] = True
            logger.info(" Automatically continuing to next method")

        # Handle failed test execution - check retry limit
        elif not state.get("execution_passed"):
            retry_count = state.get("retry_count", 0)
            if retry_count >= 3:
                # Max retries exceeded - skip method
                skipped = state.setdefault("skipped_methods", [])
                if method_name and method_name not in skipped:
                    skipped.append(method_name)
                    logger.warning(f" Retry limit exceeded for {method_name}, skipping to next method")
                state["retry_count"] = 0
                state["should_continue"] = True

        return state

    def generate_and_execute(self, file_path: str) -> Dict[str, Any]:
        """Generate integration test for the given Java file"""
        logger.info(f" Starting Java test generation for: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.endswith(".java"):
            raise ValueError(f"Expected Java file, got: {file_path}")

        initial_state: AgentState = {
            "file_path": file_path,
            "package": "",
            "imports": "",
            "methods": [],
            "selected_method": "",
            "analysis": {},
            "internal_code": "",
            "external_code": "",
            "flow_analysis": {},
            "flow_name": "UnknownFlow",
            "test_class": "",
            "final_test_class": "",
            "test_file_path": "",
            "raw_output_file": "",
            "is_valid": False,
            "validation_errors": [],
            "retry_count": 0,
            "kb_context": "",
            "selected_method_info": {},
            "completed_methods": [],
            "skipped_methods": [],
            "all_methods_completed": False,
            "user_stopped": False,
            "should_continue": False,
        }

        try:
            result = self.graph.invoke(initial_state)
            completed = result.get("completed_methods", [])
            skipped = result.get("skipped_methods", [])
            selected = result.get("selected_method", "")
            logger.info(f" Methods completed so far: {completed}")
            logger.info(f" Methods skipped: {skipped}")
            if selected:
                logger.info(f" Last processed method: {selected}")

            if result.get("validation_errors"):
                logger.error(f" Validation errors: {result['validation_errors']}")
                return {"success": False, "errors": result["validation_errors"], "result": result}

            if not result.get("final_test_class") and not result.get("test_class"):
                logger.warning(" No test class generated")
                return {"success": False, "errors": ["No test generated"], "result": result}

            # Final summary
            total = len(result.get("methods", []))
            done = len(completed)
            skip = len(skipped)
            logger.info(f" Java test generation finished — {done} completed, {skip} skipped, {total - done - skip} remaining out of {total}")

            if result.get("test_file_path"):
                logger.info(f" Test saved to: {result['test_file_path']}")

            return {"success": True, "test_file_path": result.get("test_file_path", ""), "result": result}

        except KeyboardInterrupt:
            logger.info(" Java test generation cancelled by user")
            current_state = result if 'result' in locals() else initial_state
            current_state["user_stopped"] = True
            logger.info(" Last merged test file already auto-saved — nothing more to save")
            return {"success": True, "test_file_path": current_state.get("test_file_path", ""), "result": current_state}

        except Exception as e:
            logger.error(f" Error during Java test generation: {e}")
            return {"success": False, "errors": [str(e)], "result": None}