# generate_test/generate_test.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # Load .env
from common.agent_state import AgentState
from central_logger.logger import get_logger
from java_core.prompts import CONTROLLER_CONFIG, SERVICE_CONFIG
from java_core.nodes.extract_dependencies import generate_test_file_path, extract_method_code


logger = get_logger(__name__)
client = OpenAI()
# Validate required env variables
required_vars = ["MODEL", "TEMPERATURE", "MAX_TOKENS"]
for var in required_vars:
    if var not in os.environ:
        raise RuntimeError(f"Missing required env variable: {var}")

MODEL = os.environ["MODEL"]
TEMPERATURE = float(os.environ["TEMPERATURE"])
MAX_TOKENS = int(os.environ["MAX_TOKENS"])

# Debug flag to dump extracted method code for verification
DEBUG_METHOD_DUMP = True



def generate_test(state: AgentState) -> AgentState:
    """
    Generate JUnit 5 + Mockito integration test using GPT.
    Always enforces IntegrationTest suffix.
    """
    logger.info(" Generating integration test")

    try:
        # --- Flow name handling ---
        flow_name = state.get("flow_name")
        if not flow_name:
            logger.warning(" No flow_name found in state, using fallback")
            flow_name = "UnknownFlow"
            state["flow_name"] = flow_name

        class_name = f"{flow_name}IntegrationTest"
        logger.info(f" Target test class: {class_name}")

       
        

        # --- Select config ---
        target_type = state.get("target", "service")
        config = CONTROLLER_CONFIG if target_type == "controller" else SERVICE_CONFIG
        logger.info(f" Using config for: {target_type}")

        # --- Build prompt ---
        prompt = _build_test_generation_prompt(state, config, class_name)

        # Retry context
        if state.get("execution_logs") and state.get("test_class"):
            prompt += f"""

### PREVIOUS TEST FAILURE CONTEXT
The previously generated test failed. Consider the following generated code and Gradle execution logs to produce a corrected test.

#### Previously Generated Test Code:
{state['test_class']}

#### Execution Logs:
{state['execution_logs']}

# This is retry attempt {state.get('retry_count', 1)}
"""
            logger.info(f" Appended previous test and logs for retry attempt {state.get('retry_count', 1)}")

        # --- Call GPT ---
        response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": config['system_prompt']},
                {"role": "user", "content": prompt}
            ]
        )

        raw_ai_response = response.choices[0].message.content.strip()

        
        # --- No cleaning, trust AI ---
        test_class = raw_ai_response

        # --- Update state ---
        state['test_class'] = test_class
        state['test_file_path'] = generate_test_file_path(state, flow_name)
       
        logger.info(" Integration test generated successfully")

        return state

    except Exception as e:
        logger.error(f" Error generating test: {e}")
        state['validation_errors'] = state.get('validation_errors', []) + [f"Test generation error: {str(e)}"]
        return state


def _build_test_generation_prompt(state: AgentState, config: dict, class_name: str) -> str:
    """Build comprehensive test generation prompt."""

    flow_analysis_section = ""
    if state.get("flow_analysis"):
        flow_analysis_section = f"\n### Flow Analysis:\n```json\n{json.dumps(state['flow_analysis'], indent=2)}\n```\n"
    elif state.get("flow_analysis_raw"):
        flow_analysis_section = f"\n### Flow Analysis (Raw):\n{state['flow_analysis_raw']}\n"

    internal_deps_section = f"\n### Internal Dependencies:\n```java\n{state['internal_code']}\n```\n" if state.get('internal_code') else "\n### Internal Dependencies:\n```\n```\n"
    external_deps_section = f"\n### External Dependencies:\n```java\n{state['external_code']}\n```\n" if state.get('external_code') else "\n### External Dependencies:\n```\n```\n"
    imports_section = f"\n### Required Imports:\n```java\n{state['imports']}\n```\n" if state.get('imports') else "\n### Required Imports:\n```\n```\n"
   
    selected_method = state.get('selected_method', '')
    selected_method_cap = selected_method[0].upper() + selected_method[1:] if selected_method else "TestMethod"

    # Extract method code using imported function
    method_code = extract_method_code(state['file_path'], selected_method)
    if not method_code:
        method_code = f"// Method {selected_method} could not be extracted"
        logger.warning(f"Could not extract method code for {selected_method}")


    prompt = config['user_prompt'].format(
        package=state.get('package', ''),
        imports_section=imports_section,
        method_code_section=method_code,
        flow_analysis_section=flow_analysis_section,
        internal_deps_section=internal_deps_section,
        external_deps_section=external_deps_section,
        flow_name=class_name,
        selected_method_cap=selected_method_cap
    )

    return prompt