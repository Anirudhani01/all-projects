AI-Powered Integration Test Generator

An intelligent test generation agent that automatically creates comprehensive integration tests for Java and Python applications using AI-powered analysis and LangGraph workflow orchestration.

Features:

Fully Automated Workflow: Processes all methods automatically without manual intervention.

AI-Powered Method Analysis: Understands method functionality and dependencies using OpenAI models.

Flow-Based Test Generation: Generates tests based on business flow analysis rather than simple unit tests.

Smart Dependency Extraction: Automatically identifies internal and external dependencies.

Knowledge Base Integration: Optional enhancement using base_kb_loader for smarter test generation.

Retry Logic: Automatic retries for failed tests with detailed logging.

Real-time Execution: Generates and executes tests immediately using Gradle (for Java) or pytest (for Python).

Multi-Language Support: Java and Python test generation through a unified factory interface.

Prerequisites

Python 3.8+

Java 8+ (for Java test generation)

Gradle (with gradlew wrapper in your project)

OpenAI API key configured in environment variables

Installation

Clone the repository:

git clone <repo_url>
cd integration-test-agent-copy


Create a Python virtual environment:

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Create a .env file in the root directory and configure required settings:

OPENAI_API_KEY=<your_api_key>
model=gpt-4o
temperature=0.1
max_tokens=4000
PROJECT_ROOT=C:\opencrx
LANGUAGE=java

Usage

Run the test generator:

python main.py --file <path_to_source_file>


Generates integration tests automatically for all methods in the source file.

Analyzes method dependencies, generates flow-based tests, saves files, and executes them.

Summarizes completed and skipped methods, and outputs the generated test file location.

Output

Integration Test Files:

JUnit 5 test classes for Java

pytest test modules for Python

Flow Analysis: JSON files describing business flows.

Debug Outputs: Raw AI responses and intermediate processing results.

Execution Logs: Detailed logs of the workflow and test execution.

Test Naming Convention
{FlowName}IntegrationTest.java   # Java
{FlowName}_test.py                # Python

Project Structure
C:\integration-test-agent-copy
├── main.py
├── requirements.txt
├── .env
├── KB/                     # Optional knowledge base
│   └── __init__.py
├── base_factory/           # Factory for test generator agents
│   └── test_generator_factory.py
├── base_kb_loader/         # Knowledge base loader
│   └── kb_loader.py
├── java_core/              # Java-specific logic
│   ├── java_test_generator_agent.py
│   ├── prompt.py
│   └── nodes/
│       ├── parse_input.py
│       └── extract_dependencies.py
├── select_method/          # Automated method selection logic
│   └── select_method.py
├── base_executor/          # Saving and executing tests
│   ├── save_test_file.py
│   └── execute_test.py
├── analyze_method/
│   └── analyze_method.py
├── flow_analyzer/
│   └── flow_analyzer.py
├── generate_test/
│   └── generate_test.py
└── core/
    ├── agent_state.py
    └── logger.py

Workflow Architecture

Parse Input: Extracts methods from the source file.

Select Method: Automatically selects all detected methods.

Analyze Method: AI-powered method analysis.

Extract Dependencies: Resolves required internal and external dependencies.

Flow Analysis: Generates business flow representation.

Knowledge Base Lookup (optional): Enhances test logic using kb_loader.

Generate Test: Creates integration tests.

Save Test: Writes test files to the appropriate directory.

Execute Test: Runs tests and captures results.

Includes automatic retry logic and detailed logging at each step.

Factory & Multi-Language Support

TestGeneratorFactory automatically provides the correct agent based on language:

from base_factory.test_generator_factory import TestGeneratorFactory

agent = TestGeneratorFactory.create_agent("java")
result = agent.generate_test("path/to/MyClass.java")


Supported languages:

Java

Python

Logging & Debugging

Logs: Captured via core/logger.py.