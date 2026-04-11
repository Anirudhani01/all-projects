import os
import sys
import argparse
import base64
import asyncio
import json
import traceback
import logging

from components.image_parser.utils import encode_image, detect_layout_types
from components.image_parser.extractor import extract_ui_structure  # Unified extractor

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def run_extraction(image_path: str, mode: str = "unified") -> dict:
    """
    Run layout extraction from a UI screenshot and return the JSON structure.

    Args:
        image_path: Path to the input image.
        mode: Extraction mode (default: 'unified').

    Returns:
        The extracted layout structure as a dictionary.
    """
    try:
        logger.info(f"Processing image: {image_path}")

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image path '{image_path}' not found.")

        image_b64 = encode_image(image_path)
        if not image_b64:
            raise ValueError("Failed to encode image.")

        layout_detection = await detect_layout_types(image_b64)
        detected_layouts = layout_detection.get("detected_layouts", [])

        if not detected_layouts:
            raise ValueError("No valid layout types were detected.")

        layout_info = [(l["type"], l.get("id", ""), l.get("position", {})) for l in detected_layouts]
        logger.info("Detected layout blocks:")
        for layout in layout_info:
            logger.info(f"  - {layout}")

        # Unified extraction using composite structure
        result = await extract_ui_structure(image_b64, layout_info)

        final_output = result.get("data", {})
        usage = result.get("usage", {})

        if usage:
            logger.info("Token Usage:")
            logger.info(f"  Prompt Tokens:     {usage.get('prompt_tokens', 0)}")
            logger.info(f"  Completion Tokens: {usage.get('completion_tokens', 0)}")
            logger.info(f"  Total Tokens:      {usage.get('total_tokens', 0)}")

        return final_output

    except Exception as e:
        logger.error(f"An error occurred during extraction: {e}")
        logger.debug(traceback.format_exc())
        return {}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run layout extraction on a given image.")
    parser.add_argument("--image", required=True, help="Path to the input image.")
    parser.add_argument("--mode", choices=["unified", "loop"], default="unified", help="Reserved for future use.")
    args = parser.parse_args()

    result = asyncio.run(run_extraction(args.image, mode=args.mode))
    logger.info("Extracted Output:")
    logger.info(json.dumps(result, indent=2))
