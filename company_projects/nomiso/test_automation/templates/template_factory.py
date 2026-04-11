"""Template factory for managing and creating test generation templates."""

from typing import Dict, Type, Optional, List
from .base_templates import PromptTemplate
from .test_generation_templates import (
    APITestTemplate,
    UnitTestTemplate,
    WebUITestTemplate,
    MobileUITestTemplate,
    EdgeCaseTestTemplate,
    PerformanceTestTemplate,
)
from .specialized_templates import (
    PositiveTestTemplate,
    NegativeTestTemplate,
    HappyPathTestTemplate,
    FunctionalTestTemplate,
    E2ETestTemplate,
)


class TemplateFactory:
    """Factory for creating and managing test generation templates."""

    # Template registry mapping categories to template classes
    _templates: Dict[str, Type[PromptTemplate]] = {
        # Primary test categories
        "api": APITestTemplate,
        "unit": UnitTestTemplate,
        "webui": WebUITestTemplate,
        "mobileui": MobileUITestTemplate,
        "edge_cases": EdgeCaseTestTemplate,
        "performance": PerformanceTestTemplate,
        # Specialized test types
        "positive": PositiveTestTemplate,
        "negative": NegativeTestTemplate,
        "happy_path": HappyPathTestTemplate,
        "functional": FunctionalTestTemplate,
        "e2e": E2ETestTemplate,
        # Aliases for convenience
        "integration": E2ETestTemplate,
        "load": PerformanceTestTemplate,
        "stress": PerformanceTestTemplate,
        "boundary": EdgeCaseTestTemplate,
        "smoke": HappyPathTestTemplate,
        "regression": FunctionalTestTemplate,
        "acceptance": HappyPathTestTemplate,
    }

    # Category descriptions for documentation
    _category_descriptions = {
        "api": "REST API testing with HTTP methods, authentication, validation",
        "unit": "Unit testing for individual functions and components",
        "webui": "Web UI testing with Selenium, user interactions, accessibility",
        "mobileui": "Mobile UI testing for iOS/Android apps with gestures and platform-specific features",
        "edge_cases": "Edge case and boundary testing for error conditions and limits",
        "performance": "Performance, load, and stress testing scenarios",
        "positive": "Positive test cases for valid inputs and happy path scenarios",
        "negative": "Negative test cases for invalid inputs and error conditions",
        "happy_path": "Happy path testing for optimal user journeys",
        "functional": "Functional testing for feature validation and requirements compliance",
        "e2e": "End-to-end testing for complete business workflows",
    }

    # Prompting technique mappings
    _prompting_techniques = {
        "api": "Chain-of-Thought (CoT) - Systematic reasoning for complex API testing scenarios",
        "unit": "Few-Shot Learning - Examples-based learning for consistent unit test patterns",
        "webui": "Tree-of-Thoughts (ToT) - Multi-path exploration for comprehensive UI testing",
        "mobileui": "Role-Based Prompting - Expert mobile QA engineer perspective",
        "edge_cases": "Metacognitive Prompting - Self-reflection on failure modes and edge conditions",
        "performance": "Chain-of-Thought with Self-Consistency - Systematic performance analysis",
        "positive": "Few-Shot Learning - Example-driven positive scenario generation",
        "negative": "Tree-of-Thoughts - Multi-path exploration of failure scenarios",
        "happy_path": "Role-Based Prompting - Business analyst and UX expert perspective",
        "functional": "Chain-of-Thought - Systematic requirements validation approach",
        "e2e": "Tree-of-Thoughts - Comprehensive workflow path exploration",
    }

    @classmethod
    def create_template(cls, category: str) -> Optional[PromptTemplate]:
        """Create a template instance for the specified category.

        Args:
            category: Test category (api, unit, webui, mobileui, etc.)

        Returns:
            Template instance or None if category not found
        """
        category = category.lower().strip()

        if category not in cls._templates:
            return None

        template_class = cls._templates[category]
        return template_class()

    @classmethod
    def get_available_categories(cls) -> List[str]:
        """Get list of available template categories.

        Returns:
            List of available category names
        """
        # Return unique categories (exclude aliases)
        unique_categories = []
        seen_classes = set()

        for category, template_class in cls._templates.items():
            if template_class not in seen_classes:
                unique_categories.append(category)
                seen_classes.add(template_class)

        return sorted(unique_categories)

    @classmethod
    def get_category_info(cls, category: str) -> Optional[Dict[str, str]]:
        """Get information about a specific category.

        Args:
            category: Test category name

        Returns:
            Dictionary with category information or None if not found
        """
        category = category.lower().strip()

        if category not in cls._templates:
            return None

        return {
            "category": category,
            "description": cls._category_descriptions.get(
                category, "No description available"
            ),
            "prompting_technique": cls._prompting_techniques.get(
                category, "Standard prompting"
            ),
            "template_class": cls._templates[category].__name__,
        }

    @classmethod
    def get_categories_by_type(cls, test_type: str) -> List[str]:
        """Get categories filtered by test type.

        Args:
            test_type: Type filter (api, ui, functional, performance, etc.)

        Returns:
            List of matching categories
        """
        test_type = test_type.lower().strip()

        type_mappings = {
            "api": ["api"],
            "ui": ["webui", "mobileui"],
            "functional": ["functional", "unit", "positive", "negative"],
            "performance": ["performance", "load", "stress"],
            "integration": ["e2e", "integration"],
            "quality": ["edge_cases", "boundary"],
            "business": ["happy_path", "acceptance", "smoke"],
        }

        return type_mappings.get(test_type, [])

    @classmethod
    def register_template(
        cls,
        category: str,
        template_class: Type[PromptTemplate],
        description: str = "",
        technique: str = "",
    ) -> None:
        """Register a new template category.

        Args:
            category: Category name
            template_class: Template class implementing PromptTemplate
            description: Category description
            technique: Prompting technique used
        """
        cls._templates[category.lower().strip()] = template_class

        if description:
            cls._category_descriptions[category.lower().strip()] = description

        if technique:
            cls._prompting_techniques[category.lower().strip()] = technique

    @classmethod
    def get_template_info(cls) -> Dict[str, Dict[str, str]]:
        """Get complete information about all available templates.

        Returns:
            Dictionary mapping categories to their information
        """
        info = {}

        for category in cls.get_available_categories():
            info[category] = cls.get_category_info(category)

        return info

    @classmethod
    def validate_category(cls, category: str) -> bool:
        """Validate if a category exists.

        Args:
            category: Category name to validate

        Returns:
            True if category exists, False otherwise
        """
        return category.lower().strip() in cls._templates

    @classmethod
    def suggest_categories(cls, query: str) -> List[str]:
        """Suggest categories based on a query string.

        Args:
            query: Search query

        Returns:
            List of suggested categories
        """
        query = query.lower().strip()
        suggestions = []

        # Direct matches
        for category in cls._templates.keys():
            if query in category:
                suggestions.append(category)

        # Description matches
        for category, description in cls._category_descriptions.items():
            if query in description.lower() and category not in suggestions:
                suggestions.append(category)

        # Keyword mappings
        keyword_mappings = {
            "rest": ["api"],
            "http": ["api"],
            "selenium": ["webui"],
            "appium": ["mobileui"],
            "pytest": ["unit", "functional"],
            "jest": ["unit"],
            "cypress": ["webui", "e2e"],
            "automation": ["webui", "mobileui", "api"],
            "load": ["performance"],
            "stress": ["performance"],
            "security": ["negative", "edge_cases"],
            "validation": ["positive", "functional"],
        }

        for keyword, categories in keyword_mappings.items():
            if keyword in query:
                for category in categories:
                    if category not in suggestions:
                        suggestions.append(category)

        return suggestions[:5]  # Limit to top 5 suggestions
