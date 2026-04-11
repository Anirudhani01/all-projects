from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict, total=False):
    # Input
    file_path: str

    # Parsed data
    package: str
    imports: str
    methods: List[Dict[str, Any]]
    selected_method: str
    selected_method_info: Dict[str, Any]

    # Analysis
    analysis: Dict[str, Any]

    # Dependencies
    internal_code: str
    external_code: str

    # Flow Analysis
    flow_analysis: Dict[str, Any]
    flow_analysis_raw: Optional[str]
    flow_name: str  # descriptive name extracted from flow analysis

    # Knowledge Base
    kb_context: str  

    # Generated test (raw + structured parts)
    test_class: str
    final_test_class: str
    test_file_path: str
    raw_output_file: str  # path to saved raw AI response
    test_package: str     # <-- new field for updated test package

    # Validation
    is_valid: bool
    validation_errors: List[str]
    retry_count: int

    # Classification target
    target: str

    # Multi-method orchestration
    completed_methods: List[str]
    all_methods_completed: bool
    auto_continue: bool
    should_continue: bool
    user_stopped: bool
    skipped_methods: List[str]

    manual_continue_prompted: bool     # whether user was prompted after last method
    manual_continue_choice: str        # "stop" or "continue"
    auto_mode_count: int               # number of methods executed so far in auto mode
    auto_mode_limit: int               # max methods to run automatically (0 = unlimited)

    # --- Execution state fields ---
    project_root: str                  # hardcoded project path
    execution_logs: str                # full Gradle stdout/stderr
    execution_passed: bool             # True if test passed, else False
    execution_errors: List[str]        # detailed errors or logs on failure
    execution_error_summary: str       # concise summary of errors if test failed

