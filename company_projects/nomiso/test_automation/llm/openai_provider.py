"""OpenAI LLM provider implementation."""

import json
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from .base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(
        self, model: str = "gpt-4o-mini", api_key: Optional[str] = None, **kwargs
    ):
        """Initialize OpenAI provider."""
        super().__init__(model, **kwargs)
        self.client = AsyncOpenAI(
            api_key=api_key or kwargs.get("api_key"),
            **{k: v for k, v in kwargs.items() if k not in ["api_key"]},
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate response from OpenAI."""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                provider="openai",
                usage=(
                    {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                    if response.usage
                    else None
                ),
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id,
                },
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {str(e)}")

    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate structured JSON response from OpenAI."""

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

        # Use OpenAI's structured output if available
        if "response_format" not in kwargs and hasattr(
            self.client.chat.completions, "create"
        ):
            kwargs["response_format"] = {"type": "json_object"}

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
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                provider="openai",
                usage=(
                    {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                    if response.usage
                    else None
                ),
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id,
                },
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI chat failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            # Check if API key is set
            return bool(self.client.api_key)
        except Exception:
            return False

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai"
