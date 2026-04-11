"""Base prompt templates with advanced prompting techniques."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from jinja2 import Template


class PromptTemplate(ABC):
    """Base class for prompt templates."""

    def __init__(self, template_name: str, template_content: str):
        """Initialize the prompt template."""
        self.template_name = template_name
        self.template = Template(template_content)

    @abstractmethod
    def render(self, **kwargs) -> str:
        """Render the template with provided variables."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the expected JSON output schema."""
        pass


class ChainOfThoughtTemplate(PromptTemplate):
    """Chain-of-Thought prompting template for complex reasoning."""

    def __init__(
        self, template_name: str, template_content: str, reasoning_steps: List[str]
    ):
        """Initialize CoT template with reasoning steps."""
        super().__init__(template_name, template_content)
        self.reasoning_steps = reasoning_steps

    def render(self, **kwargs) -> str:
        """Render CoT template with step-by-step reasoning."""
        reasoning_prompt = "\n".join(
            [f"Step {i+1}: {step}" for i, step in enumerate(self.reasoning_steps)]
        )

        kwargs["reasoning_steps"] = reasoning_prompt
        return self.template.render(**kwargs)


class FewShotTemplate(PromptTemplate):
    """Few-shot learning template with examples."""

    def __init__(
        self, template_name: str, template_content: str, examples: List[Dict[str, Any]]
    ):
        """Initialize few-shot template with examples."""
        super().__init__(template_name, template_content)
        self.examples = examples

    def render(self, **kwargs) -> str:
        """Render few-shot template with examples."""
        kwargs["examples"] = self.examples
        return self.template.render(**kwargs)


class TreeOfThoughtsTemplate(PromptTemplate):
    """Tree-of-Thoughts template for exploring multiple reasoning paths."""

    def __init__(
        self, template_name: str, template_content: str, exploration_paths: List[str]
    ):
        """Initialize ToT template with exploration paths."""
        super().__init__(template_name, template_content)
        self.exploration_paths = exploration_paths

    def render(self, **kwargs) -> str:
        """Render ToT template with exploration paths."""
        paths_prompt = "\n".join(
            [f"Path {i+1}: {path}" for i, path in enumerate(self.exploration_paths)]
        )

        kwargs["exploration_paths"] = paths_prompt
        return self.template.render(**kwargs)


class RoleBasedTemplate(PromptTemplate):
    """Role-based prompting template."""

    def __init__(
        self, template_name: str, template_content: str, role: str, expertise: List[str]
    ):
        """Initialize role-based template."""
        super().__init__(template_name, template_content)
        self.role = role
        self.expertise = expertise

    def render(self, **kwargs) -> str:
        """Render role-based template."""
        kwargs["role"] = self.role
        kwargs["expertise"] = ", ".join(self.expertise)
        return self.template.render(**kwargs)


class MetacognitiveTemplate(PromptTemplate):
    """Metacognitive prompting template with self-reflection."""

    def __init__(
        self, template_name: str, template_content: str, reflection_questions: List[str]
    ):
        """Initialize metacognitive template."""
        super().__init__(template_name, template_content)
        self.reflection_questions = reflection_questions

    def render(self, **kwargs) -> str:
        """Render metacognitive template with reflection."""
        reflection_prompt = "\n".join(
            [f"Reflect: {question}" for question in self.reflection_questions]
        )

        kwargs["reflection_questions"] = reflection_prompt
        return self.template.render(**kwargs)
