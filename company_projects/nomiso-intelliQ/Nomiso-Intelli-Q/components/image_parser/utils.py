import os
import json
import base64
import asyncio
import re
from dotenv import load_dotenv

import openai

# Load environment variables and set OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load template library (excluding composite)
TEMPLATE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "template_library.json"))
COMPOSITE_TEMPLATE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__),"composite_template.json"))

with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    TEMPLATE_LIBRARY = json.load(f)

VALID_TYPES = [t for t in TEMPLATE_LIBRARY.keys()]  # Composite handled separately
TYPE_MAP = TEMPLATE_LIBRARY

def encode_image(image_path: str) -> str:
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        # print(f"Failed to encode image: {image_path}\nError: {e}")
        return {"error": "Failed to encode image", "raw": f"{image_path}\nError: {e}"}

def safe_json_parse(content: str):
    try:
        return json.loads(content)
    except:
        try:
            cleaned = content.replace("```json", "").replace("```", "").strip()
            match = re.search(r"({.*})", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return json.loads(cleaned)
        except Exception as e:
            # print("Failed to parse JSON:", e)
            # print("Raw content was:\n", content[:1000])
            return {"error": "Could not parse JSON", "raw": content}




async def smart_chat_completion(
    messages,
    model_primary="gpt-4o",
    model_fallback="gpt-4.1",
    max_tokens_primary=16000,
    max_tokens_fallback=32768
):
    client = openai.OpenAI()

    def run_model_call(model, max_tokens):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                max_tokens=max_tokens
            ), None
        except Exception as e:
            return None, e

    # Call primary model
    response, error = run_model_call(model_primary, max_tokens_primary)
    usage = response.usage.model_dump() if response and hasattr(response, "usage") else {}
    needs_fallback = (
        not response or usage.get("completion_tokens", 0) >= max_tokens_primary
    )
    # print(needs_fallback,"needs_fallback")

    # Fallback if needed
    if needs_fallback:
        response, error = run_model_call(model_fallback, max_tokens_fallback)
        if not response:
            return {"error": f"Both models failed: {type(error).__name__}: {error}"}, {}

        usage = response.usage.model_dump() if hasattr(response, "usage") else {}

    # Final parse
    try:
        content = response.choices[0].message.content
        return safe_json_parse(content), usage
    except Exception:
        return {"error": "Invalid model output structure"}, {}


async def detect_layout_types(image_b64: str) -> dict:
    system_prompt = f"""
You are a visual layout classifier for a QA automation tool.

You will be shown a screenshot from a real user interface (web, mobile, or tablet).
Your job is to identify each visible layout block separately and return them with their type, unique id, and approximate screen position.

Supported layout types:
{VALID_TYPES}

Guidelines:
- Use only visual structure (e.g., groupings, fields, alignment, shadows).
- Do NOT guess based on text. This is visual layout classification only.
- If multiple layouts of the same type (e.g., 2 forms) are visible, return each one separately.
- If nothing matches known layouts, return type as "general".

Each layout should include:
- type (from known types)
- id (make a unique identifier like form_00_xyz)
- position (approximate description like top-left, center, bottom)

Expected JSON Output:
{{
  "detected_layouts": [
    {{
      "type": "form",
      "id": "form_00_user_info",
      "position": "top-left"
    }}
  ]
}}
"""

    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What layout types are visible on this screen?"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]
        }
    ]

    response, _ = await smart_chat_completion(messages, max_tokens_primary=1000, max_tokens_fallback=1000)
    return response

async def validate_structure(image_b64: str, pom_json: dict):
    validation_prompt = """
You are a UI structure validator.

You will be shown a JSON-based layout extracted from a UI screenshot.
Your tasks are:
- Fill in missing fields if clues are visible (e.g., label, icon, text alignment, position)
- Ensure all template fields are filled if visible (avoid leaving any standard structure empty)
- Add missing metadata (position, icons, states, colors, etc.) if visually present
- Remove blank, null, or irrelevant fields
- Regroup elements under the correct structural block (e.g., buttons under actions, title under card)
- Flag if any visible structure is present but missing in JSON (e.g., visible menu not extracted)
- Do not hallucinate or invent data not clearly visible
- Ensure JSON output matches the required format of the original layout type schema
- Output must be valid JSON only.
"""

    messages = [
        {"role": "system", "content": validation_prompt.strip()},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Validate and fix structure: {json.dumps(pom_json)}"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]
        }
    ]

    response, _ = await smart_chat_completion(messages)
    return response
