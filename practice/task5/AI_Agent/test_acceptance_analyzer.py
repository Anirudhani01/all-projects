#!/usr/bin/env python3
"""
Test script for UserStoryAcceptanceCriteriaAnalyzer
Demonstrates how the analyzer filters test cases based on acceptance criteria.
"""

import sys
from pathlib import Path

# Add the AI_Agent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.acceptance_criteria_analyzer import UserStoryAcceptanceCriteriaAnalyzer, TestRelevance


def test_acceptance_criteria_analyzer():
    """Test the acceptance criteria analyzer with a sample user story."""
    
    # Sample user story
    user_story = """
    As a new customer, I want to register for an account on the platform so that I can access personalized features and save my preferences.
    
    Acceptance Criteria:
    - The system must validate email format and ensure it's unique
    - Password must be at least 8 characters with special characters
    - User must provide first name, last name, and email address
    - System must send confirmation email after successful registration
    - Registration form must be intuitive and user-friendly
    """
    
    print("🧪 Testing UserStoryAcceptanceCriteriaAnalyzer")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = UserStoryAcceptanceCriteriaAnalyzer()
    
    # Analyze user story
    print("\n📝 Analyzing user story...")
    analyzed_story = analyzer.analyze_user_story(user_story)
    
    print(f"✅ Business Domain: {analyzed_story.business_domain}")
    print(f"✅ Primary Functionality: {analyzed_story.primary_functionality}")
    print(f"✅ Validation Requirements: {', '.join(analyzed_story.validation_requirements)}")
    print(f"✅ Security Requirements: {', '.join(analyzed_story.security_requirements)}")
    
    print(f"\n📋 Extracted {len(analyzed_story.extracted_criteria)} acceptance criteria:")
    for criterion in analyzed_story.extracted_criteria:
        print(f"   - {criterion.id}: {criterion.description}")
        print(f"     Priority: {criterion.priority}, Test Requirements: {', '.join(criterion.test_requirements)}")
    
    # Simulate test cases
    print("\n🧪 Simulating test case filtering...")
    
    # Mock test cases
    class MockTestCase:
        def __init__(self, name, target_unit, category):
            self.test_name = name
            self.target_unit = target_unit
            self.test_category = category
    
    test_cases = [
        MockTestCase("test_register_user_valid_inputs", "register_user", "positive"),
        MockTestCase("test_validate_email_format", "validate_email", "validation"),
        MockTestCase("test_password_strength", "validate_password", "validation"),
        MockTestCase("test_send_confirmation_email", "send_email", "positive"),
        MockTestCase("test_user_interface_intuitive", "ui_components", "user_experience"),
        MockTestCase("test_unrelated_function", "unrelated_function", "positive"),
        MockTestCase("test_database_connection", "db_connection", "infrastructure"),
    ]
    
    print(f"📊 Original test cases: {len(test_cases)}")
    
    # Filter test cases
    filtered_cases, relevance_scores = analyzer.filter_test_cases(test_cases, analyzed_story)
    
    print(f"📊 Filtered test cases: {len(filtered_cases)}")
    print(f"📊 Irrelevant test cases removed: {len(test_cases) - len(filtered_cases)}")
    
    # Show relevance scores
    print("\n📈 Test case relevance analysis:")
    for test_case in test_cases:
        relevance = relevance_scores[test_case.test_name]
        status = "✅" if relevance != TestRelevance.IRRELEVANT else "❌"
        print(f"   {status} {test_case.test_name}: {relevance.value}")
    
    # Generate prioritization report
    print("\n📋 Generating prioritization report...")
    report = analyzer.generate_test_prioritization_report(analyzed_story, relevance_scores)
    
    # Save report to file
    with open("acceptance_criteria_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ Prioritization report saved to: acceptance_criteria_report.md")
    
    return analyzed_story, filtered_cases, relevance_scores


if __name__ == "__main__":
    try:
        test_acceptance_criteria_analyzer()
        print("\n🎉 Acceptance criteria analyzer test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
