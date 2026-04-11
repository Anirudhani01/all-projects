#!/usr/bin/env python3
"""
Main entry point for the AI-Powered Unit Test Case Generation System.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.langchain_pipeline import LangChainPipeline
from models.models import TestGenerationRequest


def main():
    """Main execution function for the unit test generator."""
    
    print("=== AI-Powered Unit Test Case Generation System ===")
    print("Version: 1.0.0")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = LangChainPipeline()
    
    # Check pipeline status
    status = pipeline.get_pipeline_status()
    print(f"\nPipeline Status:")
    for key, value in status.items():
        print(f"  - {key}: {value}")
    
    # Interactive user story input
    print(f"\n{'='*60}")
    print("📝 USER STORY INPUT")
    print(f"{'='*60}")
    
    # Get user story directly
    user_story = input("Enter your user story: ").strip()
    
    if not user_story:
        print("❌ No user story provided. Exiting.")
        return
    
    # Create story info
    story_info = {
        "title": "User Story",
        "story": user_story,
        "description": "User-provided story"
    }
    
    print(f"\n{'='*60}")
    print(f"Processing User Story: {story_info['title']}")
    print(f"{'='*60}")
    
    # Validate user story
    validation = pipeline.validate_user_story(story_info['story'])
    if validation['errors']:
        print(f"❌ Validation Errors:")
        for error in validation['errors']:
            print(f"  - {error}")
        return
    
    if validation['warnings']:
        print(f"⚠️  Validation Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    if validation['suggestions']:
        print(f"💡 Suggestions:")
        for suggestion in validation['suggestions']:
            print(f"  - {suggestion}")
    
    # Use Prompt Analyzer to intelligently select template
    print(f"\n🔍 Analyzing user story and knowledge base for optimal template selection...")
    from core.prompt_analyzer import PromptAnalyzer
    from core.prompt_loader import PromptTemplateLoader
    
    prompt_analyzer = PromptAnalyzer()
    prompt_loader = PromptTemplateLoader()
    
    # Load knowledge base content for analysis
    try:
        with open("utils/knowledge_base.json", 'r', encoding='utf-8') as f:
            knowledge_base_content = f.read()
    except Exception as e:
        print(f"⚠️ Warning: Could not load knowledge base: {e}")
        knowledge_base_content = "Knowledge base not available"
    
    # Analyze and select optimal template
    selected_template, template_display_name, analysis_details = prompt_analyzer.analyze_and_select_template(
        user_story, knowledge_base_content
    )
    
    # Generate test suite using the selected template
    print(f"\n🔧 Generating test suite using {template_display_name} template...")
    response = pipeline.generate_tests_with_custom_config(
        user_story=story_info['story'],
        codebase_path="../full-stack-fastapi-template/backend/app",
        selected_template=selected_template
    )
    
    if response.success:
        print(f"✅ Test suite generated successfully!")
        print(f"⏱️  Generation time: {response.generation_time:.2f} seconds")
        
        # Display results
        test_suite = response.test_suite
        print(f"\n📋 Template Selection: {test_suite.template_selection}")
        
        print(f"\n🔗 Unit Mapping:")
        for mapping in test_suite.unit_mapping:
            print(f"  - {mapping['story_requirement']} → {mapping['code_unit']}")
        
        print(f"\n🧪 Generated Test Cases ({len(test_suite.test_cases)} total):")
        for i, test_case in enumerate(test_suite.test_cases, 1):
            print(f"\n  {i}. {test_case.test_name}")
            print(f"     Target Unit: {test_case.target_unit}")
            print(f"     Category: {test_case.test_category}")
            print(f"     Mock Requirements: {', '.join(test_case.mock_requirements)}")
        
        # Export test suite
        print(f"\n📁 Exporting test suite...")
        
        # Export as Python
        python_code = pipeline.export_test_suite(response, "python")
        output_file = "generated_tests.py"
        with open(output_file, "w") as f:
            f.write(python_code)
        print(f"  ✅ Python tests saved to: {output_file}")
        
        # Export as Markdown
        markdown_content = pipeline.export_test_suite(response, "markdown")
        output_file = "test_suite.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"  ✅ Markdown report saved to: {output_file}")
        
        # Display coverage analysis
        if test_suite.coverage_analysis:
            print(f"\n📊 Coverage Analysis:")
            print(test_suite.coverage_analysis)
    
    else:
        print(f"❌ Test generation failed: {response.error_message}")
    
    print(f"\n{'='*60}")
    print("🎉 Unit Test Generation Complete!")
    print(f"{'='*60}")
    
    # Summary
    print(f"\n📈 Summary:")
    print(f"  - Processed user story successfully")
    print(f"  - Generated test suite successfully")
    print(f"  - Exported results in multiple formats")
    print(f"\n📁 Generated Files:")
    
    # List generated files
    python_file = "generated_tests.py"
    markdown_file = "test_suite.md"
    if os.path.exists(python_file):
        print(f"  - {python_file}")
    if os.path.exists(markdown_file):
        print(f"  - {markdown_file}")
    
    print(f"\n🚀 Next Steps:")
    print(f"  1. Review generated test cases")
    print(f"  2. Customize test data and assertions")
    print(f"  3. Run tests to verify functionality")
    print(f"  4. Integrate with your CI/CD pipeline")


def demo_mode():
    """Run the system in demo mode with a single user story."""
    print("=== AI-Powered Unit Test Case Generation System - Demo Mode ===")
    
    # Simple demo user story
    demo_story = """User Login Validation
As a user, I want the system to validate my login credentials so that only authorized users can access the application.
- System accepts email and password input
- System validates email format
- System checks password length requirements
- System returns success for valid credentials
- System returns error for invalid credentials"""
    
    # Initialize pipeline
    pipeline = LangChainPipeline()
    
    # Generate test suite
    print("🔧 Generating test suite for demo user story...")
    response = pipeline.generate_tests_for_story(demo_story)
    
    if response.success:
        print("✅ Demo completed successfully!")
        print(f"Generated {len(response.test_suite.test_cases)} test cases")
        
        # Export as Python
        python_code = pipeline.export_test_suite(response, "python")
        with open("demo_tests.py", "w") as f:
            f.write(python_code)
        print("Demo tests saved to: demo_tests.py")
    else:
        print(f"❌ Demo failed: {response.error_message}")


if __name__ == "__main__":
    # Check if demo mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        main()
