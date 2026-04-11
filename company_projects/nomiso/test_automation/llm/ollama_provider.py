"""Ollama LLM provider implementation."""

import json
import asyncio
from typing import Any, Dict, List, Optional

import ollama
from .base import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    """Ollama LLM provider implementation."""

    def __init__(self, model: str = "llama3.1:8b-instruct-q8_0", **kwargs):
        """Initialize Ollama provider."""
        super().__init__(model, **kwargs)
        self.client = ollama.AsyncClient(
            host=kwargs.get("host", "http://localhost:11434")
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate response from Ollama."""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            options = {
                "temperature": temperature,
                "num_predict": max_tokens or -1,
            }

            response = await self.client.chat(
                model=self.model, messages=messages, options=options, **kwargs
            )

            return LLMResponse(
                content=response["message"]["content"],
                model=self.model,
                provider="ollama",
                usage={
                    "prompt_tokens": response.get("prompt_eval_count", 0),
                    "completion_tokens": response.get("eval_count", 0),
                    "total_tokens": response.get("prompt_eval_count", 0)
                    + response.get("eval_count", 0),
                },
                metadata={
                    "eval_duration": response.get("eval_duration", 0),
                    "load_duration": response.get("load_duration", 0),
                    "total_duration": response.get("total_duration", 0),
                },
            )

        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")

    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate structured JSON response from Ollama."""

        # Enhanced system prompt for structured output
        json_instruction = f"""
You must respond with valid JSON that strictly follows this schema:
{json.dumps(schema, indent=2)}

Rules:
1. Output ONLY valid JSON, no additional text or explanation
2. Follow the exact schema structure and types
3. Use proper JSON formatting with double quotes
4. If uncertain about a value, use null or appropriate default
"""

        enhanced_system = (
            f"{system_prompt}\n\n{json_instruction}"
            if system_prompt
            else json_instruction
        )

        # Add JSON formatting instruction to prompt
        enhanced_prompt = f"{prompt}\n\nProvide your response as valid JSON following the specified schema:"

        response = await self.generate(
            enhanced_prompt,
            system_prompt=enhanced_system,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Validate JSON response
        try:
            json.loads(response.content)
        except json.JSONDecodeError as e:
            # Try to extract JSON from response if wrapped in text
            content = response.content.strip()
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end != -1:
                    content = content[start:end].strip()
            elif "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                content = content[start:end]

            try:
                json.loads(content)
                response.content = content
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON response: {e}")

        return response

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate response from conversation."""
        try:
            options = {
                "temperature": temperature,
                "num_predict": max_tokens or -1,
            }

            response = await self.client.chat(
                model=self.model, messages=messages, options=options, **kwargs
            )

            return LLMResponse(
                content=response["message"]["content"],
                model=self.model,
                provider="ollama",
                usage={
                    "prompt_tokens": response.get("prompt_eval_count", 0),
                    "completion_tokens": response.get("eval_count", 0),
                    "total_tokens": response.get("prompt_eval_count", 0)
                    + response.get("eval_count", 0),
                },
                metadata={
                    "eval_duration": response.get("eval_duration", 0),
                    "load_duration": response.get("load_duration", 0),
                    "total_duration": response.get("total_duration", 0),
                },
            )

        except Exception as e:
            raise RuntimeError(f"Ollama chat failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            # Try to list models to test connection
            models = ollama.list()
            return any(
                model["name"] == self.model for model in models.get("models", [])
            )
        except Exception:
            return False

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "ollama"

    async def pull_model(self) -> bool:
        """Pull the model if not available."""
        try:
            await self.client.pull(self.model)
            return True
        except Exception as e:
            print(f"Failed to pull model {self.model}: {e}")
            return False
