import os
import datetime
from pathlib import Path
from user_story_analyser.user_story_analyser import analyse_user_story
from test_case_generator.test_case import generate_test_cases
from acceptance_criteria_checker.acceptance_criteria_checker import check_acceptance_criteria, generate_validation_report, save_validation_results

# --- Helper to create a results folder ---
def create_results_folder(base_folder="test_results"):
    Path(base_folder).mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = Path(base_folder) / f"results_{timestamp}"
    folder_path.mkdir()
    return folder_path

# --- Helper to convert test cases to Markdown table ---
def format_test_cases_markdown(test_cases):
    if not test_cases:
        return "⚠️ No test cases generated."
    
    markdown_content = "# Test Cases Generated\n\n"
    markdown_content += f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Summary
    markdown_content += f"**Total Test Cases:** {len(test_cases)}\n\n"
    
    # Test Cases Table
    markdown_content += "## Test Cases Table\n\n"
    markdown_content += "| **Test Case ID** | **Test Scenario** | **Test Steps** | **Expected Result** | **Type** | **Status** |\n"
    markdown_content += "|---|---|---|---|---|---|\n"
    
    for idx, case in enumerate(test_cases, start=1):
        scenario = case.get("scenario", "N/A")
        steps = case.get("steps", "N/A")
        expected = case.get("expected", "N/A")
        case_type = case.get("type", "N/A")
        status = case.get("status", "Pending")
        
        # Clean and truncate long text for table
        scenario_clean = scenario[:80] + "..." if len(scenario) > 80 else scenario
        steps_clean = steps[:80] + "..." if len(steps) > 80 else steps
        expected_clean = expected[:80] + "..." if len(expected) > 80 else expected
        
        markdown_content += f"| TC{idx:03d} | {scenario_clean} | {steps_clean} | {expected_clean} | {case_type} | {status} |\n"
    
    # Detailed Test Cases
    markdown_content += "\n## Detailed Test Cases\n\n"
    
    for idx, case in enumerate(test_cases, start=1):
        markdown_content += f"### TC{idx:03d}: {case.get('scenario', 'N/A')}\n\n"
        markdown_content += f"**Type:** {case.get('type', 'N/A')}\n\n"
        markdown_content += f"**Status:** {case.get('status', 'Pending')}\n\n"
        markdown_content += f"**Test Steps:**\n{case.get('steps', 'N/A')}\n\n"
        markdown_content += f"**Expected Result:**\n{case.get('expected', 'N/A')}\n\n"
        markdown_content += "---\n\n"
    
    return markdown_content

# --- Main Program ---
if __name__ == "__main__":
    print("🚀 User Story Test Case Generator\n")
    
    # Step 1: Get user story input
    user_story = input("Enter your user story: ").strip()
    
    if not user_story:
        print("❌ User story cannot be empty.")
        exit(1)
    
    # Step 1.5: Get acceptance criteria input
    acceptance_criteria = input("Enter acceptance criteria (or press Enter to skip): ").strip()
    has_acceptance_criteria = bool(acceptance_criteria)
    
    # Step 2: Analyse the user story
    print("\n⏳ Analysing user story...\n")
    try:
        analysis = analyse_user_story(user_story)
        print("✅ User Story Analysis Completed.\n")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        print("⚠ Using fallback analysis (first 2 sentences of user story).")
        analysis = '. '.join(user_story.split('.')[:2]) + '.'
    
    print("🔹 Analysis Output:\n")
    print(analysis)
    print("\n" + "-"*50)
    
    # Step 3: Create results folder
    results_folder = create_results_folder()
    
    # Step 4: Generate test cases
    print("\n⚡ Generating test cases...\n")
    template_path = Path(__file__).parent / "prompts"  # Fixed: use absolute path
    knowledge_base_path = Path(__file__).parent / "knowledge_base" / "knowledge_base.json"  # Fixed: use absolute path
    
    try:
        test_cases = generate_test_cases(user_story, analysis, str(template_path), str(knowledge_base_path))
    except Exception as e:
        print(f"❌ Test case generation failed: {e}")
        test_cases = []

    # Step 5: Validate test cases against acceptance criteria (if provided)
    validation_results = None
    if has_acceptance_criteria and test_cases:
        print("\n🔍 Validating test cases against acceptance criteria...")
        try:
            validation_results = check_acceptance_criteria(test_cases, acceptance_criteria)
            print(f"✅ Validation completed: {validation_results['summary']['satisfaction_rate']} satisfaction rate")
            
            # Add detailed output for unsatisfied test cases
            if validation_results['not_satisfied']:
                print(f"\n❌ UNSATISFIED TEST CASES ({len(validation_results['not_satisfied'])} out of {len(test_cases)}):")
                for i, tc in enumerate(validation_results['not_satisfied'], 1):
                    print(f"   ❌ TC{i}: {tc.get('scenario', 'Unknown')[:60]}...")
                    print(f"      Steps: {tc.get('steps', 'N/A')[:80]}...")
                    print(f"      Expected: {tc.get('expected', 'N/A')[:80]}...")
                    print()
            
            if validation_results['satisfied']:
                print(f"\n✅ SATISFIED TEST CASES ({len(validation_results['satisfied'])} out of {len(test_cases)}):")
                for i, tc in enumerate(validation_results['satisfied'], 1):
                    print(f"   ✅ TC{i}: {tc.get('scenario', 'Unknown')[:60]}...")
            
        except Exception as e:
            print(f"⚠️ Validation failed: {e}")
            validation_results = None
    
    # Step 6: Convert test cases to Markdown
    if test_cases:
        markdown_output = format_test_cases_markdown(test_cases)
    else:
        markdown_output = "⚠️ No test cases generated."

    # Step 7: Save test cases to markdown file
    test_file = results_folder / "test_cases.md"  # Changed to .md
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(f"# User Story Test Cases\n\n")
        f.write(f"**User Story:**\n{user_story}\n\n")
        f.write(f"**Analysis:**\n{analysis}\n\n")
        if has_acceptance_criteria:
            f.write(f"**Acceptance Criteria:**\n{acceptance_criteria}\n\n")
        f.write(markdown_output)
        
        # Add validation report if available
        if validation_results:
            f.write("\n" + "="*80 + "\n\n")
            f.write(generate_validation_report(validation_results, acceptance_criteria))
    
    print(f"\n✅ Test cases saved to: {test_file}")
    
    # Save validation results to JSON if available
    if validation_results:
        save_validation_results(validation_results, results_folder)
    
    print("🎉 Process completed!")
