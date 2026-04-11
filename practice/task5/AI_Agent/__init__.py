"""
AI-Powered Unit Test Case Generation System
A unified LangChain pipeline for generating comprehensive unit test cases from user stories.
"""

__version__ = "1.0.0"
__author__ = "AI Test Generation Team"

from .core import KnowledgeBaseAnalyzer, TemplateCatalog, UnitTestGenerator, LangChainPipeline, Config, PromptTemplateLoader, PromptAnalyzer, UserStoryAcceptanceCriteriaAnalyzer
from .models import UnitComponentType, TestingPattern, CodeUnit, UserStory, UnitTestTemplate, GeneratedTest, TestSuite, TestGenerationRequest, TestGenerationResponse

# Make integrations optional
try:
    from integrations.ai_integration_manager import AIIntegrationManager
    from integrations.ollama_integration import OllamaIntegration
    from integrations.gemini_integration import GeminiIntegration
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False

__all__ = [
    "KnowledgeBaseAnalyzer", "TemplateCatalog", "UnitTestGenerator", "LangChainPipeline", "Config", "PromptTemplateLoader", "PromptAnalyzer", "UserStoryAcceptanceCriteriaAnalyzer",
    "UnitComponentType", "TestingPattern", "CodeUnit", "UserStory", "UnitTestTemplate", "GeneratedTest", "TestSuite", "TestGenerationRequest", "TestGenerationResponse",
]

if INTEGRATIONS_AVAILABLE:
    __all__.extend([
        "OllamaIntegration", "GeminiIntegration", "AIIntegrationManager",
    ])
