#!/usr/bin/env python3
"""
Setup script for AI integrations in the AI-Powered Unit Test Case Generation System.
This script helps configure and test Ollama and Gemini integrations.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def setup_environment():
    """Set up the environment file."""
    env_file = Path(".env")
    env_template = Path("env_template.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_template.exists():
        print("📝 Creating .env file from template...")
        try:
            with open(env_template, 'r') as f:
                template_content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(template_content)
            
            print("✅ .env file created successfully!")
            print("📝 Please edit .env file and add your Gemini API key:")
            print("   GEMINI_API_KEY=your_actual_api_key_here")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ env_template.txt not found")
        return False

def test_ai_integrations():
    """Test all AI integrations."""
    print("\n🧪 Testing AI Integrations...")
    
    try:
        from ai_integration_manager import AIIntegrationManager
        
        # Test with auto selection
        print("\n🔍 Testing with auto model selection...")
        ai_manager = AIIntegrationManager(preferred_model="auto")
        
        # Get status
        status = ai_manager.get_status_summary()
        print(f"Status: {status}")
        
        # Test connections
        print("\n🔗 Testing all connections...")
        connections = ai_manager.test_all_connections()
        
        print("\n📊 Connection Test Results:")
        print(f"Ollama: {'✅ Available' if connections['ollama']['available'] else '❌ Not Available'}")
        if connections['ollama']['available']:
            print(f"  - Connection: {connections['ollama']['connection']}")
        
        print(f"Gemini: {'✅ Available' if connections['gemini']['available'] else '❌ Not Available'}")
        if connections['gemini']['available']:
            print(f"  - Connection: {connections['gemini']['connection']}")
        
        print(f"\n💡 Recommendation: {connections['recommendation']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed the required dependencies:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error testing integrations: {e}")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 AI-Powered Unit Test Case Generation System - Setup")
    print("=" * 60)
    
    # Step 1: Setup environment
    print("\n📝 Step 1: Setting up environment...")
    if not setup_environment():
        print("❌ Environment setup failed")
        return False
    
    # Step 2: Install dependencies
    print("\n📦 Step 2: Installing dependencies...")
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return False
    
    # Step 3: Test integrations
    print("\n🧪 Step 3: Testing AI integrations...")
    if not test_ai_integrations():
        print("❌ Integration testing failed")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your Gemini API key")
    print("2. Make sure Ollama is running with phi3:mini model")
    print("3. Run test_demo.py to test the system")
    print("4. Use main.py for full functionality")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
