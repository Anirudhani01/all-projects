# 🤖 Advanced Test Automation Framework

A sophisticated test automation framework that leverages AI and advanced prompting techniques to generate comprehensive test suites for any application. Built with Chain-of-Thought reasoning, Few-Shot Learning, Tree-of-Thoughts exploration, Role-Based prompting, and Metacognitive reflection.

## 🌟 Features

### 🧠 Sophisticated Prompting Techniques
- **Chain-of-Thought (CoT)**: Step-by-step reasoning for complex test scenarios
- **Few-Shot Learning**: Pattern-based learning from examples
- **Tree-of-Thoughts (ToT)**: Multi-path exploration for comprehensive coverage
- **Role-Based Prompting**: Expert domain knowledge integration
- **Metacognitive Prompting**: Self-reflection on test quality and failure modes

### 🔄 Complete Agent Chain Workflow
1. **Test Generation Agent**: AI-powered test case generation
2. **Validation Agent**: Quality assurance and completeness checking
3. **Execution Agent**: Test running and results collection
4. **Report Generator**: Comprehensive analysis and recommendations

### 🎯 Multiple Test Categories
- **API Testing**: REST endpoints, authentication, validation
- **Unit Testing**: Function-level testing with mocking
- **WebUI Testing**: Selenium-based user interface testing
- **Mobile UI Testing**: iOS/Android app testing
- **Edge Case Testing**: Boundary conditions and error scenarios
- **Performance Testing**: Load, stress, and scalability testing
- **Positive/Negative Testing**: Valid and invalid input scenarios
- **Happy Path Testing**: Optimal user journey validation
- **Functional Testing**: Feature and requirement validation
- **End-to-End Testing**: Complete workflow testing

### 🔌 LLM Provider Abstraction
- **Ollama**: Local LLM support (default: llama3.1:8b-instruct-q8_0)
- **OpenAI**: Cloud-based models with hot-swappable configuration
- **Extensible**: Easy to add new LLM providers

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- UV package manager
- Ollama (for local LLM) or OpenAI API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ecommerce-test-automation

# Install dependencies with UV
uv sync

# Start Ollama (if using local LLM)
ollama serve
ollama pull llama3.1:8b-instruct-q8_0
```

### Basic Usage

```bash
# Check available test categories
uv run python -m test_automation.main list-categories

# Check LLM provider status
uv run python -m test_automation.main check-llm

# Run complete workflow for API tests
uv run python -m test_automation.main run-workflow \
  --programming-language Python \
  --testing-framework pytest \
  --test-cases data/test_cases.json \
  --categories api \
  --knowledge-base knowledge_base/ecommerce_knowledge_base.md \
  --output-dir ./test_output

# Run for multiple categories
uv run python -m test_automation.main run-workflow \
  --programming-language Python \
  --testing-framework pytest \
  --test-cases data/test_cases.json \
  --categories api unit webui performance \
  --knowledge-base knowledge_base/ecommerce_knowledge_base.md \
  --output-dir ./test_output \
  --verbose

# Run for all available categories
uv run python -m test_automation.main run-workflow \
  --programming-language Python \
  --testing-framework pytest \
  --test-cases data/test_cases.json \
  --all-categories \
  --knowledge-base knowledge_base/ecommerce_knowledge_base.md \
  --output-dir ./test_output
```

### Demo Script

```bash
# Run the comprehensive demo
uv run python demo.py
```

## 🏗️ Architecture

### Core Components

```
test_automation/
├── agents/                 # Agent chain orchestration
│   ├── base_agent.py      # Base agent interface
│   ├── test_generation_agent.py  # Test case generation
│   ├── validation_agent.py       # Quality validation
│   ├── execution_agent.py        # Test execution
│   └── agent_chain.py            # Workflow orchestration
├── generators/            # Test case and code generators
│   ├── test_generator.py  # Main test generation logic
│   └── code_generator.py  # Code file generation
├── llm/                   # LLM abstraction layer
│   ├── base.py           # LLM provider interface
│   ├── ollama_provider.py # Ollama integration
│   ├── openai_provider.py # OpenAI integration
│   └── factory.py        # Provider factory
├── templates/             # Advanced prompt templates
│   ├── base_templates.py  # Template base classes
│   ├── test_generation_templates.py  # Main test templates
│   ├── specialized_templates.py      # Specialized templates
│   └── template_factory.py          # Template management
├── runners/               # Test execution and reporting
│   └── report_generator.py # Comprehensive reporting
└── main.py               # CLI interface
```

### Ecommerce CLI Application

```
ecommerce_cli/
├── models.py             # Pydantic data models
├── services.py           # Business logic and data access
└── main.py              # CLI commands
```

## 📊 Sample Output

### Test Generation Results
```json
{
  "test_suite_name": "API Test Suite",
  "framework": "pytest",
  "language": "Python",
  "test_cases": [
    {
      "test_name": "test_create_product_with_valid_data",
      "description": "Test successful product creation with valid input data",
      "category": "api",
      "priority": "high",
      "http_method": "POST",
      "endpoint": "/api/products",
      "request_body": {
        "name": "Test Product",
        "price": 99.99,
        "category": "electronics"
      },
      "expected_status_code": 201,
      "assertions": [
        "Response contains product ID",
        "Product name matches input",
        "Price is correctly stored"
      ]
    }
  ]
}
```

### Generated Test Code
```python
import pytest
import requests

