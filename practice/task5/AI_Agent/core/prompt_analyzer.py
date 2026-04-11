"""
Prompt Analyzer for the AI-Powered Unit Test Case Generation System.
Intelligently analyzes user stories and knowledge bases to select the optimal prompt template.
"""

import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json


class PromptAnalyzer:
    """Intelligently analyzes and selects the optimal prompt template."""
    
    def __init__(self):
        self.template_characteristics = self._initialize_template_characteristics()
    
    def _initialize_template_characteristics(self) -> Dict[str, Dict]:
        """Initialize characteristics of each prompt template."""
        return {
            "prompt_1": {
                "name": "Direct Ask (Simple, Strict)",
                "persona": "Automation Tester Intern",
                "style": "direct",
                "complexity": "simple",
                "focus": ["basic_validation", "standard_testing", "pytest_format"],
                "best_for": [
                    "straightforward functionality",
                    "clear acceptance criteria",
                    "standard unit testing",
                    "beginner testers"
                ],
                "keywords": ["validate", "test", "pytest", "basic", "simple"]
            },
            "prompt_2": {
                "name": "Role Based (QA Engineer Style)",
                "persona": "Senior QA Engineer",
                "style": "professional",
                "complexity": "moderate",
                "focus": ["comprehensive_testing", "business_logic", "robustness"],
                "best_for": [
                    "business-critical functionality",
                    "complex business rules",
                    "comprehensive testing requirements",
                    "experienced QA teams"
                ],
                "keywords": ["business", "robust", "comprehensive", "validation", "functionality"]
            },
            "prompt_3": {
                "name": "Step-by-Step (Process Guided)",
                "persona": "Test Lead (Process-Oriented)",
                "style": "structured",
                "complexity": "high",
                "focus": ["process_following", "structured_workflow", "methodical_testing"],
                "best_for": [
                    "complex workflows",
                    "multi-step processes",
                    "regulated environments",
                    "audit requirements"
                ],
                "keywords": ["process", "workflow", "step", "structured", "methodical"]
            }
        }
    
    def analyze_user_story(self, user_story: str) -> Dict[str, any]:
        """Analyze user story to extract characteristics for template selection."""
        analysis = {
            "complexity_score": 0,
            "style_indicators": [],
            "keywords_found": [],
            "acceptance_criteria_count": 0,
            "business_focus": False,
            "technical_focus": False,
            "process_indicators": 0,
            "recommended_template": "prompt_1"
        }
        
        # Analyze story length and complexity
        lines = user_story.strip().split('\n')
        analysis["acceptance_criteria_count"] = len([line for line in lines if line.strip().startswith('-')])
        
        # Complexity scoring
        if len(user_story) > 500:
            analysis["complexity_score"] += 3
        elif len(user_story) > 300:
            analysis["complexity_score"] += 2
        elif len(user_story) > 100:
            analysis["complexity_score"] += 1
        
        analysis["complexity_score"] += analysis["acceptance_criteria_count"]
        
        # Analyze content for style indicators
        story_lower = user_story.lower()
        
        # Business focus indicators
        business_keywords = ["business", "customer", "user", "stakeholder", "requirement", "feature"]
        if any(keyword in story_lower for keyword in business_keywords):
            analysis["business_focus"] = True
            analysis["complexity_score"] += 1
        
        # Technical focus indicators
        technical_keywords = ["api", "database", "function", "method", "class", "algorithm", "validation"]
        if any(keyword in story_lower for keyword in technical_keywords):
            analysis["technical_focus"] = True
        
        # Process indicators
        process_keywords = ["step", "workflow", "process", "sequence", "order", "flow"]
        analysis["process_indicators"] = sum(1 for keyword in process_keywords if keyword in story_lower)
        analysis["complexity_score"] += analysis["process_indicators"]
        
        # Find specific keywords for template matching
        for template_name, characteristics in self.template_characteristics.items():
            for keyword in characteristics["keywords"]:
                if keyword in story_lower:
                    analysis["keywords_found"].append((template_name, keyword))
        
        return analysis
    
    def analyze_knowledge_base(self, knowledge_base_content: str) -> Dict[str, any]:
        """Analyze knowledge base structure and content."""
        analysis = {
            "total_units": 0,
            "component_types": {},
            "complexity_level": "low",
            "dependencies_count": 0,
            "file_count": 0
        }
        
        try:
            # Try to parse as JSON
            kb_data = json.loads(knowledge_base_content)
            
            # Analyze code units
            if "code_units" in kb_data:
                analysis["total_units"] = len(kb_data["code_units"])
                
                # Analyze component types
                for unit in kb_data["code_units"]:
                    comp_type = unit.get("component_type", "unknown")
                    analysis["component_types"][comp_type] = analysis["component_types"].get(comp_type, 0) + 1
                    
                    # Count dependencies
                    dependencies = unit.get("dependencies", [])
                    analysis["dependencies_count"] += len(dependencies)
            
            # Analyze file structure
            if "file_analysis" in kb_data:
                analysis["file_count"] = len(kb_data["file_analysis"].get("python_files", []))
            
            # Determine complexity level
            if analysis["total_units"] > 100 or analysis["dependencies_count"] > 50:
                analysis["complexity_level"] = "high"
            elif analysis["total_units"] > 50 or analysis["dependencies_count"] > 20:
                analysis["complexity_level"] = "medium"
            
        except (json.JSONDecodeError, KeyError, TypeError):
            # If parsing fails, do basic text analysis
            analysis["total_units"] = knowledge_base_content.count("component_type")
            analysis["complexity_level"] = "unknown"
        
        return analysis
    
    def select_optimal_template(self, user_story_analysis: Dict, knowledge_base_analysis: Dict) -> Tuple[str, str, Dict]:
        """Select the optimal prompt template based on analysis."""
        template_scores = {}
        reasoning = {}
        
        for template_name, characteristics in self.template_characteristics.items():
            score = 0
            reasons = []
            
            # Score based on user story complexity
            if characteristics["complexity"] == "simple" and user_story_analysis["complexity_score"] <= 3:
                score += 3
                reasons.append("Template complexity matches story complexity")
            elif characteristics["complexity"] == "moderate" and 2 <= user_story_analysis["complexity_score"] <= 5:
                score += 3
                reasons.append("Template complexity matches story complexity")
            elif characteristics["complexity"] == "high" and user_story_analysis["complexity_score"] >= 4:
                score += 3
                reasons.append("Template complexity matches story complexity")
            
            # Score based on business vs technical focus
            if characteristics["focus"] and "business_logic" in characteristics["focus"] and user_story_analysis["business_focus"]:
                score += 2
                reasons.append("Template focuses on business logic, matching story focus")
            
            if characteristics["focus"] and "comprehensive_testing" in characteristics["focus"] and user_story_analysis["complexity_score"] >= 3:
                score += 2
                reasons.append("Template provides comprehensive testing for complex stories")
            
            # Score based on process indicators
            if characteristics["style"] == "structured" and user_story_analysis["process_indicators"] >= 2:
                score += 2
                reasons.append("Template provides structured approach for process-heavy stories")
            
            # Score based on knowledge base complexity
            if characteristics["complexity"] == "high" and knowledge_base_analysis["complexity_level"] == "high":
                score += 1
                reasons.append("Template complexity matches knowledge base complexity")
            
            # Score based on keyword matches
            keyword_matches = [item for item in user_story_analysis["keywords_found"] if item[0] == template_name]
            if keyword_matches:
                score += len(keyword_matches)
                reasons.append(f"Found {len(keyword_matches)} keyword matches")
            
            template_scores[template_name] = score
            reasoning[template_name] = reasons
        
        # Select template with highest score
        optimal_template = max(template_scores, key=template_scores.get)
        optimal_score = template_scores[optimal_template]
        
        # If scores are tied, prefer simpler templates
        if optimal_score == 0:
            optimal_template = "prompt_1"  # Default fallback
            reasoning[optimal_template] = ["Default fallback - no clear template preference"]
        
        return optimal_template, optimal_template, {
            "selected_template": optimal_template,
            "template_scores": template_scores,
            "reasoning": reasoning,
            "user_story_analysis": user_story_analysis,
            "knowledge_base_analysis": knowledge_base_analysis
        }
    
    def analyze_and_select_template(self, user_story: str, knowledge_base_content: str) -> Tuple[str, str, Dict]:
        """Complete analysis and template selection process."""
        print("🔍 Analyzing user story and knowledge base for optimal template selection...")
        
        # Analyze user story
        user_story_analysis = self.analyze_user_story(user_story)
        print(f"📊 User Story Analysis:")
        print(f"  - Complexity Score: {user_story_analysis['complexity_score']}")
        print(f"  - Acceptance Criteria: {user_story_analysis['acceptance_criteria_count']}")
        print(f"  - Business Focus: {user_story_analysis['business_focus']}")
        print(f"  - Process Indicators: {user_story_analysis['process_indicators']}")
        
        # Analyze knowledge base
        knowledge_base_analysis = self.analyze_knowledge_base(knowledge_base_content)
        print(f"📊 Knowledge Base Analysis:")
        print(f"  - Total Units: {knowledge_base_analysis['total_units']}")
        print(f"  - Component Types: {knowledge_base_analysis['component_types']}")
        print(f"  - Complexity Level: {knowledge_base_analysis['complexity_level']}")
        
        # Select optimal template
        template_name, template_display_name, selection_details = self.select_optimal_template(
            user_story_analysis, knowledge_base_analysis
        )
        
        print(f"🎯 Template Selection:")
        print(f"  - Selected: {template_display_name}")
        print(f"  - Template: {template_name}")
        print(f"  - Reasoning: {', '.join(selection_details['reasoning'][template_name])}")
        
        return template_name, template_display_name, selection_details
