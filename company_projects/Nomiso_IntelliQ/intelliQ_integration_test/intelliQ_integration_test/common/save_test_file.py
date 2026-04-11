import os
from common.agent_state import AgentState
from central_logger.logger import get_logger

logger = get_logger(__name__)

def save_test_file(state: AgentState) -> AgentState:
    """
    Save the test class to disk unconditionally (skip validation).
    """
    logger.info(" Saving test file")
    
    test_class = state.get('test_class', '')
    test_file_path = state.get("test_file_path", "")
    skipped_methods = state.get("skipped_methods", [])
    flow_name = state.get("flow_name", "<unknown>")

    if not test_class:
        error_msg = "Test class content is empty"
        logger.error(f" {error_msg}")
        state.setdefault('validation_errors', []).append(error_msg)
        return state

    if not test_file_path:
        error_msg = "Test file path is missing"
        logger.error(f" {error_msg}")
        state.setdefault('validation_errors', []).append(error_msg)
        return state

    try:
        # Ensure directory exists
        test_dir = os.path.dirname(test_file_path)
        os.makedirs(test_dir, exist_ok=True)

        logger.debug(f" Writing {flow_name}IntegrationTest → {test_file_path}")

        # Write the test file unconditionally
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_class)

        state["final_test_saved"] = True
        logger.info(f" Test file saved to: {test_file_path}")
        
        if skipped_methods:
            logger.warning(f" Some methods were skipped: {skipped_methods}")
            state["skipped_in_save"] = skipped_methods

    except Exception as e:
        logger.error(f" Error saving test file: {e}")
        state.setdefault('validation_errors', []).append(f"Save error: {str(e)}")

    return state

