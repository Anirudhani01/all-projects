import json
import logging
from typing import Dict, Any, List, Optional
from components.common.llm_client import LLMClient
from components.common.prompts import rerun_failed_cases_system_prompt, rerun_failed_cases_user_prompt
from pathlib import Path

class FailedTestCasesRegenerationService:
    """
    A service for convertion story into proper structure and use that to generate test cases.
    """
    def __init__(self, llm_client, config):
        """Initialize the checker service."""
        self.llm_client = llm_client
        self.config = config
        self.logger = logging.getLogger(__name__)

    def failed_test_cases_regenerator(self, structured_user_story_text: str, test_cases_with_feedback, rag_chunks: str) -> Dict[str, Any]:
        """
        Review a story and provide structured feedback.

        Args:
            story (Dict[str, Any]): The story to review
            rag_chunks (str): Context from the RAG service

        Returns:
            Dict[str, Any]: regenerated test cases in proper structure
        """
        self.logger.info("[REGENERATOR] Regenerating failed test cases...")
        system_prompt = rerun_failed_cases_system_prompt
        user_prompt = rerun_failed_cases_user_prompt.format(
                test_cases_with_feedback=json.dumps(test_cases_with_feedback, indent=2),
                structured_user_story_text=structured_user_story_text,
                rag_context=rag_chunks
            )
        # Get response from LLM
        regenerated_failed_testcases = self.llm_client.generate_response(system_prompt, user_prompt)
        return regenerated_failed_testcases
    
    def failed_testcases_regenerator_with_text(self, structured_text: str, rag_chunks: str, failed_test_cases: Any) -> Dict[str, Any]:
        """
        Regenerate failed test cases using pre-generated structured text.
        
        Args:
            structured_text (str): Pre-generated structured text from story
            rag_chunks (str): Context from the RAG service
            failed_test_cases (Any): Failed test cases to regenerate
            
        Returns:
            Dict[str, Any]: Regenerated test cases results
        """
        self.logger.info("[REGENERATOR] Regenerating failed test cases...")
        system_prompt = rerun_failed_cases_system_prompt
        
        # Convert failed test cases to JSON string if needed
        if isinstance(failed_test_cases, dict):
            test_cases_json = json.dumps(failed_test_cases, indent=2)
        else:
            test_cases_json = str(failed_test_cases)
        
        user_prompt = rerun_failed_cases_user_prompt.format(
            test_cases_with_feedback=test_cases_json,
            structured_user_story_text=structured_text,
            rag_context=rag_chunks
        )
        
        # Get response from LLM
        regenerated_result = self.llm_client.generate_response(system_prompt, user_prompt)
        return regenerated_result



