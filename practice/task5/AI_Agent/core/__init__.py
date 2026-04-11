"""
Core components of the AI-Powered Unit Test Case Generation System.
"""

from .knowledge_analyzer import KnowledgeBaseAnalyzer
from .template_catalog import TemplateCatalog
from .test_generator import UnitTestGenerator
from .langchain_pipeline import LangChainPipeline
from .config import Config
from .prompt_loader import PromptTemplateLoader
from .prompt_analyzer import PromptAnalyzer
from .acceptance_criteria_analyzer import UserStoryAcceptanceCriteriaAnalyzer

# Make integrations optional
try:
    from integrations.ai_integration_manager import AIIntegrationManager
    from integrations.ollama_integration import OllamaIntegration
    from integrations.gemini_integration import GeminiIntegration
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False

__all__ = [
    "KnowledgeBaseAnalyzer",
    "TemplateCatalog", 
    "UnitTestGenerator",
    "LangChainPipeline",
    "Config",
    "PromptTemplateLoader",
    "PromptAnalyzer"
]
