import logging
from typing import Dict, Any, Optional
from openai import OpenAI
import json

class LLMClient:
    """
    A client for interacting with the OpenAI Language Model (LLM).

    This class provides a simplified interface for sending requests to the OpenAI API
    and receiving generated responses. It handles the authentication and model selection.
    """
    def __init__(self, api_key: str, model: str):
        """
        Initializes the LLMClient.

        Args:
            api_key (str): The API key for accessing the OpenAI service.
            model (str): The default language model to be used for generating responses.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    def generate_response(self, system_prompt: str, user_prompt: str, 
                         model: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response using the OpenAI API.

        This method sends a system and user prompt to the OpenAI chat completions endpoint
        and returns the full response object as a dictionary. It allows specifying a
        different model for a particular request, otherwise it uses the default model.

        Args:
            system_prompt (str): The system-level instructions for the language model.
            user_prompt (str): The user's input or question to the language model.
            model (Optional[str]): A specific model to use for this request, overriding the default.

        Returns:
            Dict[str, Any]: The full response from the OpenAI API as a dictionary,
                            or an error dictionary if an exception occurs.
        """
        try:
            # Add explicit JSON formatting instructions to system prompt
            json_system_prompt = f"{system_prompt}\n\nCRITICAL: Your response MUST be a valid JSON object. Do not include any text, markdown formatting, or explanations outside the JSON object."
            
            # Create the chat completion with JSON response format
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=[
                    {"role": "system", "content": json_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"},
                seed=42  # For consistent responses
            )
            
            # Extract content and parse JSON
            content = response.choices[0].message.content
            response_dict = json.loads(content)
            
            # Log usage statistics and response details for debugging
            usage_stats = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            self.logger.debug(f"LLM JSON Response - Model: {response.model}, Finish Reason: {response.choices[0].finish_reason}")
            self.logger.debug(f"Token Usage - Prompt: {usage_stats['prompt_tokens']}, Completion: {usage_stats['completion_tokens']}, Total: {usage_stats['total_tokens']}")
            self.logger.debug(f"Raw LLM Response:\n{response_dict}")
            
            return response_dict
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return {"error": f"[OpenAI Error] {e}"}
        
    def generate_response_text(self, system_prompt: str, user_prompt: str, 
                         model: Optional[str] = None) -> str:
        """
        Generate a text response using the OpenAI API.

        This method sends a system and user prompt to the OpenAI chat completions endpoint
        and returns the response content as text. It allows specifying a
        different model for a particular request, otherwise it uses the default model.

        Args:
            system_prompt (str): The system-level instructions for the language model.
            user_prompt (str): The user's input or question to the language model.
            model (Optional[str]): A specific model to use for this request, overriding the default.

        Returns:
            str: The response content from the OpenAI API as text.
        """
        try:
            # Create the chat completion for text response
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                seed=42  # For consistent responses
            )
            
            content = response.choices[0].message.content
            
            # Log usage statistics and response details for debugging
            usage_stats = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            self.logger.debug(f"LLM Text Response - Model: {response.model}, Finish Reason: {response.choices[0].finish_reason}")
            self.logger.debug(f"Token Usage - Prompt: {usage_stats['prompt_tokens']}, Completion: {usage_stats['completion_tokens']}, Total: {usage_stats['total_tokens']}")
            self.logger.debug(f"Response Content Length: {len(content)} characters")
            
            return content
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return f"[OpenAI Error] {e}"
    
    def generate_response_text_with_stats(self, system_prompt: str, user_prompt: str, 
                         model: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a text response with usage statistics from the OpenAI API.

        Args:
            system_prompt (str): The system-level instructions for the language model.
            user_prompt (str): The user's input or question to the language model.
            model (Optional[str]): A specific model to use for this request, overriding the default.

        Returns:
            Dict[str, Any]: Dictionary containing 'content', 'usage', and 'model' information.
        """
        try:
            # Create the chat completion for text response
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                seed=42  # For consistent responses
            )
            
            content = response.choices[0].message.content
            usage_stats = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            return {
                'content': content,
                'usage': usage_stats,
                'model': response.model,
                'finish_reason': response.choices[0].finish_reason
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return {
                'content': f"[OpenAI Error] {e}",
                'error': str(e),
                'usage': None,
                'model': model or self.model,
                'finish_reason': 'error'
            }
