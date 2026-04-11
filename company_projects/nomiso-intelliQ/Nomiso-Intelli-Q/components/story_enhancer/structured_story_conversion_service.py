import json
import logging
from typing import Dict, Any, List, Optional
from components.common.llm_client import LLMClient
from components.common.prompts import story_to_text_system_prompt, story_to_text_user_prompt
from pathlib import Path

class structuredstoryfortestcaseService:
    """
    A service for convertion story into proper structure and use that to generate test cases.
    """
    def __init__(self, llm_client, config):
        """Initialize the checker service."""
        self.llm_client = llm_client
        self.config = config
        self.logger = logging.getLogger(__name__)

    
    def story_to_structured_json(self, story: Dict[str, Any]) -> str:
        """
        Review a story and provide structured feedback.

        Args:
            story (Dict[str, Any]): The story to review
            rag_chunks (str): Context from the RAG service

        Returns:
            Dict[str, Any]: json containing story in proper structure
        """
        # Always use the proper prompts from prompts.py for structured text generation
        self.logger.info("[TESTCASE_GENERATION] Converting story to structured text...")
        system_prompt = story_to_text_system_prompt
        user_prompt = story_to_text_user_prompt.format(
                raw_user_story=json.dumps(story, indent=2)
            )
        # Get response from LLM
        result = self.llm_client.generate_response(system_prompt, user_prompt)
        return result
    



