"""
Unified AI Integration Manager for the AI-Powered Unit Test Case Generation System.
Supports both Ollama (phi3:mini) and Google Gemini models.
"""

import os
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from .ollama_integration import OllamaIntegration
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from .gemini_integration import GeminiIntegration
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIIntegrationManager:
    """Manages AI integrations for test generation."""
    
    def __init__(self, preferred_model: str = "auto"):
        """
        Initialize the AI integration manager.
        
        Args:
            preferred_model: "auto", "ollama", "gemini", or "local"
        """
        self.preferred_model = preferred_model
        self.ollama_integration = None
        self.gemini_integration = None
        self.active_integration = None
        
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Initialize available AI integrations."""
        # Initialize Ollama integration
        if OLLAMA_AVAILABLE:
            try:
                ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                ollama_model = os.getenv("OLLAMA_MODEL", "phi3:mini")
                self.ollama_integration = OllamaIntegration(
                    model_name=ollama_model,
                    base_url=ollama_url
                )
            except Exception as e:
                print(f"Warning: Failed to initialize Ollama integration: {e}")
        
        # Initialize Gemini integration
        if GEMINI_AVAILABLE:
            try:
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                if gemini_api_key:
                    self.gemini_integration = GeminiIntegration(api_key=gemini_api_key)
                else:
                    print("Warning: GEMINI_API_KEY not found in environment variables")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini integration: {e}")
        
        # Select active integration based on preference
        self._select_active_integration()
    
    def _select_active_integration(self):
        """Select the active AI integration based on preference and availability."""
        if self.preferred_model == "auto":
            # Try Gemini first (usually more reliable), then Ollama
            if self.gemini_integration and self.gemini_integration.is_available():
                self.active_integration = self.gemini_integration
                print("✅ Using Google Gemini for AI-powered test generation")
            elif self.ollama_integration and self.ollama_integration.is_available():
                self.active_integration = self.ollama_integration
                print("✅ Using Ollama (phi3:mini) for AI-powered test generation")
            else:
                self.active_integration = None
                print("⚠️  No AI integration available, falling back to local generation")
        
        elif self.preferred_model == "gemini":
            if self.gemini_integration and self.gemini_integration.is_available():
                self.active_integration = self.gemini_integration
                print("✅ Using Google Gemini for AI-powered test generation")
            else:
                print("❌ Gemini not available, falling back to local generation")
                self.active_integration = None
        
        elif self.preferred_model == "ollama":
            if self.ollama_integration and self.ollama_integration.is_available():
                self.active_integration = self.ollama_integration
                print("✅ Using Ollama (phi3:mini) for AI-powered test generation")
            else:
                print("❌ Ollama not available, falling back to local generation")
                self.active_integration = None
        
        elif self.preferred_model == "local":
            self.active_integration = None
            print("ℹ️  Using local generation mode (no AI integration)")
    
    def is_ai_available(self) -> bool:
        """Check if any AI integration is available."""
        return self.active_integration is not None
    
    def get_active_integration_info(self) -> Dict[str, Any]:
        """Get information about the active AI integration."""
        if not self.active_integration:
            return {
                "active": False,
                "provider": "Local Generation",
                "model": "None"
            }
        
        try:
            info = self.active_integration.get_model_info()
            info["active"] = True
            return info
        except Exception as e:
            return {
                "active": False,
                "provider": "Unknown",
                "model": "Unknown",
                "error": str(e)
            }
    
    def generate_test_cases(self, user_story: str, code_units: list, template_info: dict) -> Dict[str, Any]:
        """Generate test cases using the active AI integration."""
        if not self.active_integration:
            return {
                "success": False,
                "error": "No AI integration available",
                "generated_tests": [],
                "fallback": True
            }
        
        try:
            print(f"🤖 Generating test cases using {self.active_integration.__class__.__name__}...")
            result = self.active_integration.generate_test_cases(user_story, code_units, template_info)
            
            if result.get("success", False):
                print("✅ AI-generated test cases successfully created")
            else:
                print(f"⚠️  AI generation failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during AI generation: {e}")
            return {
                "success": False,
                "error": f"AI generation error: {str(e)}",
                "generated_tests": [],
                "fallback": True
            }
    
    def generate_text(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> Optional[str]:
        """Generate text using the active AI integration."""
        if not self.active_integration:
            print("⚠️  No AI integration available for text generation")
            return None
        
        try:
            print(f"🤖 Generating text using {self.active_integration.__class__.__name__}...")
            
            # Check if the active integration has generate_text method
            if hasattr(self.active_integration, 'generate_text'):
                result = self.active_integration.generate_text(prompt, max_tokens, temperature)
                if result:
                    print("✅ Text generated successfully")
                    return result
                else:
                    print("⚠️  Text generation returned empty result")
                    return None
            else:
                print("⚠️  Active integration doesn't support text generation")
                return None
                
        except Exception as e:
            print(f"❌ Error during text generation: {e}")
            return None
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test connections to all available AI services."""
        results = {
            "ollama": {"available": False, "connection": None},
            "gemini": {"available": False, "connection": None},
            "recommendation": None
        }
        
        # Test Ollama
        if self.ollama_integration:
            try:
                connection_info = self.ollama_integration.test_connection()
                results["ollama"] = {
                    "available": True,
                    "connection": connection_info
                }
            except Exception as e:
                results["ollama"]["connection"] = {"error": str(e)}
        
        # Test Gemini
        if self.gemini_integration:
            try:
                connection_info = self.gemini_integration.test_connection()
                results["gemini"] = {
                    "available": True,
                    "connection": connection_info
                }
            except Exception as e:
                results["gemini"]["connection"] = {"error": str(e)}
        
        # Provide recommendation
        if results["gemini"]["available"] and results["gemini"]["connection"].get("connected"):
            results["recommendation"] = "Use Gemini (more reliable, better performance)"
        elif results["ollama"]["available"] and results["ollama"]["connection"].get("connected"):
            results["recommendation"] = "Use Ollama (local, privacy-focused)"
        else:
            results["recommendation"] = "No AI integration available, use local generation"
        
        return results
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different AI model."""
        if model_name == "ollama" and self.ollama_integration:
            if self.ollama_integration.is_available():
                self.active_integration = self.ollama_integration
                print("✅ Switched to Ollama integration")
                return True
            else:
                print("❌ Ollama not available")
                return False
        
        elif model_name == "gemini" and self.gemini_integration:
            if self.gemini_integration.is_available():
                self.active_integration = self.gemini_integration
                print("✅ Switched to Gemini integration")
                return True
            else:
                print("❌ Gemini not available")
                return False
        
        elif model_name == "local":
            self.active_integration = None
            print("✅ Switched to local generation mode")
            return True
        
        else:
            print(f"❌ Model '{model_name}' not available")
            return False
    
    def get_status_summary(self) -> str:
        """Get a human-readable status summary."""
        if not self.active_integration:
            return "🔴 Local Generation Mode (No AI integration active)"
        
        try:
            info = self.active_integration.get_model_info()
            provider = info.get("provider", "Unknown")
            model = info.get("model_name", "Unknown")
            return f"🟢 AI-Powered Mode: {provider} - {model}"
        except Exception:
            return "🟡 AI Integration Active (Status unknown)"
