import json
import re
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv
from common.agent_state import AgentState
from central_logger.logger import get_logger
from java_core.prompts import FLOW_ANALYSIS_PROMPT
import os

load_dotenv()
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


def flow_analyzer(state: AgentState) -> AgentState:
    """
    Analyze control/data flow using GPT, storing JSON in state['flow_analysis'].
    Extracts a descriptive flow_name for test class naming.
    Leaves test class and file path generation to generate_test node.
    """
    method_name = state.get("selected_method", "<unknown>")
    logger.info(f" Performing flow analysis for: {method_name}")

    try:
        method_code = state.get("selected_method_info", {}).get("code", "")
        if not method_code:
            raise KeyError("method_code is missing from state['selected_method_info']")

        logger.debug(" Method code:\n" + method_code)

        # Build prompt
        system_prompt = FLOW_ANALYSIS_PROMPT["system"]
        user_prompt = FLOW_ANALYSIS_PROMPT["user"].format(
            package=state.get("package", ""),
            imports=state.get("imports", ""),
            method=method_code,
            internal=state.get("internal_code", ""),
            external=state.get("external_code", ""),
        )

        max_retries = 1
        flow_data = None
        last_response = ""

        for attempt in range(max_retries + 1):
            response = client.chat.completions.create(
                model=MODEL,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            last_response = response.choices[0].message.content.strip()
            flow_data = _extract_json_from_response(last_response)

            if flow_data is not None:
                break
            else:
                logger.warning(f"⚠️ JSON parse failed on attempt {attempt+1}, retrying...")
                sleep(0.5)

        if flow_data:
            state["flow_analysis"] = flow_data
            logger.info(" Flow analysis stored in state['flow_analysis']")
            logger.debug(" Parsed flow analysis:\n" + json.dumps(flow_data, indent=2))
        else:
            state["flow_analysis"] = {}
            state["flow_analysis_raw"] = last_response
            logger.warning(" Could not parse flow analysis as JSON, raw response saved")

        # --- Extract and sanitize flow_name ---
        flow_name = None
        if isinstance(flow_data, dict):
            flow_name = flow_data.get("flow_name")

        if not flow_name:
            flow_name = f"{method_name}Flow"
            logger.warning(f" No flow_name in flow_data, using fallback: {flow_name}")
        else:
            # sanitize for Java class naming
            flow_name = re.sub(r'[^0-9a-zA-Z_]', '', flow_name)
            flow_name = flow_name[0].upper() + flow_name[1:]
            logger.info(" Trusting flow_name from flow_analyzer (fallback only if missing).")

        state["flow_name"] = flow_name
        logger.info(f" Final flow_name set: {flow_name}")


        return state

    except Exception as e:
        logger.error(f" Error during flow analysis: {e}")
        state.setdefault("validation_errors", []).append(f"Flow analysis error: {str(e)}")
        return state


def _extract_json_from_response(text: str) -> dict | None:
    """
    Try to extract JSON from GPT response safely.
    Supports plain JSON, fenced ```json blocks, or embedded JSON.
    """
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Markdown code block
    json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Fallback: any JSON-like substring
    json_pattern = r"\{.*\}"
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None

