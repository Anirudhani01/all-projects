import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

class MeasureAccuracyService:
    """
    A service for measuring test case generation accuracy programmatically.
    """
    def __init__(self, llm_client, config):
        """Initialize the accuracy measurement service."""
        self.llm_client = llm_client
        self.config = config
        self.logger = logging.getLogger(__name__)

    def measure_accuracy_programmatically(self, generated_test_cases: List[Dict], validation_results: Dict) -> Dict[str, Any]:
        """
        Programmatically measure accuracy based on test cases and validation results.
        
        Args:
            generated_test_cases (List[Dict]): The generated test cases
            validation_results (Dict): The validation results with review scores
        
        Returns:
            Dict[str, Any]: Accuracy measurement results
        """
        self.logger.info("[ACCURACY] Calculating test case accuracy metrics programmatically...")
        
        # Extract validation data
        validated_test_cases = validation_results.get("validated_test_cases", [])
        
        # Count totals
        total_test_cases = len(generated_test_cases)
        validated_pass = len([tc for tc in validated_test_cases if tc.get("validation_passed", False)])
        validated_fail = total_test_cases - validated_pass
        
        # Calculate accuracy percentage
        accuracy = (validated_pass / total_test_cases * 100) if total_test_cases > 0 else 0.0
        
        # Calculate average scores across all dimensions
        completeness_scores = [tc.get("review_scores", {}).get("completeness", 0.0) for tc in validated_test_cases]
        clarity_scores = [tc.get("review_scores", {}).get("clarity", 0.0) for tc in validated_test_cases]
        logic_scores = [tc.get("review_scores", {}).get("logic", 0.0) for tc in validated_test_cases]
        coverage_scores = [tc.get("review_scores", {}).get("coverage", 0.0) for tc in validated_test_cases]
        
        avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0
        avg_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0.0
        avg_logic = sum(logic_scores) / len(logic_scores) if logic_scores else 0.0
        avg_coverage = sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0.0
        
        # Identify common failure reasons (for failed test cases)
        common_failure_reasons = self._identify_failure_patterns(validated_test_cases)
        
        # Create the evaluation summary
        evaluation_summary = {
            "evaluation_summary": {
                "total_test_cases": total_test_cases,
                "validated_pass": validated_pass,
                "validated_fail": validated_fail,
                "accuracy": f"{accuracy:.1f}%",
                "average_scores": {
                    "completeness": round(avg_completeness, 3),
                    "clarity": round(avg_clarity, 3),
                    "logic": round(avg_logic, 3),
                    "coverage": round(avg_coverage, 3)
                },
                "common_failure_reasons": common_failure_reasons
            }
        }
        
        self.logger.info(f"[ACCURACY] Calculated accuracy: {accuracy:.1f}% ({validated_pass}/{total_test_cases} passed)")
        return evaluation_summary
    
    def _identify_failure_patterns(self, validated_test_cases: List[Dict]) -> List[str]:
        """
        Identify common failure patterns from validation results.
        
        Args:
            validated_test_cases (List[Dict]): Validated test cases with scores
            
        Returns:
            List[str]: Common failure reasons
        """
        failure_reasons = []
        
        # Count low scores in each dimension
        low_completeness_count = len([tc for tc in validated_test_cases 
                                    if tc.get("review_scores", {}).get("completeness", 1.0) < 0.75])
        low_clarity_count = len([tc for tc in validated_test_cases 
                               if tc.get("review_scores", {}).get("clarity", 1.0) < 0.75])
        low_logic_count = len([tc for tc in validated_test_cases 
                             if tc.get("review_scores", {}).get("logic", 1.0) < 0.75])
        low_coverage_count = len([tc for tc in validated_test_cases 
                                if tc.get("review_scores", {}).get("coverage", 1.0) < 0.75])
        
        total_cases = len(validated_test_cases)
        
        # Identify common issues (if more than 20% of cases have the issue)
        threshold = total_cases * 0.2
        
        if low_completeness_count > threshold:
            failure_reasons.append("Incomplete test case specifications")
        if low_clarity_count > threshold:
            failure_reasons.append("Unclear test steps or expected outputs")
        if low_logic_count > threshold:
            failure_reasons.append("Illogical test flow or inconsistent steps")
        if low_coverage_count > threshold:
            failure_reasons.append("Insufficient coverage of edge cases or scenarios")
        
        # If no specific patterns, provide generic reason
        if not failure_reasons:
            failed_count = len([tc for tc in validated_test_cases if not tc.get("validation_passed", True)])
            if failed_count > 0:
                failure_reasons.append("Minor quality improvements needed")
            else:
                failure_reasons.append("No significant issues identified")
        
        return failure_reasons

    def measure_accuracy(self, story: Dict[str, Any], rag_chunks: str) -> str:
        """
        Legacy method - kept for compatibility.
        """
        return json.dumps({"message": "Use measure_accuracy_programmatically method instead"})
    
    def measure_accuracy_with_data(self, generated_test_cases: str, validation_results: str, rag_chunks: str) -> Dict[str, Any]:
        """
        Legacy method - now uses programmatic calculation.
        """
        try:
            # Parse JSON strings
            if isinstance(generated_test_cases, str):
                generated_data = json.loads(generated_test_cases)
            else:
                generated_data = generated_test_cases
                
            if isinstance(validation_results, str):
                validation_data = json.loads(validation_results)
            else:
                validation_data = validation_results
            
            # Use programmatic method
            return self.measure_accuracy_programmatically(generated_data, validation_data)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"[ACCURACY] Error parsing JSON: {e}")
            return {"error": "Invalid JSON format in input data"}
    
    def accuracy_measure_with_text(self, structured_text: str, rag_chunks: str, test_cases: Any) -> Dict[str, Any]:
        """
        Legacy method - kept for compatibility.
        """
        return json.dumps({"message": "Use measure_accuracy_programmatically method instead"})
    