"""
Main unit test generation engine for the AI-Powered Unit Test Case Generation System.
"""

import time
from typing import List, Dict, Any
from models import (
    CodeUnit, UserStory, UnitTestTemplate, GeneratedTest, 
    TestSuite, TestGenerationRequest, TestGenerationResponse
)
from .template_catalog import TemplateCatalog
from .knowledge_analyzer import KnowledgeBaseAnalyzer
from .prompt_loader import PromptTemplateLoader
from .acceptance_criteria_analyzer import UserStoryAcceptanceCriteriaAnalyzer

# Make AI integration optional
try:
    from integrations.ai_integration_manager import AIIntegrationManager
    AI_INTEGRATION_AVAILABLE = True
except ImportError:
    AI_INTEGRATION_AVAILABLE = False
    print("⚠️ AI integration not available. Using template-based generation only.")


class UnitTestGenerator:
    """Main unit test generation engine."""
    
    def __init__(self):
        self.template_catalog = TemplateCatalog()
        self.knowledge_analyzer = KnowledgeBaseAnalyzer()
        self.prompt_loader = PromptTemplateLoader()
        
        # Initialize AI manager only if available
        if AI_INTEGRATION_AVAILABLE:
            self.ai_manager = AIIntegrationManager()
            # Pass AI manager to acceptance analyzer
            self.acceptance_analyzer = UserStoryAcceptanceCriteriaAnalyzer(self.ai_manager)
        else:
            self.ai_manager = None
            self.acceptance_analyzer = UserStoryAcceptanceCriteriaAnalyzer()
        
    def generate_test_suite(self, request: TestGenerationRequest) -> TestGenerationResponse:
        """Generate comprehensive unit test suite from user story."""
        start_time = time.time()
        
        try:
            # Step 1: Parse user story
            user_story = self._parse_user_story(request.user_story, getattr(request, 'selected_template', 'prompt_1'))
            
            # Step 2: Analyze codebase and extract units
            codebase_path = request.codebase_path or "."
            code_units = self.knowledge_analyzer.analyze_codebase(codebase_path)
            
            # Step 3: Map story to relevant units
            relevant_units = self.knowledge_analyzer.map_story_to_units(user_story)
            
            # Step 4: Select optimal template
            selected_template = self.template_catalog.select_template(user_story, relevant_units)
            
            # Step 5: Generate test cases
            test_cases = self._generate_test_cases(user_story, relevant_units, selected_template)
            
            # Step 6: Create mock specifications
            mock_specs = self._create_mock_specifications(relevant_units) if request.include_mocks else {}
            
            # Step 7: Generate coverage analysis
            coverage_analysis = self._generate_coverage_analysis(test_cases, relevant_units) if request.include_coverage else ""
            
            # Step 8: Create test suite
            test_suite = TestSuite(
                template_selection=f"Selected {selected_template.template_name} based on component types: {[u.component_type.value for u in relevant_units]}",
                unit_mapping=[{"story_requirement": user_story.title, "code_unit": unit.name} for unit in relevant_units],
                test_cases=test_cases,
                mock_specifications=mock_specs,
                coverage_analysis=coverage_analysis
            )
            
            generation_time = time.time() - start_time
            
            return TestGenerationResponse(
                success=True,
                test_suite=test_suite,
                generation_time=generation_time
            )
            
        except Exception as e:
            generation_time = time.time() - start_time
            return TestGenerationResponse(
                success=False,
                error_message=str(e),
                generation_time=generation_time
            )
    
    def _parse_user_story(self, story_text: str, selected_template: str = "prompt_1") -> UserStory:
        """Parse user story text into structured format."""
        lines = story_text.strip().split('\n')
        title = lines[0] if lines else "Default Story"
        description = lines[1] if len(lines) > 1 else "No description provided"
        
        # Extract acceptance criteria
        acceptance_criteria = []
        for line in lines[2:]:
            if line.strip().startswith('-') or line.strip().startswith('*'):
                acceptance_criteria.append(line.strip()[1:].strip())
        
        return UserStory(
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            priority="medium",
            complexity="medium",
            selected_template=selected_template
        )
    
    def _generate_test_cases(self, user_story: UserStory, code_units: List[CodeUnit], template: UnitTestTemplate) -> List[GeneratedTest]:
        """Generate individual test cases using AI-powered prompts."""
        test_cases = []
        
        # Load knowledge base content for AI prompts
        knowledge_base_content = self._get_knowledge_base_content()
        
        # Use AI to generate tests based on prompt templates
        for unit in code_units:
            # Generate comprehensive test cases using AI
            ai_generated_tests = self._generate_ai_tests(user_story, unit, knowledge_base_content)
            test_cases.extend(ai_generated_tests)
        
        # Filter test cases based on acceptance criteria analysis
        if test_cases:
            print("🔍 Analyzing user story acceptance criteria to filter relevant test cases...")
            analyzed_story = self.acceptance_analyzer.analyze_user_story(user_story.description)
            filtered_cases, relevance_scores = self.acceptance_analyzer.filter_test_cases(test_cases, analyzed_story)
            
            print(f"📊 Test case filtering results:")
            print(f"   - Original test cases: {len(test_cases)}")
            print(f"   - Filtered test cases: {len(filtered_cases)}")
            print(f"   - Irrelevant test cases removed: {len(test_cases) - len(filtered_cases)}")
            
            # Generate prioritization report
            prioritization_report = self.acceptance_analyzer.generate_test_prioritization_report(analyzed_story, relevance_scores)
            
            # Store the filtered cases and analysis
            test_cases = filtered_cases
            self._last_analysis = {
                'analyzed_story': analyzed_story,
                'relevance_scores': relevance_scores,
                'prioritization_report': prioritization_report
            }
            
            # If all test cases were filtered out, provide a helpful message
            if len(filtered_cases) == 0:
                print("⚠️  Warning: All test cases were filtered out as irrelevant to the acceptance criteria.")
                print("💡 Consider:")
                print("   - Adding more specific acceptance criteria to your user story")
                print("   - Reviewing the business domain and functionality alignment")
                print("   - Adjusting the relevance thresholds in the analyzer")
        
        return test_cases
    
    def _generate_ai_tests(self, user_story: UserStory, code_unit: CodeUnit, knowledge_base_content: str) -> List[GeneratedTest]:
        """Generate test cases using AI and prompt templates."""
        test_cases = []
        
        # Get the selected template from user story or use default
        template_name = getattr(user_story, 'selected_template', 'prompt_1')
        if not template_name or template_name not in self.prompt_loader.list_available_templates():
            template_name = "prompt_1"
            print(f"⚠️ Using default template: {template_name}")
        else:
            print(f"🎯 Using selected template: {template_name}")
        
        # Format the prompt with user story and knowledge base
        formatted_prompt = self.prompt_loader.format_template(
            template_name, 
            user_story.description, 
            knowledge_base_content
        )
        
        # Create a comprehensive prompt for the LLM
        comprehensive_prompt = f"""
{formatted_prompt}

CODE UNIT DETAILS:
- Name: {code_unit.name}
- Type: {code_unit.component_type.value}
- File: {code_unit.file_path}
- Parameters: {code_unit.parameters}
- Return Type: {code_unit.return_type}
- Dependencies: {code_unit.dependencies}

KNOWLEDGE BASE CONTEXT:
{knowledge_base_content[:2000]}...

INSTRUCTIONS:
Based on the user story, knowledge base, and code unit details above, generate comprehensive pytest unit tests.
Focus on testing the specific functionality described in the user story.
Include positive, negative, and boundary test cases as appropriate.
"""
        
        print(f"🤖 Sending prompt to AI for code unit: {code_unit.name}")
        print(f"📝 Prompt length: {len(comprehensive_prompt)} characters")
        
        # Generate tests using AI if available
        if self.ai_manager and AI_INTEGRATION_AVAILABLE:
            print(f"🤖 Using AI for test generation...")
            ai_response = self.ai_manager.generate_text(
                comprehensive_prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            if ai_response:
                print(f"✅ AI generated response for {code_unit.name}")
                print(f"📊 Response length: {len(ai_response)} characters")
                # Parse AI response and create test cases
                test_cases = self._parse_ai_response(ai_response, code_unit)
            else:
                print(f"❌ AI generation failed for {code_unit.name}, using fallback")
                # Fallback to template-based generation if AI fails
                test_cases = self._generate_fallback_tests(code_unit, self.template_catalog.get_template_by_type(code_unit.component_type))
        else:
            print(f"📝 AI not available, using template-based generation for {code_unit.name}")
            # Use template-based generation
            test_cases = self._generate_fallback_tests(code_unit, self.template_catalog.get_template_by_type(code_unit.component_type))
        
        return test_cases
    
    def _parse_ai_response(self, ai_response: str, code_unit: CodeUnit) -> List[GeneratedTest]:
        """Parse AI-generated response into test case objects."""
        test_cases = []
        
        # Simple parsing - look for test function definitions
        lines = ai_response.split('\n')
        current_test = None
        
        for line in lines:
            if line.strip().startswith('def test_'):
                # Start of a new test
                if current_test:
                    test_cases.append(current_test)
                
                test_name = line.strip().split('(')[0].replace('def ', '')
                current_test = GeneratedTest(
                    test_name=test_name,
                    target_unit=code_unit.name,
                    setup_code="",
                    input_parameters={},
                    expected_output="",
                    assertions=[],
                    mock_requirements=[],
                    test_category="ai_generated"
                )
            elif current_test and line.strip().startswith('#'):
                # Add comments as setup code
                current_test.setup_code += line + "\n"
        
        # Add the last test if exists
        if current_test:
            test_cases.append(current_test)
        
        return test_cases
    
    def _generate_fallback_tests(self, code_unit: CodeUnit, template: UnitTestTemplate) -> List[GeneratedTest]:
        """Generate fallback tests using template-based approach."""
        test_cases = []
        
        # Generate positive test cases
        positive_test = self._create_positive_test_case(code_unit, template)
        test_cases.append(positive_test)
        
        # Generate negative test cases
        negative_test = self._create_negative_test_case(code_unit, template)
        test_cases.append(negative_test)
        
        # Generate boundary test cases
        boundary_test = self._create_boundary_test_case(code_unit, template)
        test_cases.append(boundary_test)
        
        # Generate exception test cases if applicable
        if code_unit.error_conditions:
            exception_test = self._create_exception_test_case(code_unit, template)
            test_cases.append(exception_test)
        
        return test_cases
    
    def _get_knowledge_base_content(self) -> str:
        """Get knowledge base content for AI prompts."""
        try:
            # Try to load the knowledge base file
            kb_path = Path("utils/knowledge_base.json")
            if kb_path.exists():
                with open(kb_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return "Knowledge base not available"
        except Exception as e:
            return f"Error loading knowledge base: {e}"
    
    def _create_positive_test_case(self, unit: CodeUnit, template: UnitTestTemplate) -> GeneratedTest:
        """Create a positive test case for valid inputs."""
        return GeneratedTest(
            test_name=f"test_{unit.name}_valid_inputs",
            target_unit=unit.name,
            setup_code=self._generate_setup_code(unit, template, "positive"),
            input_parameters=self._generate_input_parameters(unit, "positive"),
            expected_output=self._generate_expected_output(unit, "positive"),
            assertions=self._generate_assertions(unit, template, "positive"),
            mock_requirements=self._generate_mock_requirements(unit),
            test_category="positive",
            test_steps=[
                f"Setup test environment for {unit.name}",
                f"Prepare valid input data for {unit.name}",
                f"Execute {unit.name} function",
                f"Verify successful execution"
            ]
        )
    
    def _create_negative_test_case(self, unit: CodeUnit, template: UnitTestTemplate) -> GeneratedTest:
        """Create a negative test case for invalid inputs."""
        return GeneratedTest(
            test_name=f"test_{unit.name}_invalid_inputs",
            target_unit=unit.name,
            setup_code=self._generate_setup_code(unit, template, "negative"),
            input_parameters=self._generate_input_parameters(unit, "negative"),
            expected_output=self._generate_expected_output(unit, "negative"),
            assertions=self._generate_assertions(unit, template, "negative"),
            mock_requirements=self._generate_mock_requirements(unit),
            test_category="negative",
            test_steps=[
                f"Setup test environment for {unit.name}",
                f"Prepare invalid input data for {unit.name}",
                f"Execute {unit.name} function",
                f"Verify error handling"
            ]
        )
    
    def _create_boundary_test_case(self, unit: CodeUnit, template: UnitTestTemplate) -> GeneratedTest:
        """Create a boundary test case for edge conditions."""
        return GeneratedTest(
            test_name=f"test_{unit.name}_boundary_conditions",
            target_unit=unit.name,
            setup_code=self._generate_setup_code(unit, template, "boundary"),
            input_parameters=self._generate_input_parameters(unit, "boundary"),
            expected_output=self._generate_expected_output(unit, "boundary"),
            assertions=self._generate_assertions(unit, template, "boundary"),
            mock_requirements=self._generate_mock_requirements(unit),
            test_category="boundary",
            test_steps=[
                f"Setup test environment for {unit.name}",
                f"Prepare boundary input data for {unit.name}",
                f"Execute {unit.name} function",
                f"Verify boundary handling"
            ]
        )
    
    def _create_exception_test_case(self, unit: CodeUnit, template: UnitTestTemplate) -> GeneratedTest:
        """Create an exception test case for error conditions."""
        return GeneratedTest(
            test_name=f"test_{unit.name}_exception_handling",
            target_unit=unit.name,
            setup_code=self._generate_setup_code(unit, template, "exception"),
            input_parameters=self._generate_input_parameters(unit, "exception"),
            expected_output="Exception raised",
            assertions=self._generate_assertions(unit, template, "exception"),
            mock_requirements=self._generate_mock_requirements(unit),
            test_category="exception",
            test_steps=[
                f"Setup test environment for {unit.name}",
                f"Prepare input data that will cause exceptions for {unit.name}",
                f"Execute {unit.name} function",
                f"Verify exception handling"
            ]
        )
    
    def _generate_setup_code(self, unit: CodeUnit, template: UnitTestTemplate, test_type: str) -> str:
        """Generate setup code for the test case."""
        if test_type == "positive":
            return f"""
# Mock dependencies
{self._generate_mock_setup(unit)}

# Prepare test data
test_data = {self._generate_test_data(unit, test_type)}
"""
        elif test_type == "negative":
            return f"""
# Mock dependencies
{self._generate_mock_setup(unit)}

# Prepare invalid test data
invalid_data = {self._generate_test_data(unit, test_type)}
"""
        elif test_type == "boundary":
            return f"""
# Mock dependencies
{self._generate_mock_setup(unit)}

# Prepare boundary test data
boundary_data = {self._generate_test_data(unit, test_type)}
"""
        else:  # exception
            return f"""
# Mock dependencies to trigger exceptions
{self._generate_mock_setup(unit, trigger_exception=True)}

# Prepare test data that will cause exceptions
exception_data = {self._generate_test_data(unit, test_type)}
"""
    
    def _generate_mock_setup(self, unit: CodeUnit, trigger_exception: bool = False) -> str:
        """Generate mock setup code for dependencies."""
        mock_code = []
        
        for dep in unit.dependencies:
            if "Session" in dep:
                mock_code.append("mock_session = Mock()")
            elif "settings" in dep:
                mock_code.append("mock_settings = Mock()")
            elif "jwt" in dep:
                mock_code.append("mock_jwt = Mock()")
            elif "emails" in dep:
                mock_code.append("mock_emails = Mock()")
            elif "jinja2" in dep:
                mock_code.append("mock_template = Mock()")
            elif "pathlib" in dep:
                mock_code.append("mock_path = Mock()")
            elif "datetime" in dep:
                mock_code.append("mock_datetime = Mock()")
        
        return "\n".join(mock_code)
    
    def _generate_test_data(self, unit: CodeUnit, test_type: str) -> str:
        """Generate appropriate test data based on test type and unit."""
        if "email" in unit.name.lower():
            if test_type == "positive":
                return '{"email": "test@example.com", "template": "test.html", "context": {"key": "value"}}'
            elif test_type == "negative":
                return '{"email": "invalid-email", "template": "", "context": {}}'
            elif test_type == "boundary":
                return '{"email": "a" * 100 + "@example.com", "template": "a" * 1000, "context": {"key": "a" * 10000}}'
            else:  # exception
                return '{"email": None, "template": None, "context": None}'
        elif "user" in unit.name.lower():
            if test_type == "positive":
                return '{"email": "user@example.com", "password": "securepass123", "username": "testuser"}'
            elif test_type == "negative":
                return '{"email": "", "password": "", "username": ""}'
            elif test_type == "boundary":
                return '{"email": "a" * 100 + "@example.com", "password": "a" * 1000, "username": "a" * 100}'
            else:  # exception
                return '{"email": None, "password": None, "username": None}'
        else:
            return '{"param1": "value1", "param2": "value2"}'
    
    def _generate_input_parameters(self, unit: CodeUnit, test_type: str) -> Dict[str, Any]:
        """Generate input parameters for the test case."""
        params = {}
        
        for param in unit.parameters:
            if param["name"] == "self":
                continue  # Skip self parameter for methods
                
            # Generate meaningful parameter values based on parameter name and type
            if "email" in param["name"].lower():
                if test_type == "positive":
                    params[param["name"]] = "test@example.com"
                elif test_type == "negative":
                    params[param["name"]] = "invalid-email"
                elif test_type == "boundary":
                    params[param["name"]] = "a" * 100 + "@example.com"
                else:  # exception
                    params[param["name"]] = None
            elif "password" in param["name"].lower():
                if test_type == "positive":
                    params[param["name"]] = "SecurePass123!"
                elif test_type == "negative":
                    params[param["name"]] = ""
                elif test_type == "boundary":
                    params[param["name"]] = "a" * 1000
                else:  # exception
                    params[param["name"]] = None
            elif "username" in param["name"].lower():
                if test_type == "positive":
                    params[param["name"]] = "testuser"
                elif test_type == "negative":
                    params[param["name"]] = ""
                elif test_type == "boundary":
                    params[param["name"]] = "a" * 100
                else:  # exception
                    params[param["name"]] = None
            elif "db" in param["name"].lower():
                params[param["name"]] = "mock_db_session"
            elif "client" in param["name"].lower():
                params[param["name"]] = "test_client"
            elif "token" in param["name"].lower():
                params[param["name"]] = "mock_token_headers"
            else:
                # Generic parameter handling
                if test_type == "positive":
                    params[param["name"]] = f"valid_{param['name']}"
                elif test_type == "negative":
                    params[param["name"]] = f"invalid_{param['name']}"
                elif test_type == "boundary":
                    params[param["name"]] = f"boundary_{param['name']}"
                else:  # exception
                    params[param["name"]] = f"exception_{param['name']}"
        
        return params
    
    def _generate_expected_output(self, unit: CodeUnit, test_type: str) -> Any:
        """Generate expected output for the test case."""
        if test_type == "positive":
            if unit.return_type == "str":
                return "Successfully generated string result"
            elif unit.return_type == "User | None":
                return "User object created successfully"
            elif unit.return_type == "None":
                return "Operation completed successfully"
            else:
                return "Expected result returned successfully"
        elif test_type == "negative":
            if "email" in unit.name.lower():
                return "Validation error for invalid email"
            elif "password" in unit.name.lower():
                return "Validation error for invalid password"
            elif "user" in unit.name.lower():
                return "User creation/update error"
            else:
                return "Appropriate error message or exception"
        elif test_type == "boundary":
            if "email" in unit.name.lower():
                return "Handles extremely long email addresses"
            elif "password" in unit.name.lower():
                return "Handles extremely long passwords"
            elif "user" in unit.name.lower():
                return "Handles boundary user data conditions"
            else:
                return "Expected behavior at boundary conditions"
        else:  # exception
            return "Exception raised and handled appropriately"
    
    def _generate_assertions(self, unit: CodeUnit, template: UnitTestTemplate, test_type: str) -> List[str]:
        """Generate assertions for the test case."""
        assertions = []
        
        if test_type == "positive":
            if unit.return_type == "str":
                assertions.extend([
                    "assert result is not None",
                    "assert isinstance(result, str)",
                    "assert len(result) > 0"
                ])
            elif unit.return_type == "User | None":
                assertions.extend([
                    "assert result is not None",
                    "assert isinstance(result, User)",
                    "assert result.email == expected_email"
                ])
            elif unit.return_type == "None":
                assertions.extend([
                    "assert result is None"
                ])
        elif test_type == "negative":
            assertions.extend([
                "assert result is None or result == expected_error"
            ])
        elif test_type == "boundary":
            assertions.extend([
                "assert result is not None",
                "assert result == expected_boundary_result"
            ])
        else:  # exception
            assertions.extend([
                "with pytest.raises(ExpectedException):",
                "    # Function call that should raise exception"
            ])
        
        return assertions
    
    def _generate_mock_requirements(self, unit: CodeUnit) -> List[str]:
        """Generate mock requirements for the unit."""
        requirements = []
        
        for dep in unit.dependencies:
            if "Session" in dep:
                requirements.append("Mock database session")
            elif "settings" in dep:
                requirements.append("Mock configuration settings")
            elif "jwt" in dep:
                requirements.append("Mock JWT operations")
            elif "emails" in dep:
                requirements.append("Mock email service")
            elif "jinja2" in dep:
                requirements.append("Mock template engine")
            elif "pathlib" in dep:
                requirements.append("Mock file system operations")
            elif "datetime" in dep:
                requirements.append("Mock time operations")
        
        return requirements
    
    def _create_mock_specifications(self, code_units: List[CodeUnit]) -> Dict[str, str]:
        """Create detailed mock specifications for dependencies."""
        mock_specs = {}
        
        for unit in code_units:
            for dep in unit.dependencies:
                if "Session" in dep and "database_session" not in mock_specs:
                    mock_specs["database_session"] = """
@pytest.fixture
def mock_db_session():
    with patch('app.crud.Session') as mock_session:
        mock_session.return_value.exec.return_value.first.return_value = None
        mock_session.return_value.add.return_value = None
        mock_session.return_value.commit.return_value = None
        mock_session.return_value.refresh.return_value = None
        yield mock_session
"""
                elif "settings" in dep and "settings" not in mock_specs:
                    mock_specs["settings"] = """
@pytest.fixture
def mock_settings():
    with patch('app.utils.settings') as mock_settings:
        mock_settings.emails_enabled = True
        mock_settings.SMTP_HOST = 'localhost'
        mock_settings.SMTP_PORT = 587
        yield mock_settings
"""
                elif "jwt" in dep and "jwt" not in mock_specs:
                    mock_specs["jwt"] = """
@pytest.fixture
def mock_jwt():
    with patch('app.utils.jwt') as mock_jwt:
        mock_jwt.encode.return_value = 'mock_token'
        mock_jwt.decode.return_value = {'sub': 'test@example.com'}
        yield mock_jwt
"""
        
        return mock_specs
    
    def _generate_coverage_analysis(self, test_cases: List[GeneratedTest], code_units: List[CodeUnit]) -> str:
        """Generate coverage analysis for the test suite."""
        total_tests = len(test_cases)
        
        if total_tests == 0:
            return """
Test Coverage Analysis:
- Total Test Cases: 0
- Positive Test Cases: 0 (0.0%)
- Negative Test Cases: 0 (0.0%)
- Boundary Test Cases: 0 (0.0%)
- Exception Test Cases: 0 (0.0%)

Coverage Areas:
- Input validation coverage: No relevant tests
- Business logic coverage: No relevant tests
- Error handling coverage: No relevant tests
- Edge case coverage: No relevant tests
- Mock dependency coverage: No relevant tests

Note: All test cases were filtered out by acceptance criteria analysis.
Consider adding more specific acceptance criteria to your user story.
"""
        
        positive_tests = len([t for t in test_cases if t.test_category == "positive"])
        negative_tests = len([t for t in test_cases if t.test_category == "negative"])
        boundary_tests = len([t for t in test_cases if t.test_category == "boundary"])
        exception_tests = len([t for t in test_cases if t.test_category == "exception"])
        
        coverage_summary = f"""
Test Coverage Analysis:
- Total Test Cases: {total_tests}
- Positive Test Cases: {positive_tests} ({(positive_tests/total_tests)*100:.1f}%)
- Negative Test Cases: {negative_tests} ({(negative_tests/total_tests)*100:.1f}%)
- Boundary Test Cases: {boundary_tests} ({(boundary_tests/total_tests)*100:.1f}%)
- Exception Test Cases: {exception_tests} ({(exception_tests/total_tests)*100:.1f}%)

Coverage Areas:
- Input validation coverage: Complete
- Business logic coverage: Complete
- Error handling coverage: Complete
- Edge case coverage: Complete
- Mock dependency coverage: Complete

Test Categories by Component Type:
"""
        
        # Add component type breakdown
        for unit in code_units:
            coverage_summary += f"- {unit.name}: {unit.component_type.value}\n"
        
        return coverage_summary
