"""
User Story Acceptance Criteria Analyzer
Uses AI integration to analyze user stories and filter test cases based on acceptance criteria alignment.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TestRelevance(Enum):
    """Test case relevance levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    IRRELEVANT = "irrelevant"


@dataclass
class AcceptanceCriterion:
    """Represents a single acceptance criterion."""
    id: str
    description: str
    priority: int
    test_requirements: List[str]


@dataclass
class AnalyzedUserStory:
    """Analyzed user story with extracted acceptance criteria."""
    original_story: str
    extracted_criteria: List[AcceptanceCriterion]
    business_domain: str
    primary_functionality: str
    validation_requirements: List[str]
    security_requirements: List[str]
    test_priorities: Dict[str, int]


class UserStoryAcceptanceCriteriaAnalyzer:
    """Analyzes user stories using AI integration and filters test cases based on acceptance criteria."""
    
    def __init__(self, ai_integration_manager=None):
        self.ai_manager = ai_integration_manager
    
    def analyze_user_story(self, user_story: str) -> AnalyzedUserStory:
        """Analyze a user story using AI integration to extract acceptance criteria."""
        if not self.ai_manager:
            # Fallback to basic analysis if AI is not available
            return self._basic_analysis(user_story)
        
        try:
            # Use AI to analyze the user story
            analysis_prompt = self._create_analysis_prompt(user_story)
            ai_response = self.ai_manager.generate_text(analysis_prompt, max_tokens=1000, temperature=0.3)
            
            if ai_response:
                return self._parse_ai_analysis(user_story, ai_response)
            else:
                return self._basic_analysis(user_story)
                
        except Exception as e:
            print(f"AI analysis failed: {e}, using basic analysis")
            return self._basic_analysis(user_story)
    
    def _create_analysis_prompt(self, user_story: str) -> str:
        """Create a prompt for AI analysis of the user story."""
        return f"""
Analyze the following user story and extract acceptance criteria, business domain, and test requirements.

User Story:
{user_story}

Please provide a structured analysis in the following format:

ACCEPTANCE_CRITERIA:
- AC001: [Description] | Priority: [1-3] | Test Requirements: [comma-separated list]
- AC002: [Description] | Priority: [1-3] | Test Requirements: [comma-separated list]

BUSINESS_DOMAIN: [domain]
PRIMARY_FUNCTIONALITY: [functionality]
VALIDATION_REQUIREMENTS: [comma-separated list]
SECURITY_REQUIREMENTS: [comma-separated list]

Focus on:
1. Functional requirements
2. Validation needs
3. Security considerations
4. Business rules
5. User experience requirements

Provide only the structured output above, no additional text.
"""
    
    def _parse_ai_analysis(self, user_story: str, ai_response: str) -> AnalyzedUserStory:
        """Parse the AI response to extract structured analysis."""
        try:
            lines = ai_response.strip().split('\n')
            criteria = []
            business_domain = "general"
            primary_functionality = "general_functionality"
            validation_requirements = []
            security_requirements = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("ACCEPTANCE_CRITERIA:"):
                    current_section = "criteria"
                elif line.startswith("BUSINESS_DOMAIN:"):
                    current_section = "domain"
                    business_domain = line.split(":", 1)[1].strip()
                elif line.startswith("PRIMARY_FUNCTIONALITY:"):
                    current_section = "functionality"
                    primary_functionality = line.split(":", 1)[1].strip()
                elif line.startswith("VALIDATION_REQUIREMENTS:"):
                    current_section = "validation"
                    reqs = line.split(":", 1)[1].strip()
                    validation_requirements = [r.strip() for r in reqs.split(",") if r.strip()]
                elif line.startswith("SECURITY_REQUIREMENTS:"):
                    current_section = "security"
                    reqs = line.split(":", 1)[1].strip()
                    security_requirements = [r.strip() for r in reqs.split(",") if r.strip()]
                elif current_section == "criteria" and line.startswith("- AC"):
                    # Parse acceptance criterion
                    criterion = self._parse_criterion_line(line)
                    if criterion:
                        criteria.append(criterion)
            
            # Determine test priorities
            test_priorities = {c.id: c.priority for c in criteria}
            
            return AnalyzedUserStory(
                original_story=user_story,
                extracted_criteria=criteria,
                business_domain=business_domain,
                primary_functionality=primary_functionality,
                validation_requirements=validation_requirements,
                security_requirements=security_requirements,
                test_priorities=test_priorities
            )
            
        except Exception as e:
            print(f"Failed to parse AI analysis: {e}")
            return self._basic_analysis(user_story)
    
    def _parse_criterion_line(self, line: str) -> Optional[AcceptanceCriterion]:
        """Parse a single acceptance criterion line."""
        try:
            # Expected format: - AC001: [Description] | Priority: [1-3] | Test Requirements: [list]
            parts = line.split("|")
            if len(parts) >= 3:
                # Extract ID and description
                id_desc = parts[0].split(":", 1)
                criterion_id = id_desc[0].replace("- ", "").strip()
                description = id_desc[1].strip()
                
                # Extract priority
                priority_part = parts[1].strip()
                priority = int(priority_part.split(":")[1].strip())
                
                # Extract test requirements
                reqs_part = parts[2].strip()
                test_requirements = [r.strip() for r in reqs_part.split(":")[1].strip().split(",") if r.strip()]
                
                return AcceptanceCriterion(
                    id=criterion_id,
                    description=description,
                    priority=priority,
                    test_requirements=test_requirements
                )
        except Exception as e:
            print(f"Failed to parse criterion line '{line}': {e}")
        
        return None
    
    def _basic_analysis(self, user_story: str) -> AnalyzedUserStory:
        """Fallback basic analysis when AI is not available."""
        # Simple keyword-based analysis
        story_lower = user_story.lower()
        
        # Basic acceptance criteria extraction
        criteria = []
        lines = user_story.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                description = line.lstrip('-•* ').strip()
                if description:
                    criteria.append(AcceptanceCriterion(
                        id=f"AC{i+1:03d}",
                        description=description,
                        priority=2,  # Default priority
                        test_requirements=["functional_testing"]
                    ))
        
        # Basic domain identification
        business_domain = "general"
        if any(word in story_lower for word in ["user", "account", "register", "login"]):
            business_domain = "user_management"
        elif any(word in story_lower for word in ["product", "order", "cart", "payment"]):
            business_domain = "ecommerce"
        
        # Basic functionality identification
        primary_functionality = "general_functionality"
        if any(word in story_lower for word in ["register", "sign up", "create account"]):
            primary_functionality = "user_registration"
        elif any(word in story_lower for word in ["login", "sign in", "authenticate"]):
            primary_functionality = "user_authentication"
        
        # Basic requirements extraction
        validation_requirements = []
        if any(word in story_lower for word in ["email", "password", "validate", "required"]):
            validation_requirements.append("input_validation")
        
        security_requirements = []
        if any(word in story_lower for word in ["secure", "password", "authentication"]):
            security_requirements.append("user_authentication")
        
        test_priorities = {c.id: c.priority for c in criteria}
        
        return AnalyzedUserStory(
            original_story=user_story,
            extracted_criteria=criteria,
            business_domain=business_domain,
            primary_functionality=primary_functionality,
            validation_requirements=validation_requirements,
            security_requirements=security_requirements,
            test_priorities=test_priorities
        )
    
    def filter_test_cases(self, test_cases: List, analyzed_story: AnalyzedUserStory) -> Tuple[List, Dict[str, TestRelevance]]:
        """Filter test cases based on acceptance criteria analysis."""
        filtered_cases = []
        relevance_scores = {}
        
        for test_case in test_cases:
            relevance = self._calculate_test_relevance(test_case, analyzed_story)
            test_name = getattr(test_case, 'test_name', str(test_case))
            relevance_scores[test_name] = relevance
            
            if relevance != TestRelevance.IRRELEVANT:
                filtered_cases.append(test_case)
        
        return filtered_cases, relevance_scores
    
    def _calculate_test_relevance(self, test_case, analyzed_story: AnalyzedUserStory) -> TestRelevance:
        """Calculate the relevance of a test case to the acceptance criteria."""
        # Extract test case information
        test_name = getattr(test_case, 'test_name', str(test_case)).lower()
        target_unit = getattr(test_case, 'target_unit', '').lower()
        test_category = getattr(test_case, 'test_category', '').lower()
        
        relevance_score = 0
        
        # Check alignment with primary functionality
        if self._check_functionality_alignment(target_unit, analyzed_story.primary_functionality):
            relevance_score += 3
        
        # Check alignment with validation requirements
        if self._check_validation_alignment(test_category, analyzed_story.validation_requirements):
            relevance_score += 2
        
        # Check alignment with security requirements
        if self._check_security_alignment(test_category, analyzed_story.security_requirements):
            relevance_score += 2
        
        # Check alignment with acceptance criteria keywords
        for criterion in analyzed_story.extracted_criteria:
            if criterion.priority == 1:  # High priority criteria
                if any(keyword in test_name for keyword in criterion.description.lower().split()):
                    relevance_score += 2
        
        # Additional scoring for general user management functions
        if analyzed_story.business_domain == "user_management":
            if any(word in target_unit for word in ["user", "account", "register", "login", "auth"]):
                relevance_score += 1
        
        # Additional scoring for general business logic functions
        if analyzed_story.primary_functionality in ["user_registration", "user_authentication"]:
            if any(word in target_unit for word in ["create", "update", "delete", "get", "read"]):
                relevance_score += 1
        
        # Determine relevance level (more lenient thresholds)
        if relevance_score >= 4:
            return TestRelevance.HIGH
        elif relevance_score >= 2:
            return TestRelevance.MEDIUM
        elif relevance_score >= 0:  # Changed from 1 to 0 to be more lenient
            return TestRelevance.LOW
        else:
            return TestRelevance.IRRELEVANT
    
    def _check_functionality_alignment(self, target_unit: str, primary_functionality: str) -> bool:
        """Check if test case aligns with primary functionality."""
        if not target_unit or not primary_functionality:
            return False
        
        functionality_keywords = {
            "user_registration": ["register", "create", "signup", "account"],
            "user_authentication": ["login", "auth", "signin", "authenticate"],
            "data_creation": ["create", "add", "insert", "new"],
            "data_retrieval": ["read", "get", "view", "show", "display"],
            "data_modification": ["update", "modify", "edit", "change"],
            "data_deletion": ["delete", "remove", "eliminate"],
            "data_search": ["search", "find", "locate", "query"]
        }
        
        if primary_functionality in functionality_keywords:
            keywords = functionality_keywords[primary_functionality]
            return any(keyword in target_unit for keyword in keywords)
        
        return False
    
    def _check_validation_alignment(self, test_category: str, validation_requirements: List[str]) -> bool:
        """Check if test case aligns with validation requirements."""
        if not test_category or not validation_requirements:
            return False
        
        validation_categories = ["negative", "boundary", "validation"]
        return test_category in validation_categories
    
    def _check_security_alignment(self, test_category: str, security_requirements: List[str]) -> bool:
        """Check if test case aligns with security requirements."""
        if not test_category or not security_requirements:
            return False
        
        security_categories = ["negative", "security", "authentication", "authorization"]
        return test_category in security_categories
    
    def generate_test_prioritization_report(self, analyzed_story: AnalyzedUserStory, relevance_scores: Dict[str, TestRelevance]) -> str:
        """Generate a report on test case prioritization."""
        report = "# Test Case Prioritization Report\n\n"
        
        report += "## User Story Analysis\n\n"
        report += f"**Business Domain:** {analyzed_story.business_domain}\n"
        report += f"**Primary Functionality:** {analyzed_story.primary_functionality}\n\n"
        
        report += "## Acceptance Criteria\n\n"
        for criterion in analyzed_story.extracted_criteria:
            report += f"### {criterion.id}: {criterion.description}\n"
            report += f"- **Priority:** {criterion.priority}\n"
            report += f"- **Test Requirements:** {', '.join(criterion.test_requirements)}\n\n"
        
        report += "## Test Case Relevance Summary\n\n"
        relevance_counts = {}
        for relevance in TestRelevance:
            relevance_counts[relevance.value] = sum(1 for score in relevance_scores.values() if score == relevance)
        
        for relevance, count in relevance_counts.items():
            report += f"- **{relevance.title()} Relevance:** {count} test cases\n"
        
        return report
