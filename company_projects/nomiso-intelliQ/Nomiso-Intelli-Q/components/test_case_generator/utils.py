import asyncio
import sys
import json


def ensure_event_loop_compatibility():
    """
    Ensure the event loop is compatible across platforms.
    On Windows, switches the default ProactorEventLoop to SelectorEventLoop for compatibility with async drivers.
    """
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())




def safe_json_parse(content: str) -> dict:
    """
    Safely parse a JSON string that may be wrapped in markdown-style code blocks.
    
    Args:
        content (str): Raw JSON string, possibly with ```json wrappers.
    
    Returns:
        dict: Parsed JSON dictionary, or a fallback {"error": "..."} if failed.
    """
    try:
        # Strip markdown code block wrappers if present
        clean = content.strip()
        if clean.startswith("```json"):
            clean = clean.removeprefix("```json").removesuffix("```").strip()
        elif clean.startswith("```"):
            clean = clean.removeprefix("```").removesuffix("```").strip()

        # Parse the cleaned string
        return json.loads(clean)
    
    except Exception as e:
        return {
            "error": f"Could not parse JSON",
            "raw": content,
            "exception": str(e)
        }
