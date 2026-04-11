"""
Tests for configuration and settings
"""

import pytest
from app.config import settings

class TestConfiguration:
    """Test class for configuration settings"""
    
    def test_settings_initialization(self):
        """Test that settings are properly initialized"""
        assert settings.app_name == "MoodBooster API"
        assert isinstance(settings.debug, bool)
        assert isinstance(settings.database_url, str)
        assert "mysql+pymysql://" in settings.database_url
    
    def test_llm_settings(self):
        """Test LLM-related settings"""
        assert isinstance(settings.gemini_api_key, (str, type(None)))
        assert isinstance(settings.ollama_base_url, str)
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.ollama_model == "phi3:mini"
    
    def test_fallback_settings(self):
        """Test fallback configuration settings"""
        assert isinstance(settings.use_gemini, bool)
        assert isinstance(settings.use_ollama, bool)
        assert isinstance(settings.use_keyword_fallback, bool)
        
        # At least one fallback should be enabled
        assert settings.use_gemini or settings.use_ollama or settings.use_keyword_fallback
    
    def test_ai_ml_settings(self):
        """Test AI/ML model settings"""
        assert isinstance(settings.huggingface_model, str)
        assert isinstance(settings.spacy_model, str)
        assert len(settings.huggingface_model) > 0
        assert len(settings.spacy_model) > 0
    
    def test_database_url_format(self):
        """Test database URL format"""
        db_url = settings.database_url
        
        # Should contain MySQL connection string
        assert "mysql+pymysql://" in db_url
        assert "@localhost:3306/" in db_url
        assert "moodbooster" in db_url
    
    def test_environment_variables(self):
        """Test that environment variables can be loaded"""
        # This test ensures the .env file loading works
        # The actual values depend on the environment
        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'gemini_api_key')
        assert hasattr(settings, 'ollama_base_url')
        assert hasattr(settings, 'ollama_model')
    
    def test_settings_types(self):
        """Test that all settings have correct types"""
        # String settings
        string_settings = [
            'app_name', 'database_url', 'huggingface_model', 
            'spacy_model', 'ollama_base_url', 'ollama_model'
        ]
        
        for setting in string_settings:
            value = getattr(settings, setting)
            assert isinstance(value, str), f"{setting} should be string, got {type(value)}"
        
        # Boolean settings
        bool_settings = ['debug', 'use_gemini', 'use_ollama', 'use_keyword_fallback']
        
        for setting in bool_settings:
            value = getattr(settings, setting)
            assert isinstance(value, bool), f"{setting} should be bool, got {type(value)}"
        
        # Optional string settings
        optional_string_settings = ['gemini_api_key']
        
        for setting in optional_string_settings:
            value = getattr(settings, setting)
            assert isinstance(value, (str, type(None))), f"{setting} should be str or None, got {type(value)}"