class TestAPITestSuite:
    """Generated API test suite"""
    
    def test_create_product_with_valid_data(self):
        """Test successful product creation with valid input data"""
        headers = {"Content-Type": "application/json"}
        request_data = {
            "name": "Test Product",
            "price": 99.99,
            "category": "electronics"
        }
        
        response = requests.post(
            url="/api/products",
            headers=headers,
            json=request_data
        )
        
        assert response.status_code == 201
        response_data = response.json()
        assert "id" in response_data
        assert response_data["name"] == "Test Product"
        assert response_data["price"] == 99.99
```

## 🎯 Advanced Usage

### Custom Configuration

```python
from test_automation.agents import AgentChain

# Initialize with custom configuration
agent_chain = AgentChain(
    llm_provider="ollama",
    model="llama3.1:8b-instruct-q8_0",
    host="http://localhost:11434"
)

# Run with custom workflow configuration
workflow_config = {
    "generation": {
        "temperature": 0.8,
        "max_tokens": 4000
    },
    "validation": {
        "strict_mode": True
    },
    "execution": {
        "enabled": True,
        "generate_html_report": True
    }
}

result = await agent_chain.run_complete_workflow(
    programming_language="Python",
    testing_framework="pytest",
    test_cases_file="my_test_cases.json",
    categories=["api", "unit"],
    workflow_config=workflow_config
)
```

### Using OpenAI Provider

```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run with OpenAI
uv run python -m test_automation.main run-workflow \
  --llm-provider openai \
  --model gpt-4o-mini \
  --programming-language Python \
  --testing-framework pytest \
  --test-cases data/test_cases.json \
  --categories api \
  --output-dir ./test_output
```

## 🔧 Configuration

### Test Cases JSON Structure
```json
{
  "application_info": {
    "name": "Your Application",
    "description": "Application description"
  },
  "test_scenarios": {
    "category_name": {
      "scenarios": [
        {
          "scenario_id": "TEST_001",
          "title": "Test Scenario Title",
          "description": "Detailed description",
          "priority": "high",
          "test_data": {
            "valid_input": {},
            "invalid_input": {}
          }
        }
      ]
    }
  }
}
```

### Knowledge Base Format
The knowledge base should be a markdown file containing:
- Application overview and architecture
- Business rules and requirements
- API endpoints and data models
- User workflows and scenarios
- Security considerations
- Performance requirements

## 📈 Reports and Analytics

The framework generates comprehensive reports including:

### Executive Summary
- Workflow status and duration
- Success rates and key metrics
- Critical issues and highlights

### Detailed Analysis
- Stage-by-stage breakdown
- Quality metrics and scores
- Performance indicators

### Failure Analysis
- Root cause analysis (AI-powered)
- Failure categorization
- Impact assessment
- Resolution strategies

### Recommendations
- Immediate actions required
- Short-term improvements
- Long-term strategies
- Best practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

See `pyproject.toml` for complete dependency list. Key dependencies:
- `ollama>=0.2.1` - Local LLM integration
- `openai>=1.3.0` - OpenAI API integration
- `pydantic>=2.5.0` - Data validation
- `jinja2>=3.1.2` - Template engine
- `pytest>=7.4.0` - Testing framework
- `selenium>=4.15.0` - WebUI testing
- `rich>=13.7.0` - Beautiful CLI output

## 🐛 Troubleshooting

### Common Issues

1. **LLM Connection Failed**
   ```bash
   # Check if Ollama is running
   ollama list
   
   # Pull the required model
   ollama pull llama3.1:8b-instruct-q8_0
   ```

2. **Import Errors**
   ```bash
   # Reinstall dependencies
   uv sync --reinstall
   ```

3. **Test Generation Fails**
   - Check test_cases.json format
   - Verify knowledge base file exists
   - Ensure sufficient disk space for outputs

### Debug Mode
```bash
# Run with verbose output
uv run python -m test_automation.main run-workflow \
  --verbose \
  [other options]
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LLaMA 3.1** for powerful local language model capabilities
- **Ollama** for easy local LLM deployment
- **OpenAI** for pioneering AI language models
- **FastAPI** and **Pydantic** for excellent Python frameworks
- **Rich** for beautiful terminal output

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the demo script for examples

---

**Built with ❤️ using sophisticated prompting techniques and AI-powered test generation**
