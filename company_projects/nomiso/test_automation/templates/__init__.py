"""Test automation prompt templates."""

from .template_factory import TemplateFactory
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

__all__ = [
    "TemplateFactory",
    "APITestTemplate",
    "UnitTestTemplate",
    "WebUITestTemplate",
    "MobileUITestTemplate",
    "EdgeCaseTestTemplate",
    "PerformanceTestTemplate",
    "PositiveTestTemplate",
    "NegativeTestTemplate",
    "HappyPathTestTemplate",
    "FunctionalTestTemplate",
    "E2ETestTemplate",
]
