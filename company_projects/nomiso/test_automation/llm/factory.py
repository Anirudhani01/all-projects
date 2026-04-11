"""LLM factory for creating provider instances."""

import os
from typing import Dict, Optional

from .base import LLMProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider


class LLMFactory:
    """Factory for creating LLM provider instances."""

    _providers = {
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,
    }

    @classmethod
    def create_provider(
        self, provider: str = "ollama", model: Optional[str] = None, **kwargs
    ) -> LLMProvider:
        """Create an LLM provider instance.

        Args:
            provider: Provider name ('ollama' or 'openai')
            model: Model name (defaults based on provider)
            **kwargs: Additional provider-specific configuration

        Returns:
            LLM provider instance

        Raises:
            ValueError: If provider is not supported
        """
        if provider not in self._providers:
            raise ValueError(
                f"Unsupported provider: {provider}. Available: {list(self._providers.keys())}"
            )

        provider_class = self._providers[provider]

        # Set default models
        if not model:
            if provider == "ollama":
                model = "llama3.1:8b-instruct-q8_0"
            elif provider == "openai":
                model = "gpt-4o-mini"

        # Provider-specific configuration
        if provider == "openai":
            kwargs.setdefault("api_key", os.getenv("OPENAI_API_KEY"))
        elif provider == "ollama":
            kwargs.setdefault(
                "host", os.getenv("OLLAMA_HOST", "http://localhost:11434")
            )

        return provider_class(model=model, **kwargs)

    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """Get availability status of all providers.

        Returns:
            Dict mapping provider names to availability status
        """
        availability = {}

        for provider_name in cls._providers:
            try:
                provider = cls.create_provider(provider_name)
                availability[provider_name] = provider.is_available()
            except Exception:
                availability[provider_name] = False

        return availability

    @classmethod
    def get_best_available_provider(cls) -> Optional[LLMProvider]:
        """Get the best available provider.

        Priority: ollama -> openai

        Returns:
            Best available provider instance or None if none available
        """
        providers_priority = ["ollama", "openai"]

        for provider_name in providers_priority:
            try:
                provider = cls.create_provider(provider_name)
                if provider.is_available():
                    return provider
            except Exception:
                continue

        return None

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """Register a new provider class.

        Args:
            name: Provider name
            provider_class: Provider class implementing LLMProvider
        """
        cls._providers[name] = provider_class
