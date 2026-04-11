import json
import logging
from typing import Dict, Any, Optional
from core.llm_client import LLMClient
from external.prompt import (
    checker_system_prompt1, checker_user_prompt1, 
    checker_system_prompt, checker_user_prompt
)

class CheckerService:
    """
    A service for reviewing and providing feedback on stories.

    This service uses an LLM client to evaluate a story based on a set of prompts.
    It can perform an initial review or a follow-up review based on previous feedback.
    """
    def __init__(self, llm_client: LLMClient):
        """
        Initializes the CheckerService.

        Args:
            llm_client (LLMClient): An instance of the LLM client for generating responses.
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
    
    def review_story(self, story: Dict[str, Any], rag_chunks: str, 
                    previous_feedback: Optional[Dict] = None, 
                    attempts: int = 0) -> Dict[str, Any]:
        """
        Review a story and provide structured feedback.

        This method sends the story to an LLM for evaluation. On the first attempt, it performs
        an initial review. On subsequent attempts, it includes previous feedback to guide the
        re-evaluation of the story.

        Args:
            story (Dict[str, Any]): The story to be reviewed, in a structured format.
            rag_chunks (str): Context from the RAG service to aid in the review.
            previous_feedback (Optional[Dict]): Feedback from a previous review, if any.
            attempts (int): The number of review attempts made so far.

        Returns:
            Dict[str, Any]: A dictionary containing the feedback from the LLM, or an empty
                            dictionary if an error occurs.
        """
        self.logger.info(f"Reviewing story - Attempt #{attempts}")
        self.logger.debug("Story being reviewed:\n%s", 
                         json.dumps(story, indent=2)[:1000])
        
        if attempts == 0:
            # First attempt: normal prompt
            system_prompt = checker_system_prompt1
            user_prompt = checker_user_prompt1.format(
                json_original_story=json.dumps(story, indent=2),
                rag_context=rag_chunks
            )
        else:
            # Later attempts: include previous feedback
            previous_feedback_str = json.dumps(previous_feedback, indent=2)
            system_prompt = checker_system_prompt
            user_prompt = checker_user_prompt.format(
                enhanced_story=json.dumps(story, indent=2),
                previous_checker_response=previous_feedback_str,
                rag_context=rag_chunks
            )
        
        response_obj = self.llm_client.generate_response(system_prompt, user_prompt)
        self.logger.info("LLM Checker Response: \n%s", json.dumps(response_obj, indent=2))

        # Handle potential error response
        if "error" in response_obj:
            self.logger.error("LLM generation failed: %s", response_obj["error"])
            return {}
        
        try:
            # Extract content and parse
            content = response_obj["choices"][0]["message"]["content"]
            feedback = json.loads(content)
            
            self.logger.info("Checker Ratings Summary:")
            for field, value in feedback.items():
                if isinstance(value, dict):
                    rating = value.get("Rating") or value.get("rating") or "N/A"
                    self.logger.info(f"   - {field}: {rating}")
            
            return feedback
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            self.logger.exception("Checker response parsing failed: %s", e)
            return {}
