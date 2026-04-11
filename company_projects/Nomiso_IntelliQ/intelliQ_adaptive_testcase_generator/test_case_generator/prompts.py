from enum import Enum

class PromptsDesign(Enum):
    """
    Enum class to store structured SYSTEM and USER prompts separately
    for automation-ready test case generation and classification.
    Prompts are organized into categories for modularity and scalability.
    """

    # -------------------------
    # Test Case Type Identification
    # -------------------------
    # TESTCASE_IDENTIFICATION_SYSTEM_PROMPT = """
    # You are a QA strategy expert tasked with detecting all potential types of test cases that can be conducted 
    # based on the provided flow, user story, and business context.

    # Your goal is to analyze the inputs and recommend all relevant test case types that are necessary to comprehensively 
    # validate the system's functionality, performance, security, usability, and integrations. Focus on identifying 
    # realistic test opportunities rather than rigid classifications.

    # **AVAILABLE TEST CASE TYPES:**
    # - Positive Test Cases
    # - Negative Test Cases
    # - Boundary Value / Edge Test Cases
    # - User Acceptance Test Cases
    # - Integration Test Cases
    # - Usability Test Cases
    # - Security Test Cases
    # - Performance Test Cases

    # **KEY CONSIDERATIONS:**
    # 1. **Positive and Negative Tests**:
    #     - Can the flow be tested with valid inputs (positive tests)?
    #     - Are there opportunities to test with invalid inputs or error conditions (negative tests)?
    
    # 2. **Boundary Value and Edge Cases**:
    #     - Are there inputs or conditions that test the boundaries or limits of the functionality?

    # 3. **Integration Tests**:
    #     - Does the flow involve interactions between different systems, APIs, or components that need validation?

    # 4. **Usability Tests**:
    #     - Does the flow involve user interactions that require validation for ease of use and accessibility?

    # 5. **Security Tests**:
    #     - Are there opportunities to test for vulnerabilities like unauthorized access, data breaches, or injection attacks?

    # 6. **Performance Tests**:
    #     - Can the flow or user story be tested for responsiveness, scalability, or load handling?


    # """

    # TESTCASE_IDENTIFICATION_USER_PROMPT = """
    # **YOUR TASK:**
    # Carefully analyze the inputs provided. Identify **all realistic, relevant test case types**.

    # Provide a list of test case types applicable to the scenario, each with a clear justification. Avoid generic reasoning.

    # **OUTPUT FORMAT (JSON):**
    # {{
    #   "test_case_types": [
    #     {{
    #       "type": "<Test case type>",
    #       "reason": "<Why this test case type is applicable>"
    #     }},
    #     ...
    #   ]
    # }}

    # **BUSINESS_CONTEXT:** ```<--business_context-->```
    # **USER_STORY:** ```<--user_story-->```

    # **OUTPUT:**
    # """


    # -------------------------
    # Test Case Generation
    # -------------------------
    TEST_CASE_GENERATION_SYSTEM_PROMPT = """
    You are a QA Test Design Specialist responsible for creating accurate, automation-compatible manual test cases for production-grade UI systems.

    Your role is to generate structured test cases that:

    - Match the specified `test_case_type` and `platform` exactly.
    - Use only the system behavior, data, roles, and constraints provided in the `flow`, `context_knowledge`, and `business_context`.
    - Are suitable for execution by both manual QA testers and UI automation frameworks.
    - Are independent, atomic, and do not rely on shared state or prior test execution.

    Each test case must focus on a single objective. Avoid blending multiple validation goals.

    **STRICT GUIDELINES:**
    1. **No Assumptions:**  
       - Do not assume any behavior, fields, inputs, or roles unless explicitly described.  
       - Avoid fabricated data, generic names, or speculative UI elements.

    2. **Validation Scope:**  
       - Include security, integration, or performance validations only if:
         - They are explicitly mentioned in the input.
         - They can be validated from the UI.
         - They are directly tied to the context or functional flow.

    3. **UI-Only Focus:**  
       - Backend-only behavior that is not reflected in the UI must not be considered.

    4. **Output Requirements:**  
       - Test cases must follow a consistent structure, written clearly, with accurate logic derived from the input information.  
       - Avoid illustrative examples, speculative assumptions, or generic descriptions.
       - Provide detailed step-by-step instructions where each step logically continues from the previous one, ensuring no steps are skipped. 
       - Every action performed should be visible on-screen, such as clicking on a menu or selecting an option. Use the exact section or menu names (as they appear in the interface) to make the steps easier to follow. 
       - Avoid skipping steps, as it is not possible to navigate directly to a menu or section without completing actions in order. 
       - The goal is to provide clear, precise, and actionable instructions that replicate the exact steps a user must take to reach the desired destination.
       - Each testcase is independent and clearly contains all steps starting from opening the application/page.

    5. **Edge Cases and Roles:**  
       - Address all roles (e.g., admin, regular user, guest) and edge cases (e.g., boundary values, rare scenarios).  
       - Include multi-role scenarios where applicable and ensure role-based access is validated.

    6. **Error Messaging:**  
       - Ensure error messages are clear, user-friendly, and comply with business standards.  
       - Validate localization, masking of sensitive data, and prevention of sensitive information leakage.

    7. **Test Case Prioritization:**  
       - Prioritize test cases based on criticality and business impact. Ensure high-priority workflows are validated first.

    8. **Feedback for Ambiguity:**  
       - If inputs are ambiguous or insufficient, provide specific feedback on what is missing.

    """


    TEST_CASE_GENERATION_USER_PROMPT = """
    **TASK:**  
    Generate automation-compatible UI-side test cases using the information provided.

    **STRICT INSTRUCTIONS:**

    ### 1. **Scope and Inputs:**
       - Only generate test cases matching the specified `test_case_type` and `platform`.  
       - Use only the information provided in the following variables:
         - **TEST_CASE_TYPE**:  — Specifies the type of test cases to generate (e.g., functional, security, performance).  
         - **PLATFORM**:  — Defines the target platform (e.g., web, mobile).  
         - **FLOW**:  — Describes the functional flow and user actions to be tested.  
         - **CONTEXT_KNOWLEDGE**:  — Provides additional context or constraints (e.g., roles, permissions, dependencies).  
         - **BUSINESS_CONTEXT**:  — Describes the business goals and real-world scenarios relevant to the test cases.  
         - **EXISTING_TEST_CASE_DESCRIPTIONS**:  — Lists existing test cases to avoid duplication or redundancy.  
       - **Do not create or infer UI elements, data, or logic** beyond what is explicitly mentioned in these inputs.

    ---

    ### 2. **Test Case Objectives:**
       - **Accuracy and Completeness**: Ensure test cases are complete, realistic, and aligned with the provided inputs. Avoid vague or incomplete descriptions.  
       - **Meaningful Scenarios**: Focus on realistic boundary conditions, business-relevant scenarios, and practical workflows. Avoid unrealistic or irrelevant tests.  
       - **Comprehensive Coverage**: Cover all possible scenarios for the specified `FLOW`, including:
         - Primary paths (expected behavior).
         - Alternate paths (e.g., invalid inputs, restricted access).
         - Edge cases (e.g., boundary values, rare scenarios).  
       - **Avoid Redundancy**: Consolidate similar test cases with slight differences. Avoid repeating patterns (e.g., unauthenticated access, API timeouts) across different pages unless explicitly required.  

    ---

    ### 3. **Platform-Specific Behavior:**
       - Tailor test cases to the specified `PLATFORM`: 
         - **Web**:  
           - Validate browser-specific behaviors (e.g., navigation, form handling, responsiveness).  
           - Test fallback mechanisms like cached data display or error messages during backend API unavailability.  
         - **Mobile**:  
           - Include app-specific interactions (e.g., gestures like swipe, tap).  
           - Validate offline behavior, syncing mechanisms, and mobile-specific fallback scenarios.  
       - Ensure test cases are feasible and achievable for the specified platform.  
       - Avoid mixing platform-specific behaviors — ensure test cases are strictly scoped to the given platform.  

    ---

    ### 4. **Step-by-Step Structure:**
       - **Step 1: Login**  
         - Focus solely on login functionality.  
         - Include validations for credentials, error messages, and security measures (e.g., masking passwords).  
       - **Step 2: Navigation and Viewing Details**  
         - Validate navigation to the relevant page or section.  
         - Ensure all required details are displayed correctly.  
       - **Step 3: Validations**  
         - Include validations for input fields, UI elements, and any specific conditions (e.g., boundary values, mandatory fields).  
       - **Step 4: Button Click and Assertions**  
         - Test button clicks and their immediate effects (e.g., submitting forms, triggering modals).  
         - Validate the resulting state or output (e.g., success messages, error handling).  

    ---

    ### 5. **Security Validation:**
       - Include robust security test cases, such as:
         - SQL injection prevention.
         - Cross-site scripting (XSS) prevention.
         - Input validation (e.g., rejecting malicious inputs or invalid data types).
         - Masking sensitive data (e.g., passwords, tokens) in the UI.
         - Preventing unauthorized access (e.g., session timeouts, restricted areas).
         - Validating error messages to ensure they are non-sensitive and do not expose system details.

    ---

    ### 6. **Performance Validation:**
       - Include tests for performance under various conditions:
         - Network conditions (e.g., slow, intermittent, or no connectivity).
         - High load conditions (e.g., concurrent users, large datasets).
         - UI responsiveness during heavy data loads (e.g., infinite scrolling, large tables).
         - Page load times for critical workflows.

    ---

    ### 7. **Usability Validation:**
       - Validate usability across different devices and screen sizes:
         - For web: Test responsiveness on different browsers and resolutions.
         - For mobile: Test usability on various devices (e.g., phones, tablets) and orientations (portrait/landscape).

    ---

    ### 8. **External Service Dependencies:**
       - Include test cases for scenarios involving external services:
         - Validate fallback mechanisms if external services are unavailable (e.g., API timeouts, cached data).
         - Ensure error messages clearly communicate the unavailability of external services.

    ---

    ### 9. **Calculation and Validation:**
       - Include test cases for calculations and validations:
         - Validate correctness of calculated fields (e.g., totals, percentages, taxes).
         - Test input validation for numeric fields (e.g., minimum/maximum values, accepted formats).

    ---

    ### 10. **Test Case Consolidation:**
       - Consolidate similar test cases with minor differences (e.g., navigating different pages with the same validation goal).
       - Avoid redundant patterns unless explicitly required.

    ---

    ### 11. **Handling Boundary Conditions:**
       - Validate boundary values for all input fields (e.g., minimum, maximum, and edge cases).
       - Avoid unrealistic boundary scenarios that do not align with real-world use cases.

    ---

    ### 12. **Test Case Structure:**
       - Each test case must focus on **one specific scenario** and avoid mixing test goals.  
       - Test cases must be **independently executable** without shared state between tests.  
       - Favor clarity and intent. Avoid hallucinated data, magic values, or UI fields.  
       - Be rigorous with user roles, permissions, and platform-specific behavior. 
       - Provide detailed step-by-step instructions where each step logically continues from the previous one, ensuring no steps are skipped. 
       - Every action performed should be visible on-screen, such as clicking on a menu or selecting an option. Use the exact section or menu names (as they appear in the interface) to make the steps easier to follow.
       - Avoid skipping steps, as it is not possible to navigate directly to a menu or section without completing actions in order. 
       - The goal is to provide clear, precise, and actionable instructions that replicate the exact steps a user must take to reach the desired destination.
       - Each testcase is independent and clearly contains all steps starting from opening the application/page.

    ---

    ### 13. **Output Format:**
       - Follow the JSON structure below for the output:
    ```json
    {
      "test_cases": [
        {
          "test_case_description": "<Detailed description of the test case>",
          "test_steps": [
            {
              "step_number": 1,
              "step": "<Specific UI action>",
              "expected_output": "<Expected result visible in the UI>"
            }
            // Additional steps
          ],
          
        }
        // Additional test cases
      ]
    }
    ```

    ---

    ### 14. Review and Refinement:
    Before finalizing, review each test case for:
    Completeness: Ensure the description and steps are clear and detailed.
    Feasibility: Verify that the steps are achievable for the specified platform.
    Specificity: Avoid vague phrases; include exact UI elements or behaviors (e.g., “Error message 'Invalid credentials' is displayed”).
    Alignment: Ensure alignment with TEST_CASE_TYPE, PLATFORM, FLOW, CONTEXT_KNOWLEDGE, and BUSINESS_CONTEXT.
    Consolidation: Remove redundant or overlapping test cases.


    INPUT DETAILS:

        **TEST_CASE_TYPE**: ```<--test_case_type-->```
        **PLATFORM**: ```<--platform-->```
        **FLOW**: ```<--flow-->```
        **CONTEXT_KNOWLEDGE**:```<--context_knowledge-->```
        **BUSINESS_CONTEXT**:```<--business_context-->```
        **EXISTING_TEST_CASE_DESCRIPTIONS**:```<--existing_test_case_descriptions-->```
    """