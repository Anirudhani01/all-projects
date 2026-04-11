# AI-Powered Unit Test Case Generation System

A unified LangChain pipeline for generating comprehensive unit test cases from user stories by intelligently selecting appropriate test templates and leveraging extracted codebase knowledge.

## 🚀 Features

### Core Capabilities
- **Intelligent Template Selection**: Automatically analyzes user stories to select optimal unit test templates
- **Codebase Analysis**: Extracts unit-level insights from source code using static analysis
- **Comprehensive Test Generation**: Creates positive, negative, boundary, and exception test cases
- **Mock Strategy Generation**: Provides detailed mock specifications for dependency isolation
- **Coverage Analysis**: Generates comprehensive test coverage reports
- **Multiple Export Formats**: Supports Python, JSON, and Markdown output

### Template Categories
- **Pure Function Templates**: For stateless, side-effect-free method testing
- **Business Logic Templates**: For isolated rule processing and calculation verification
- **Validation Component Templates**: For input sanitization and constraint checking units
- **Data Transformation Templates**: For data processing and formatting method testing
- **State Management Templates**: For object state manipulation and verification
- **Algorithm Templates**: For computational logic and mathematical operation testing

## 🏗️ Architecture

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Story    │───▶│  LangChain      │───▶│  Test Suite     │
│   Input         │    │  Pipeline       │    │  Output         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Core Engine     │
                       │  Components      │
                       └──────────────────┘
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              ┌─────────┐ ┌─────────┐ ┌─────────┐
              │Template │ │Knowledge│ │Test     │
              │Catalog  │ │Analyzer │ │Generator│
              └─────────┘ └─────────┘ └─────────┘
```

### Component Details
- **LangChainPipeline**: Main orchestration layer
- **TemplateCatalog**: Manages test templates and intelligent selection
- **KnowledgeBaseAnalyzer**: Extracts code units and maps to user stories
- **UnitTestGenerator**: Core test generation engine

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip or uv package manager

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd AI_Agent

# Install dependencies
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

## 🎯 Usage

### Basic Usage
```python
from AI_Agent.langchain_pipeline import LangChainPipeline

# Initialize pipeline
pipeline = LangChainPipeline()

# Generate tests for a user story
user_story = """
User Authentication System
As a user, I want to authenticate with email and password.
- System validates credentials
- System returns user object on success
- System returns None on failure
"""

response = pipeline.generate_tests_for_story(user_story)

if response.success:
    # Export as Python code
    python_tests = pipeline.export_test_suite(response, "python")
    
    # Export as Markdown
    markdown_report = pipeline.export_test_suite(response, "markdown")
```

### Command Line Interface
```bash
# Run full system with example user stories
python main.py

# Run demo mode
python main.py --demo

# Generate tests for specific codebase
python main.py --codebase-path /path/to/your/code
```

### Advanced Configuration
```python
# Custom configuration
response = pipeline.generate_tests_with_custom_config(
    user_story=user_story,
    codebase_path="/path/to/codebase",
    test_framework="pytest",
    include_mocks=True,
    include_coverage=True
)
```

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI API Key (optional - for future AI integration)
export OPENAI_API_KEY="your-api-key-here"

# Codebase path
export CODEBASE_PATH="/path/to/your/codebase"
```

### Pipeline Configuration
```python
# Get pipeline status
status = pipeline.get_pipeline_status()

# Validate user story before processing
validation = pipeline.validate_user_story(user_story)
```

## 📊 Output Examples

### Generated Test Case
```python
def test_authenticate_valid_inputs():
    """Test authenticate - positive case."""
    # Setup
    # Mock dependencies
    mock_session = Mock()
    
    # Prepare test data
    test_data = {"email": "user@example.com", "password": "securepass123"}
    
    # Act
    # result = authenticate(**test_data)
    
    # Assert
    assert result is not None
    assert isinstance(result, User)
    assert result.email == expected_email
```

### Coverage Analysis
```
Test Coverage Analysis:
- Total Test Cases: 12
- Positive Test Cases: 3 (25.0%)
- Negative Test Cases: 3 (25.0%)
- Boundary Test Cases: 3 (25.0%)
- Exception Test Cases: 3 (25.0%)

Coverage Areas:
- Input validation coverage: Complete
- Business logic coverage: Complete
- Error handling coverage: Complete
- Edge case coverage: Complete
- Mock dependency coverage: Complete
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=AI_Agent

# Run specific test file
pytest test_models.py
```

### Test Structure
```
AI_Agent/
├── tests/
│   ├── test_models.py
│   ├── test_template_catalog.py
│   ├── test_knowledge_analyzer.py
│   ├── test_test_generator.py
│   └── test_langchain_pipeline.py
```

## 🔍 Code Analysis

### Supported Code Patterns
- **Functions**: Pure functions, business logic functions
- **Methods**: Class methods, state management methods
- **Dependencies**: External libraries, database connections, APIs
- **Error Handling**: Exception raising, validation failures

### Analysis Features
- **AST Parsing**: Extracts function signatures and dependencies
- **Type Inference**: Determines parameter and return types
- **Business Logic Detection**: Identifies function purpose and behavior
- **Error Condition Analysis**: Finds potential failure points

## 🚀 Future Enhancements

### Planned Features
- **AI-Powered Generation**: Integration with OpenAI GPT models
- **Multi-Language Support**: Python, JavaScript, Java, C#
- **Test Data Generation**: Automatic test data creation
- **Performance Testing**: Load and stress test generation
- **Integration Testing**: End-to-end test scenario generation

### LangChain Integration
- **Chain Composition**: Modular pipeline construction
- **Memory Management**: Context-aware test generation
- **Tool Integration**: External API and database connectivity
- **Custom Prompts**: User-defined generation strategies

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black AI_Agent/
isort AI_Agent/

# Run linting
flake8 AI_Agent/
mypy AI_Agent/
```

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📚 Documentation

### API Reference
- **Models**: Data structures and validation
- **TemplateCatalog**: Template management and selection
- **KnowledgeBaseAnalyzer**: Code analysis and extraction
- **UnitTestGenerator**: Test generation engine
- **LangChainPipeline**: Main orchestration layer

### Examples
- **Basic Usage**: Simple test generation
- **Advanced Configuration**: Custom pipeline setup
- **Template Customization**: Creating custom templates
- **Integration**: Using with existing test frameworks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain**: For the pipeline architecture inspiration
- **Pydantic**: For data validation and serialization
- **Pytest**: For the testing framework foundation
- **FastAPI**: For the codebase analysis examples

## 📞 Support

### Getting Help
- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Documentation**: Comprehensive guides and examples
- **Examples**: Sample user stories and test outputs

### Community
- **GitHub**: Main repository and discussions
- **Discord**: Community chat and support
- **Blog**: Tutorials and best practices
- **Newsletter**: Updates and announcements

---

**Built with ❤️ for the testing community**
