# AI-Powered Unit Test Case Generation System - Project Structure

## 📁 **Project Organization**

```
AI_Agent/
├── 📁 core/                           # Core system components
│   ├── __init__.py                    # Core package initialization
│   ├── knowledge_analyzer.py          # Code analysis engine
│   ├── template_catalog.py            # Test template management
│   ├── test_generator.py              # Test generation engine
│   ├── langchain_pipeline.py          # Main pipeline orchestration
│   └── config.py                      # Configuration management
│
├── 📁 models/                         # Data models and enums
│   ├── __init__.py                    # Models package initialization
│   └── models.py                      # Core data structures
│
├── 📁 integrations/                   # AI service integrations
│   ├── __init__.py                    # Integrations package initialization
│   ├── ollama_integration.py          # Ollama (phi3:mini) integration
│   ├── gemini_integration.py          # Google Gemini API integration
│   └── ai_integration_manager.py      # Unified AI integration manager
│
├── 📁 scripts/                        # Executable scripts and tools
│   ├── __init__.py                    # Scripts package initialization
│   ├── main.py                        # Main application entry point
│   ├── generate_knowledge_base.py     # Source code analysis tool
│   └── setup_ai.py                    # AI integration setup tool
│
├── 📁 tests/                          # Test files and demos
│   ├── __init__.py                    # Tests package initialization
│   └── test_demo.py                   # System testing and demo
│
├── 📁 docs/                           # Documentation
│   ├── README.md                      # Main project documentation
│   └── design.md                      # System design documentation
│
├── 📁 examples/                       # Example outputs and demos
│   ├── demo_generated_tests.py        # Example generated test cases
│   └── demo_test_suite.md             # Example test suite output
│
├── 📁 utils/                          # Utility files and resources
│   ├── requirements.txt               # Python dependencies
│   ├── env_template.txt               # Environment configuration template
│   └── knowledge_base.json            # Generated knowledge base
│
├── 📁 venv/                           # Virtual environment (if created)
├── __init__.py                        # Main package initialization
└── PROJECT_STRUCTURE.md               # This file
```

## 🎯 **Package Purposes**

### **`core/`** - Core System Components
- **`knowledge_analyzer.py`**: Analyzes source code to extract testable units
- **`template_catalog.py`**: Manages test templates and selection logic
- **`test_generator.py`**: Generates test cases using selected templates
- **`langchain_pipeline.py`**: Orchestrates the entire test generation pipeline
- **`config.py`**: Centralized configuration management

### **`models/`** - Data Structures
- **`models.py`**: Defines all data models, enums, and Pydantic schemas
- **Component types, testing patterns, user stories, test suites, etc.**

### **`integrations/`** - AI Service Integrations
- **`ollama_integration.py`**: Integration with local Ollama (phi3:mini)
- **`gemini_integration.py`**: Integration with Google Gemini API
- **`ai_integration_manager.py`**: Unified manager for all AI services

### **`scripts/`** - Executable Tools
- **`main.py`**: Main application for test generation
- **`generate_knowledge_base.py`**: Analyzes codebase and generates knowledge base
- **`setup_ai.py`**: Sets up and tests AI integrations

### **`tests/`** - Testing and Validation
- **`test_demo.py`**: Comprehensive testing and demonstration of the system

### **`docs/`** - Documentation
- **`README.md`**: Complete project documentation
- **`design.md`**: System architecture and design decisions

### **`examples/`** - Sample Outputs
- **`demo_generated_tests.py`**: Example generated test cases
- **`demo_test_suite.md`**: Example test suite documentation

### **`utils/`** - Utilities and Resources
- **`requirements.txt`**: Python package dependencies
- **`env_template.txt`**: Environment configuration template
- **`knowledge_base.json`**: Generated knowledge base from code analysis

## 🚀 **Usage Examples**

### **Generate Knowledge Base from Source Code**
```bash
cd AI_Agent
python scripts/generate_knowledge_base.py
```

### **Run Main Application**
```bash
cd AI_Agent
python scripts/main.py
```

### **Test AI Integrations**
```bash
cd AI_Agent
python scripts/setup_ai.py
```

### **Run System Tests**
```bash
cd AI_Agent
python tests/test_demo.py
```

## 🔧 **Import Structure**

### **From Core Components**
```python
from core import KnowledgeBaseAnalyzer, TemplateCatalog, UnitTestGenerator
from core import LangChainPipeline, Config
```

### **From Models**
```python
from models import CodeUnit, UserStory, TestSuite, UnitComponentType
```

### **From AI Integrations**
```python
from integrations import OllamaIntegration, GeminiIntegration, AIIntegrationManager
```

### **From Scripts**
```python
from scripts import SourceCodeKnowledgeBaseGenerator, setup_environment
```

## 📋 **Key Benefits of This Organization**

1. **🧹 Clean Separation**: Each package has a clear, single responsibility
2. **🔧 Easy Maintenance**: Related functionality is grouped together
3. **📦 Modular Design**: Components can be imported and used independently
4. **🧪 Clear Testing**: Test files are organized and easy to find
5. **📚 Better Documentation**: Documentation is centralized and organized
6. **🚀 Simple Deployment**: Clear structure for packaging and distribution
7. **👥 Team Collaboration**: Different team members can work on different packages
8. **📈 Scalability**: Easy to add new features and integrations

## 🔄 **Updating Import Statements**

After reorganization, you may need to update import statements in some files. The `__init__.py` files provide clean import interfaces for each package.

## 📝 **Next Steps**

1. **Test the reorganized structure** by running the scripts
2. **Update any import statements** that may have broken paths
3. **Verify all functionality** works as expected
4. **Consider adding more examples** in the examples folder
5. **Expand documentation** for each package as needed
