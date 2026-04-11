#!/usr/bin/env python3
"""
Setup script for LLM integration
"""

import os
import sys

def setup_environment():
    """Setup environment variables for LLM integration"""
    
    env_content = """DATABASE_URL=mysql+pymysql://anirudh:password123@localhost:3306/moodbooster
HUGGINGFACE_MODEL=distilbert-base-uncased-finetuned-sst-2-english
SPACY_MODEL=en_core_web_sm
DEBUG=false

# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# Fallback Settings
USE_GEMINI=true
USE_OLLAMA=true
USE_KEYWORD_FALLBACK=true
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file created (.env)")
    print("📝 Please update GEMINI_API_KEY with your actual API key")

def install_dependencies():
    """Install LLM dependencies"""
    print("📦 Installing LLM dependencies...")
    os.system("pip install google-generativeai ollama openai langchain langchain-community")

def setup_ollama():
    """Setup Ollama with phi3:mini model"""
    print("🦙 Setting up Ollama...")
    print("1. Install Ollama from https://ollama.ai/")
    print("2. Run: ollama pull phi3:mini")
    print("3. Start Ollama service: ollama serve")

def main():
    print("🚀 Setting up LLM integration for MoodBooster")
    print("=" * 50)
    
    setup_environment()
    install_dependencies()
    setup_ollama()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Get your Gemini API key from https://makersuite.google.com/app/apikey")
    print("2. Update the GEMINI_API_KEY in .env file")
    print("3. Install and setup Ollama with phi3:mini model")
    print("4. Restart the backend server")

if __name__ == "__main__":
    main()
