from central_logger.logger import get_logger
from base_factory.base_agent import BaseTestGeneratorAgent
from java_core.java_test_generator_agent import JavaTestGeneratorAgent

logger = get_logger(__name__)


class TestGeneratorFactory:
    """Factory class to create appropriate test generator agents based on language"""
    
    @staticmethod
    def create_agent(language: str) -> BaseTestGeneratorAgent:
        """Create and return appropriate test generator agent for the given language"""
        language = language.lower()
        
        if language == 'java':
            logger.info(" Creating Java Test Generator Agent")
            return JavaTestGeneratorAgent()
        else:
            raise ValueError(f"Unsupported language: {language}. Currently only 'java' is supported.")
    
    @staticmethod
    def get_supported_languages():
        """Return list of supported languages"""
        return ['java']