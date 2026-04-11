#!/usr/bin/env python3
"""
Simple test demo for the AI-Powered Unit Test Case Generation System.
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models import UserStory, CodeUnit, UnitComponentType
from template_catalog import TemplateCatalog
from knowledge_analyzer import KnowledgeBaseAnalyzer
from test_generator import UnitTestGenerator
from langchain_pipeline import LangChainPipeline


def test_models():
    """Test the data models."""
    print("🧪 Testing data models...")
    
    # Test UserStory
    user_story = UserStory(
        title="Test Story",
        description="A test user story",
        acceptance_criteria=["Criteria 1", "Criteria 2"],
        priority="high",
        complexity="medium"
    )
    
    assert user_story.title == "Test Story"
    assert len(user_story.acceptance_criteria) == 2
    print("✅ UserStory model works correctly")
    
    # Test CodeUnit
    code_unit = CodeUnit(
        name="test_function",
        file_path="test.py",
        component_type=UnitComponentType.PURE_FUNCTION,
        signature="test_function() -> str",
        dependencies=["os"],
        return_type="str",
        parameters=[{"name": "param1", "type": "str", "required": True}],
        business_logic="Test function logic",
        error_conditions=["Test error"]
    )
    
    assert code_unit.name == "test_function"
    assert code_unit.component_type == UnitComponentType.PURE_FUNCTION
    print("✅ CodeUnit model works correctly")


def test_template_catalog():
    """Test the template catalog."""
    print("\n🧪 Testing template catalog...")
    
    catalog = TemplateCatalog()
    
    # Test template selection
    user_story = UserStory(
        title="Test",
        description="Test description",
        acceptance_criteria=["Test criteria"],
        priority="medium",
        complexity="medium"
    )
    
    code_units = [
        CodeUnit(
            name="pure_func",
            file_path="test.py",
            component_type=UnitComponentType.PURE_FUNCTION,
            signature="pure_func() -> str",
            dependencies=[],
            return_type="str",
            parameters=[],
            business_logic="Pure function",
            error_conditions=[]
        )
    ]
    
    template = catalog.select_template(user_story, code_units)
    assert template.component_type == UnitComponentType.PURE_FUNCTION
    print("✅ Template catalog works correctly")


def test_knowledge_analyzer():
    """Test the knowledge analyzer."""
    print("\n🧪 Testing knowledge analyzer...")
    
    analyzer = KnowledgeBaseAnalyzer()
    
    # Test default code units
    code_units = analyzer._get_default_code_units()
    assert len(code_units) > 0
    assert any(unit.name == "render_email_template" for unit in code_units)
    print("✅ Knowledge analyzer works correctly")


def test_test_generator():
    """Test the test generator."""
    print("\n🧪 Testing test generator...")
    
    generator = UnitTestGenerator()
    
    # Test user story parsing
    user_story = generator._parse_user_story("Title\nDescription\n- Criteria 1\n- Criteria 2")
    assert user_story.title == "Title"
    assert user_story.description == "Description"
    assert len(user_story.acceptance_criteria) == 2
    print("✅ Test generator works correctly")


def test_langchain_pipeline():
    """Test the LangChain pipeline."""
    print("\n🧪 Testing LangChain pipeline...")
    
    pipeline = LangChainPipeline()
    
    # Test pipeline status
    status = pipeline.get_pipeline_status()
    assert "generator_ready" in status
    assert status["generator_ready"] == True
    print("✅ LangChain pipeline works correctly")
    
    # Test user story validation
    validation = pipeline.validate_user_story("Valid user story with enough content")
    assert validation["valid"] == True
    print("✅ User story validation works correctly")


def run_demo():
    """Run a simple demo of the system."""
    print("🚀 Running AI-Powered Unit Test Case Generation System Demo")
    print("=" * 60)
    
    # Test all components
    test_models()
    test_template_catalog()
    test_knowledge_analyzer()
    test_test_generator()
    test_langchain_pipeline()
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! System is working correctly.")
    print("=" * 60)
    
    # Run a simple test generation
    print("\n🔧 Testing test generation...")
    
    pipeline = LangChainPipeline()
    user_story = """Simple Test Story
As a developer, I want to test the system so that I can verify it works.
- System accepts input
- System processes input
- System returns output"""
    
    response = pipeline.generate_tests_for_story(user_story)
    
    if response.success:
        print(f"✅ Generated {len(response.test_suite.test_cases)} test cases")
        
        # Export as Python
        python_code = pipeline.export_test_suite(response, "python")
        with open("demo_generated_tests.py", "w") as f:
            f.write(python_code)
        print("✅ Demo tests saved to: demo_generated_tests.py")
        
        # Export as Markdown
        markdown_content = pipeline.export_test_suite(response, "markdown")
        with open("demo_test_suite.md", "w") as f:
            f.write(markdown_content)
        print("✅ Demo report saved to: demo_test_suite.md")
        
        print("\n📊 Test Suite Summary:")
        print(f"  - Template: {response.test_suite.template_selection}")
        print(f"  - Units Mapped: {len(response.test_suite.unit_mapping)}")
        print(f"  - Test Cases: {len(response.test_suite.test_cases)}")
        print(f"  - Mock Specifications: {len(response.test_suite.mock_specifications)}")
        
    else:
        print(f"❌ Test generation failed: {response.error_message}")


if __name__ == "__main__":
    run_demo()
