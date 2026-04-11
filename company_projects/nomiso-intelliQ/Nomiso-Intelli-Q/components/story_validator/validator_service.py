import json
import logging
from typing import Dict, Any, List, Optional
from components.common.llm_client import LLMClient
from components.common.prompts import validate_quality_system_prompt, validate_quality_user_prompt, story_to_text_system_prompt, story_to_text_user_prompt
from pathlib import Path

class ValidatorService:
    """
    A service for convertion story into proper structure and use that to generate test cases.
    """
    def __init__(self, llm_client, config):
        """Initialize the checker service."""
        self.llm_client = llm_client
        self.config = config
        self.logger = logging.getLogger(__name__)

    def test_case_validator(self, story: Dict[str, Any], rag_chunks: str) -> str:
        """
        Review a story and provide structured feedback.

        Args:
            story (Dict[str, Any]): The story to review
            rag_chunks (str): Context from the RAG service

        Returns:
            Dict[str, Any]: text containing story in proper structure
        """
        self.logger.info("[VALIDATOR] Generating validation analysis...")
        system_prompt = validate_quality_system_prompt
        # Convert story to structured text first  
        structured_text = json.dumps(story, indent=2)  # For now, use JSON format
        
        user_prompt = validate_quality_user_prompt.format(
                structured_user_story_text=structured_text,
                rag_chunks=rag_chunks,
                test_cases="Test cases to be provided")
        # Get response from LLM
        testcases = self.llm_client.generate_response(system_prompt, user_prompt)
        return testcases
    
    def test_case_validator_with_cases(self, story: Dict[str, Any], rag_chunks: str, test_cases: Any) -> str:
        """
        Validate test cases against the story.
        
        Args:
            story (Dict[str, Any]): The story to review
            rag_chunks (str): Context from the RAG service
            test_cases (Any): The test cases to validate
            
        Returns:
            str: Validation results
        """
        self.logger.info("[VALIDATOR] Validating test cases against story...")
        system_prompt = validate_quality_system_prompt
        
        # Convert story to structured text
        structured_text = json.dumps(story, indent=2)
        
        # Convert test cases to JSON string if needed
        if isinstance(test_cases, dict):
            test_cases_json = json.dumps(test_cases, indent=2)
        else:
            test_cases_json = str(test_cases)
        
        user_prompt = validate_quality_user_prompt.format(
            structured_user_story_text=structured_text,
            rag_chunks=rag_chunks,
            test_cases=test_cases_json
        )
        
        # Get response from LLM
        validation_result = self.llm_client.generate_response(system_prompt, user_prompt)
        return validation_result
    
    def story_to_text(self, story: Dict[str, Any], rag_chunks: str) -> str:
        """
        Convert a story to structured text format.

        Args:
            story (Dict[str, Any]): The story to convert
            rag_chunks (str): Context from the RAG service

        Returns:
            str: Structured text representation of the story
        """
        self.logger.info("[VALIDATOR] Converting story to structured text...")
        system_prompt = story_to_text_system_prompt
        user_prompt = story_to_text_user_prompt.format(
            raw_user_story=json.dumps(story, indent=2)
        )
        # Get response from LLM
        result = self.llm_client.generate_response_text(system_prompt, user_prompt)
        return result
    
    def test_case_validator_with_text(self, structured_text: str, rag_chunks: str, test_cases: Any) -> str:
        """
        Validate test cases using pre-generated structured text.
        
        Args:
            structured_text (str): Pre-generated structured text from story
            rag_chunks (str): Context from the RAG service
            test_cases (Any): Test cases to validate
            
        Returns:
            str: Validation results
        """
        self.logger.info("[VALIDATOR] Validating test cases against story...")
        system_prompt = validate_quality_system_prompt
        
        # Convert test cases to JSON string if needed
        if isinstance(test_cases, dict):
            test_cases_json = json.dumps(test_cases, indent=2)
        else:
            test_cases_json = str(test_cases)
        
        user_prompt = validate_quality_user_prompt.format(
            structured_user_story_text=structured_text,
            rag_chunks=rag_chunks,
            test_cases=test_cases_json
        )
        
        # Get response from LLM
        validation_result = self.llm_client.generate_response(system_prompt, user_prompt)
        return validation_result
    
    def story_to_text(self, story: Dict[str, Any], rag_chunks: str) -> str:
        """
        Convert a story to structured text format.

        Args:
            story (Dict[str, Any]): The story to convert
            rag_chunks (str): Context from the RAG service

        Returns:
            str: Structured text representation of the story
        """
        self.logger.info("[VALIDATOR] Converting story to structured text...")
        system_prompt = story_to_text_system_prompt
        user_prompt = story_to_text_user_prompt.format(
            raw_user_story=json.dumps(story, indent=2)
        )
        # Get response from LLM
        result = self.llm_client.generate_response_text(system_prompt, user_prompt)
        return result
    