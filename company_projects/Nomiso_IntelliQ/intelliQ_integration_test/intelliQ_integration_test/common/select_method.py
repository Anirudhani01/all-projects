
from common.agent_state import AgentState
from central_logger.logger import get_logger

logger = get_logger(__name__)

def select_method(state: AgentState) -> AgentState:
    """
    Select target method for test generation with interactive/manual and auto modes.
    Prompts Stop/Continue only in manual mode after previous method completion.
    """
    logger.info(" Selecting method for test generation")

    methods = state.get('methods', [])

    if not methods:
        logger.error(" No methods found to select from")
        state.setdefault('validation_errors', []).append("No methods found in the parsed file")
        return state

    completed = state.get("completed_methods", [])
    skipped = state.get("skipped_methods", [])
    remaining_methods = [m for m in methods if m["name"] not in completed + skipped]

    if not remaining_methods:
        logger.info(" No remaining methods to select")
        state["all_methods_completed"] = True
        return state

    # ---------------- Auto mode ---------------- #
    if state.get("auto_continue"):
        limit = state.get("auto_mode_limit", 0)
        count = state.get("auto_mode_count", 0)
        if limit == 0 or count < limit:
            next_method = remaining_methods[0]  # pick next available
            state["selected_method"] = next_method["name"]
            state["selected_method_info"] = next_method
            state["should_continue"] = True
            
            # *** COMPLETE STATE RESET FOR NEW METHOD ***
            state["retry_count"] = 0
            state.pop("last_failed_method", None)
            state.pop("execution_logs", None)
            state.pop("execution_error_summary", None)
            
            logger.info(f" Auto-selected method: {next_method['name']} ({count+1}/{limit if limit>0 else '∞'})")
            print(f"\n Auto-processing method: {next_method['name']}")
            return state
        else:
            logger.info(" Reached auto mode limit")
            state["should_continue"] = False
            return state

    # ---------------- Manual mode ---------------- #
    # Prompt Stop/Continue only if previous method completed
    if state.get("manual_continue_prompted", False) and state.get("manual_continue_choice") == "stop":
        state["user_stopped"] = True
        state["should_continue"] = False
        logger.info(" User chose to stop in manual mode")
        return state

    # Reset previous selection
    state["selected_method"] = ""
    state["selected_method_info"] = {}
    state["manual_continue_prompted"] = False
    state["manual_continue_choice"] = ""
    
    # *** COMPLETE STATE RESET FOR NEW METHOD (MANUAL MODE) ***
    state["retry_count"] = 0
    state.pop("last_failed_method", None)
    state.pop("execution_logs", None)
    state.pop("execution_error_summary", None)

    # Display available methods
    print("\n" + "="*60)
    print("AVAILABLE METHODS FOR TEST GENERATION")
    print("="*60)
    for i, method in enumerate(remaining_methods, 1):
        modifiers = ' '.join(method.get('modifiers', []))
        return_type = method.get('return_type', 'void')
        method_name = method.get('name', '')
        signature = method.get('signature', '')
        print(f"{i:2d}. {modifiers} {return_type} {method_name}()")
        if signature:
            print(f"    Signature: {signature}")
        print()

    # Get user selection
    try:
        while True:
            choice = input(f"Select method (1-{len(remaining_methods)}): ").strip()
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(remaining_methods):
                    selected_method = remaining_methods[choice_num - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(remaining_methods)}")
            else:
                print("Please enter a valid number")
    except KeyboardInterrupt:
        print("\n Operation cancelled by user")
        state["user_stopped"] = True
        state["should_continue"] = False
        logger.info(" User cancelled method selection")
        return state

    state['selected_method'] = selected_method['name']
    state['selected_method_info'] = selected_method

    print(f"\n Selected method: {selected_method['name']}")
    logger.info(f" Selected method: {selected_method['name']}")

    return state