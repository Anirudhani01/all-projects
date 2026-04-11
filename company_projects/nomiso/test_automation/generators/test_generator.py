"""Advanced test case generator using LLM and sophisticated prompt templates."""

import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ..llm import LLMFactory, LLMProvider
from ..templates import TemplateFactory
from ..templates.base_templates import PromptTemplate


class TestGenerator:
    """Advanced test case generator with LLM integration."""

    def __init__(
        self, llm_provider: str = "ollama", model: Optional[str] = None, **llm_kwargs
    ):
        """Initialize the test generator.

        Args:
            llm_provider: LLM provider name ('ollama' or 'openai')
            model: Model name (defaults based on provider)
            **llm_kwargs: Additional LLM configuration
        """
        self.llm = LLMFactory.create_provider(llm_provider, model, **llm_kwargs)
        self.template_factory = TemplateFactory()

        # Validate LLM availability
        if not self.llm.is_available():
            if llm_provider == "ollama":
                # Try to pull the model if using Ollama
                asyncio.run(self._ensure_ollama_model())
            else:
                raise RuntimeError(f"LLM provider '{llm_provider}' is not available")

    async def _ensure_ollama_model(self) -> None:
        """Ensure Ollama model is available."""
        if hasattr(self.llm, "pull_model"):
            print(f"Pulling model {self.llm.model}...")
            success = await self.llm.pull_model()
            if not success:
                raise RuntimeError(f"Failed to pull Ollama model {self.llm.model}")

    async def generate_test_cases(
        self,
        programming_language: str,
        testing_framework: str,
        test_cases_file: Union[str, Path],
        category: str,
        knowledge_base_file: Optional[Union[str, Path]] = None,
        output_file: Optional[Union[str, Path]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **generation_kwargs,
    ) -> Dict[str, Any]:
        """Generate test cases using advanced prompt templates.

        Args:
            programming_language: Target programming language (Python, JavaScript, etc.)
            testing_framework: Testing framework (pytest, jest, etc.)
            test_cases_file: Path to test_cases.json file
            category: Test category (API, Unit, WebUI, MobileUI, etc.)
            knowledge_base_file: Optional knowledge base file
            output_file: Optional output file path
            temperature: LLM temperature setting
            max_tokens: Maximum tokens for generation
            **generation_kwargs: Additional generation parameters

        Returns:
            Generated test cases and metadata
        """
        # Load input data
        test_scenarios = self._load_test_scenarios(test_cases_file)
        knowledge_base = (
            self._load_knowledge_base(knowledge_base_file)
            if knowledge_base_file
            else ""
        )

        # Get appropriate template
        template = self.template_factory.create_template(category.lower())
        if not template:
            raise ValueError(f"Unsupported test category: {category}")

        # Prepare template variables
        template_vars = {
            "programming_language": programming_language,
            "testing_framework": testing_framework,
            "test_scenarios": json.dumps(test_scenarios, indent=2),
            "knowledge_base": knowledge_base,
            **generation_kwargs,
        }

        # Generate prompt
        prompt = template.render(**template_vars)
        schema = template.get_schema()

        # Generate test cases using LLM
        print(f"Generating {category} test cases using {self.llm.provider_name}...")
        response = await self.llm.generate_structured(
            prompt=prompt,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Parse response
        try:
            generated_tests = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse generated test cases: {e}")

        # Add metadata
        result = {
            "generation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "llm_provider": self.llm.provider_name,
                "llm_model": self.llm.model,
                "programming_language": programming_language,
                "testing_framework": testing_framework,
                "category": category,
                "template_used": template.template_name,
                "prompt_technique": self._get_prompt_technique(category),
                "token_usage": response.usage,
                "generation_time": (
                    response.metadata.get("total_duration")
                    if response.metadata
                    else None
                ),
            },
            "test_cases": generated_tests,
            "input_scenarios": test_scenarios,
        }

        # Save to file if requested
        if output_file:
            self._save_results(result, output_file)

        return result

    async def generate_multiple_categories(
        self,
        programming_language: str,
        testing_framework: str,
        test_cases_file: Union[str, Path],
        categories: List[str],
        knowledge_base_file: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        **generation_kwargs,
    ) -> Dict[str, Dict[str, Any]]:
        """Generate test cases for multiple categories.

        Args:
            programming_language: Target programming language
            testing_framework: Testing framework
            test_cases_file: Path to test_cases.json file
            categories: List of test categories
            knowledge_base_file: Optional knowledge base file
            output_dir: Optional output directory
            **generation_kwargs: Additional generation parameters

        Returns:
            Dictionary mapping categories to generated test cases
        """
        results = {}

        for category in categories:
            print(f"\n=== Generating {category} tests ===")

            try:
                output_file = None
                if output_dir:
                    output_dir_path = Path(output_dir)
                    output_dir_path.mkdir(parents=True, exist_ok=True)
                    output_file = (
                        output_dir_path
                        / f"{category}_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    )

                result = await self.generate_test_cases(
                    programming_language=programming_language,
                    testing_framework=testing_framework,
                    test_cases_file=test_cases_file,
                    category=category,
                    knowledge_base_file=knowledge_base_file,
                    output_file=output_file,
                    **generation_kwargs,
                )

                results[category] = result
                print(
                    f"✓ Generated {len(result['test_cases'].get('test_cases', []))} {category} test cases"
                )

            except Exception as e:
                print(f"✗ Failed to generate {category} tests: {e}")
                results[category] = {"error": str(e)}

        return results

    def _load_test_scenarios(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load test scenarios from JSON file."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Test cases file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in test cases file: {e}")

    def _load_knowledge_base(self, file_path: Union[str, Path]) -> str:
        """Load knowledge base content."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Knowledge base file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _save_results(
        self, results: Dict[str, Any], output_file: Union[str, Path]
    ) -> None:
        """Save results to JSON file."""
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        print(f"Results saved to: {output_file}")

    def _get_prompt_technique(self, category: str) -> str:
        """Get the prompting technique used for a category."""
        technique_map = {
            "api": "Chain-of-Thought (CoT)",
            "unit": "Few-Shot Learning",
            "webui": "Tree-of-Thoughts (ToT)",
            "mobileui": "Role-Based Prompting",
            "edge_cases": "Metacognitive Prompting",
            "performance": "Chain-of-Thought with Self-Consistency",
            "positive": "Few-Shot Learning",
            "negative": "Tree-of-Thoughts",
            "happy_path": "Role-Based Prompting",
            "functional": "Chain-of-Thought",
            "e2e": "Tree-of-Thoughts",
        }

        return technique_map.get(category.lower(), "Standard Prompting")

    def get_available_categories(self) -> List[str]:
        """Get list of available test categories."""
        return self.template_factory.get_available_categories()

    def get_category_info(self, category: str) -> Optional[Dict[str, str]]:
        """Get information about a specific category."""
        return self.template_factory.get_category_info(category)

    def suggest_categories(self, query: str) -> List[str]:
        """Suggest categories based on query."""
        return self.template_factory.suggest_categories(query)

    async def validate_llm_connection(self) -> bool:
        """Validate LLM connection."""
        try:
            response = await self.llm.generate(
                "Test connection. Respond with 'OK'.", temperature=0.1, max_tokens=10
            )
            return "ok" in response.content.lower()
        except Exception:
            return False
