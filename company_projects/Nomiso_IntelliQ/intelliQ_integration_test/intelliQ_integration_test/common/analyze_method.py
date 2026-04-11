import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

from common.agent_state import AgentState
from central_logger.logger import get_logger
from java_core.prompts import CONFIG
from java_core.nodes.extract_dependencies import extract_method_code

# Load environment variables
load_dotenv()

# Validate required env variables
required_vars = ["MODEL", "TEMPERATURE", "MAX_TOKENS"]
for var in required_vars:
    if var not in os.environ:
        raise RuntimeError(f"Missing required env variable: {var}")

MODEL = os.environ["MODEL"]
TEMPERATURE = float(os.environ["TEMPERATURE"])
MAX_TOKENS = int(os.environ["MAX_TOKENS"])

logger = get_logger(__name__)
client = OpenAI()


def analyze_method(state: AgentState) -> AgentState:
    """
    Analyze selected method using GPT to extract summary and dependencies.
    Ensures that state['selected_method_info'] always has method code.
    """
    method_name = state["selected_method"]
    logger.info(f" Analyzing method: {method_name}")

    try:
        # Extract method code using extract_dependencies function
        method_code = extract_method_code(state["file_path"], method_name)
        if not method_code:
            logger.error(f" Could not extract method code for: {method_name}")
            state["validation_errors"] = state.get("validation_errors", []) + [
                f"Method {method_name} not found"
            ]
            return state

        # Store method info for downstream nodes
        state["selected_method_info"] = {
            "name": method_name,
            "code": method_code,
        }

        # Debug log (truncate for safety)
        preview = "\n".join(method_code.splitlines()[:20])
        logger.debug(f" Extracted code preview for {method_name}:\n{preview}\n...")

        # Build GPT prompt (from CONFIG)
        system_prompt = CONFIG["system_prompt"]
        user_prompt = CONFIG["user_prompt"].format(
            package=state["package"],
            imports=state["imports"],
            method=method_code,
        )

        # Call GPT (model, temperature, max_tokens from .env)
        response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        result = response.choices[0].message.content.strip()

        # Parse JSON response
        analysis = _extract_json_from_response(result)
        if analysis:
            state["analysis"] = analysis

            # Promote "target" so generate_test can choose config
            if analysis.get("target"):
                state["target"] = analysis["target"]

            logger.info(f" Method analysis completed for: {method_name}")
            logger.debug(" Parsed analysis:\n" + json.dumps(analysis, indent=2))
        else:
            logger.warning(" Could not parse analysis as JSON, storing raw response")
            state["analysis"] = {"raw_response": result}

        return state

    except Exception as e:
        logger.error(f" Error analyzing method {method_name}: {e}")
        state["validation_errors"] = state.get("validation_errors", []) + [
            f"Analysis error: {str(e)}"
        ]
        return state


def _extract_json_from_response(text: str):
    """Try multiple strategies to extract JSON safely from GPT output."""
    try:
        return json.loads(text.strip())
    except Exception:
        pass

    # Look inside ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # Fallback: first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    return None