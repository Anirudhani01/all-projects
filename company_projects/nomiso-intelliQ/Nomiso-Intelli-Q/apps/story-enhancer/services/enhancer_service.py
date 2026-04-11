import json
import logging
from typing import Dict, Any, Optional
from core.llm_client import LLMClient
from external.prompt import enhancer_system_prompt, enhancer_user_prompt

class EnhancerService:
    """
    A service for enhancing stories based on feedback.

    This service uses an LLM client to improve a story by incorporating feedback
    from the checker service and context from the RAG service.
    """
    def __init__(self, llm_client: LLMClient):
        """
        Initializes the EnhancerService.

        Args:
            llm_client (LLMClient): An instance of the LLM client for generating responses.
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
    
    def enhance_story(self, story: Dict[str, Any], 
                     checker_response: Dict[str, Any], 
                     rag_chunks: str) -> Optional[Dict[str, Any]]:
        """
        Enhance a story based on checker feedback and RAG context.

        This method sends the original story, along with feedback and context, to an
        LLM to generate an improved version of the story.

        Args:
            story (Dict[str, Any]): The original story to be enhanced.
            checker_response (Dict[str, Any]): Feedback from the checker service.
            rag_chunks (str): Context from the RAG service.

        Returns:
            Optional[Dict[str, Any]]: The enhanced story, or None if an error occurs.
        """
        self.logger.info('Enhancing the story...')
        
        if not checker_response:
            return None
        
        user_prompt = enhancer_user_prompt.format(
            json_original_story=json.dumps(story, indent=2),
            checker_response=json.dumps(checker_response, indent=2),
            rag_context=rag_chunks
        )
        
        response_obj = self.llm_client.generate_response(
            enhancer_system_prompt, user_prompt
        )
        self.logger.info("LLM Enhancer Response: \n%s", json.dumps(response_obj, indent=2))
        
        # Handle potential error response
        if "error" in response_obj:
            self.logger.error("LLM generation failed: %s", response_obj["error"])
            return None
            
        try:
            content = response_obj["choices"][0]["message"]["content"]
            enhanced_story = json.loads(content)
            return enhanced_story
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            self.logger.exception("Enhancer response parsing failed: %s", e)
            return None