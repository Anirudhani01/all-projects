import logging
from typing import Dict, Any, Optional
from openai import OpenAI

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
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            return response.dict()
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return {"error": f"[OpenAI Error] {e}"}
