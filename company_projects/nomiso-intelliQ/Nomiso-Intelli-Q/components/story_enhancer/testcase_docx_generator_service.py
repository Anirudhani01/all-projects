import json
import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime


class TestCaseDocxGeneratorService:
    """
    Service for generating DOCX documents from test case JSON files.
    Creates formatted Word documents with test cases in table format.
    """
    
    def __init__(self, config=None):
        """Initialize the DOCX generator service."""
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_testcase_docx(self, test_cases: List[Dict[str, Any]], output_dir: str, base_name: str = "test_cases") -> bool:
        """
        Generate a single DOCX file containing all test cases.
        
        Args:
            test_cases (List[Dict[str, Any]]): List of test case dictionaries
            output_dir (str): Directory where to save the DOCX file
            base_name (str): Base name for the output file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"[TESTCASE_DOCX] Generating single DOCX for {len(test_cases)} test cases...")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate a single document containing all test cases
            self._create_consolidated_testcase_docx(test_cases, output_dir, base_name)
            
            self.logger.info(f"[TESTCASE_DOCX] Successfully generated consolidated DOCX file in: {output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"[TESTCASE_DOCX] Error generating DOCX file: {str(e)}")
            import traceback
            self.logger.error(f"[TESTCASE_DOCX] Full traceback: {traceback.format_exc()}")
            return False
    
    def _create_consolidated_testcase_docx(self, test_cases: List[Dict[str, Any]], output_dir: str, base_name: str) -> None:
        """
        Create a single DOCX file containing all test cases.
        
        Args:
            test_cases (List[Dict[str, Any]]): List of test case data
            output_dir (str): Output directory
            base_name (str): Base name for the file
        """
        doc = Document()
        
        # Add document title
        doc.add_heading("Test Cases Document", level=0)
        doc.add_paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.add_paragraph(f"Total Test Cases: {len(test_cases)}")
        doc.add_page_break()
        
        # Use the helper method to add test cases
        self._add_testcases_to_document(doc, test_cases, show_status=False)

        # Save the consolidated file
        filename = os.path.join(output_dir, f"{base_name}.docx")
        doc.save(filename)
        self.logger.info(f"[TESTCASE_DOCX] Saved consolidated test cases to: {filename}")
    
    def _create_single_testcase_docx(self, test_case: Dict[str, Any], index: int, output_dir: str, base_name: str) -> None:
        """
        Create a separate DOCX file for a single test case following the provided structure.
        (Kept for backward compatibility)
        
        Args:
            test_case (Dict[str, Any]): Test case data
            index (int): Test case index
            output_dir (str): Output directory
            base_name (str): Base name for the file
        """
        doc = Document()
        doc.add_heading(f"Test Case {index + 1}", level=1)

        doc.add_paragraph(f"Type: {test_case.get('test_case_type', 'N/A')}")
        doc.add_paragraph(f"Description: {test_case.get('test_case_description', 'N/A')}")

        doc.add_heading("Test Steps", level=2)
        steps = test_case.get("test_steps", [])
        
        # Create a table with headers
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Step No.'
        hdr_cells[1].text = 'Step'
        hdr_cells[2].text = 'Expected Output'

        # Populate the table with test steps
        for step in steps:
            row_cells = table.add_row().cells
            row_cells[0].text = str(step.get('step_number', ''))
            row_cells[1].text = step.get('step', '')
            row_cells[2].text = step.get('expected_output', '')

        # Save the file
        filename = os.path.join(output_dir, f"{base_name}_{index + 1}.docx")
        doc.save(filename)
    
    def generate_separate_testcase_docx(self, test_cases: List[Dict[str, Any]], output_dir: str, base_name: str = "test_case") -> bool:
        """
        Generate separate DOCX files for each test case (alternative method).
        
        Args:
            test_cases (List[Dict[str, Any]]): List of test case dictionaries
            output_dir (str): Directory where to save the DOCX files
            base_name (str): Base name for the output files
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"[TESTCASE_DOCX] Generating separate DOCX files for {len(test_cases)} test cases...")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate a separate document for each test case
            for i, test_case in enumerate(test_cases):
                self._create_single_testcase_docx(test_case, i, output_dir, base_name)
            
            self.logger.info(f"[TESTCASE_DOCX] Successfully generated {len(test_cases)} separate DOCX files in: {output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"[TESTCASE_DOCX] Error generating separate DOCX files: {str(e)}")
            import traceback
            self.logger.error(f"[TESTCASE_DOCX] Full traceback: {traceback.format_exc()}")
            return False
    
    def generate_from_json_file(self, json_file_path: str, output_dir: str, base_name: str) -> bool:
        """
        Generate DOCX files from a JSON test cases file.
        
        Args:
            json_file_path (str): Path to the JSON file containing test cases
            output_dir (str): Output directory for the DOCX files
            base_name (str): Base name for the output files
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load test cases from JSON file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                test_cases = data
            elif isinstance(data, dict):
                test_cases = data.get("test_cases", data.get("generated_test_cases", []))
                # Handle updated test cases format
                if not test_cases and "updated_test_cases" in data:
                    test_cases = data["updated_test_cases"]
                if not test_cases:
                    # If it's a validation result, extract test cases
                    if "validated_test_cases" in data:
                        test_cases = data["validated_test_cases"]
            else:
                self.logger.error("[TESTCASE_DOCX] Invalid JSON structure in test cases file")
                return False
            
            if not test_cases:
                self.logger.warning("[TESTCASE_DOCX] No test cases found in JSON file")
                return False
            
            # Generate the DOCX files
            success = self.generate_testcase_docx(test_cases, output_dir, base_name)
            
            if success:
                self.logger.info(f"[TESTCASE_DOCX] Consolidated test cases DOCX file generated in: {output_dir}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"[TESTCASE_DOCX] Error generating DOCX from JSON file: {str(e)}")
            return False
    
    def generate_validation_docx(self, validation_results: Dict[str, Any], output_dir: str, base_name: str = "validation_results") -> bool:
        """
        Generate DOCX file from validation results JSON.
        
        Args:
            validation_results (Dict[str, Any]): Validation results data
            output_dir (str): Output directory for the DOCX file
            base_name (str): Base name for the output file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"[TESTCASE_DOCX] Generating validation results DOCX...")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            doc = Document()
            
            # Add document title
            doc.add_heading("Test Case Validation Results", level=0)
            doc.add_paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Summary section
            doc.add_heading("Validation Summary", level=1)
            total_cases = validation_results.get('total_test_cases', 0)
            passed_cases = validation_results.get('passed_test_cases', 0)
            failed_cases = validation_results.get('failed_test_cases', 0)
            success_rate = validation_results.get('success_rate', 0)
            
            summary_table = doc.add_table(rows=4, cols=2)
            summary_table.style = 'Table Grid'
            summary_table.rows[0].cells[0].text = "Total Test Cases"
            summary_table.rows[0].cells[1].text = str(total_cases)
            summary_table.rows[1].cells[0].text = "Passed Test Cases"
            summary_table.rows[1].cells[1].text = str(passed_cases)
            summary_table.rows[2].cells[0].text = "Failed Test Cases"
            summary_table.rows[2].cells[1].text = str(failed_cases)
            summary_table.rows[3].cells[0].text = "Success Rate"
            summary_table.rows[3].cells[1].text = f"{success_rate}%"
            
            # Failed test cases section
            if failed_cases > 0:
                doc.add_heading("Failed Test Cases", level=1)
                failed_test_cases = validation_results.get('failed_test_case_details', [])
                
                if failed_test_cases:
                    failed_table = doc.add_table(rows=1, cols=4)
                    failed_table.style = 'Table Grid'
                    failed_hdr = failed_table.rows[0].cells
                    failed_hdr[0].text = 'Test Case ID'
                    failed_hdr[1].text = 'Type'
                    failed_hdr[2].text = 'Description'
                    failed_hdr[3].text = 'Failure Reason'
                    
                    for failed_case in failed_test_cases:
                        row_cells = failed_table.add_row().cells
                        row_cells[0].text = failed_case.get('test_case_id', 'N/A')
                        row_cells[1].text = failed_case.get('test_case_type', 'N/A')
                        row_cells[2].text = failed_case.get('test_case_description', 'N/A')[:100] + "..." if len(failed_case.get('test_case_description', '')) > 100 else failed_case.get('test_case_description', 'N/A')
                        row_cells[3].text = failed_case.get('failure_reason', 'N/A')
            
            # Passed test cases section
            if passed_cases > 0:
                doc.add_heading("Passed Test Cases", level=1)
                passed_test_cases = validation_results.get('passed_test_case_details', [])
                
                if passed_test_cases:
                    passed_table = doc.add_table(rows=1, cols=3)
                    passed_table.style = 'Table Grid'
                    passed_hdr = passed_table.rows[0].cells
                    passed_hdr[0].text = 'Test Case ID'
                    passed_hdr[1].text = 'Type'
                    passed_hdr[2].text = 'Description'
                    
                    for passed_case in passed_test_cases:
                        row_cells = passed_table.add_row().cells
                        row_cells[0].text = passed_case.get('test_case_id', 'N/A')
                        row_cells[1].text = passed_case.get('test_case_type', 'N/A')
                        row_cells[2].text = passed_case.get('test_case_description', 'N/A')[:100] + "..." if len(passed_case.get('test_case_description', '')) > 100 else passed_case.get('test_case_description', 'N/A')
            
            # Save the file
            filename = os.path.join(output_dir, f"{base_name}.docx")
            doc.save(filename)
            self.logger.info(f"[TESTCASE_DOCX] Saved validation results to: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"[TESTCASE_DOCX] Error generating validation DOCX: {str(e)}")
            import traceback
            self.logger.error(f"[TESTCASE_DOCX] Full traceback: {traceback.format_exc()}")
            return False
    
    def generate_accuracy_measure_docx(self, accuracy_data: Dict[str, Any], output_dir: str, base_name: str = "accuracy_results") -> bool:
        """
        Generate DOCX file from accuracy measurement results.
        
        Args:
            accuracy_data (Dict[str, Any]): Accuracy measurement data
            output_dir (str): Output directory for the DOCX file
            base_name (str): Base name for the output file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"[TESTCASE_DOCX] Generating accuracy measurement DOCX...")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            doc = Document()
            
            # Add document title
            doc.add_heading("Test Case Accuracy Measurement", level=0)
            doc.add_paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Overall accuracy section
            doc.add_heading("Overall Accuracy Metrics", level=1)
            overall_accuracy = accuracy_data.get('overall_accuracy', 0)
            total_evaluated = accuracy_data.get('total_test_cases_evaluated', 0)
            
            accuracy_table = doc.add_table(rows=2, cols=2)
            accuracy_table.style = 'Table Grid'
            accuracy_table.rows[0].cells[0].text = "Overall Accuracy Score"
            accuracy_table.rows[0].cells[1].text = f"{overall_accuracy}%"
            accuracy_table.rows[1].cells[0].text = "Total Test Cases Evaluated"
            accuracy_table.rows[1].cells[1].text = str(total_evaluated)
            
            # Accuracy by test case type
            type_accuracy = accuracy_data.get('accuracy_by_type', {})
            if type_accuracy:
                doc.add_heading("Accuracy by Test Case Type", level=1)
                type_table = doc.add_table(rows=1, cols=2)
                type_table.style = 'Table Grid'
                type_hdr = type_table.rows[0].cells
                type_hdr[0].text = 'Test Case Type'
                type_hdr[1].text = 'Accuracy Score'
                
                for test_type, score in type_accuracy.items():
                    row_cells = type_table.add_row().cells
                    row_cells[0].text = test_type
                    row_cells[1].text = f"{score}%"
            
            # Individual test case accuracy
            individual_scores = accuracy_data.get('individual_test_case_scores', [])
            if individual_scores:
                doc.add_heading("Individual Test Case Scores", level=1)
                individual_table = doc.add_table(rows=1, cols=4)
                individual_table.style = 'Table Grid'
                individual_hdr = individual_table.rows[0].cells
                individual_hdr[0].text = 'Test Case ID'
                individual_hdr[1].text = 'Type'
                individual_hdr[2].text = 'Accuracy Score'
                individual_hdr[3].text = 'Comments'
                
                for score_data in individual_scores:
                    row_cells = individual_table.add_row().cells
                    row_cells[0].text = score_data.get('test_case_id', 'N/A')
                    row_cells[1].text = score_data.get('test_case_type', 'N/A')
                    row_cells[2].text = f"{score_data.get('accuracy_score', 0)}%"
                    row_cells[3].text = score_data.get('comments', 'N/A')
            
            # Save the file
            filename = os.path.join(output_dir, f"{base_name}.docx")
            doc.save(filename)
            self.logger.info(f"[TESTCASE_DOCX] Saved accuracy results to: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"[TESTCASE_DOCX] Error generating accuracy DOCX: {str(e)}")
            import traceback
            self.logger.error(f"[TESTCASE_DOCX] Full traceback: {traceback.format_exc()}")
            return False
    
    def replace_failed_with_regenerated_testcases(self, original_test_cases: List[Dict[str, Any]], 
                                                 failed_test_case_ids: List[str], 
                                                 regenerated_test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Replace failed test cases with regenerated ones.
        
        Args:
            original_test_cases (List[Dict[str, Any]]): Original test cases
            failed_test_case_ids (List[str]): List of failed test case IDs
            regenerated_test_cases (List[Dict[str, Any]]): Regenerated test cases
            
        Returns:
            List[Dict[str, Any]]: Updated test cases with failed ones replaced
        """
        self.logger.info(f"[TESTCASE_DOCX] Replacing {len(failed_test_case_ids)} failed test cases with regenerated ones")
        
        # Create a mapping of regenerated test cases by their original ID
        regenerated_mapping = {}
        for regen_case in regenerated_test_cases:
            original_id = regen_case.get('original_test_case_id') or regen_case.get('test_case_id')
            if original_id:
                regenerated_mapping[original_id] = regen_case
        
        # Replace failed test cases
        updated_test_cases = []
        for test_case in original_test_cases:
            test_case_id = test_case.get('test_case_id')
            if test_case_id in failed_test_case_ids and test_case_id in regenerated_mapping:
                # Replace with regenerated test case
                regenerated_case = regenerated_mapping[test_case_id].copy()
                regenerated_case['status'] = 'regenerated'
                regenerated_case['regeneration_reason'] = 'Replaced failed test case'
                updated_test_cases.append(regenerated_case)
                self.logger.info(f"[TESTCASE_DOCX] Replaced failed test case {test_case_id} with regenerated version")
            else:
                # Keep original test case
                updated_test_cases.append(test_case)
        
        return updated_test_cases
    
    def generate_iteration_docx(self, test_cases: List[Dict[str, Any]], iteration_number: int, 
                              output_dir: str, base_name: str = "test_cases_iteration") -> bool:
        """
        Generate DOCX file for a specific iteration with tracking of changes.
        
        Args:
            test_cases (List[Dict[str, Any]]): Test cases for this iteration
            iteration_number (int): Iteration number
            output_dir (str): Output directory for the DOCX file
            base_name (str): Base name for the output file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"[TESTCASE_DOCX] Generating iteration {iteration_number} DOCX...")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            doc = Document()
            
            # Add document title
            doc.add_heading(f"Test Cases - Iteration {iteration_number}", level=0)
            doc.add_paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            doc.add_paragraph(f"Total Test Cases: {len(test_cases)}")
            
            # Summary of changes (if iteration > 1)
            if iteration_number > 1:
                doc.add_heading("Changes in This Iteration", level=1)
                regenerated_count = len([tc for tc in test_cases if tc.get('status') == 'regenerated'])
                original_count = len(test_cases) - regenerated_count
                
                changes_table = doc.add_table(rows=2, cols=2)
                changes_table.style = 'Table Grid'
                changes_table.rows[0].cells[0].text = "Original Test Cases"
                changes_table.rows[0].cells[1].text = str(original_count)
                changes_table.rows[1].cells[0].text = "Regenerated Test Cases"
                changes_table.rows[1].cells[1].text = str(regenerated_count)
            
            doc.add_page_break()
            
            # Generate standard test cases document
            self._add_testcases_to_document(doc, test_cases, show_status=True)
            
            # Save the file
            filename = os.path.join(output_dir, f"{base_name}_{iteration_number}.docx")
            doc.save(filename)
            self.logger.info(f"[TESTCASE_DOCX] Saved iteration {iteration_number} to: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"[TESTCASE_DOCX] Error generating iteration DOCX: {str(e)}")
            import traceback
            self.logger.error(f"[TESTCASE_DOCX] Full traceback: {traceback.format_exc()}")
            return False
    
    def _add_testcases_to_document(self, doc: Document, test_cases: List[Dict[str, Any]], show_status: bool = False) -> None:
        """
        Helper method to add test cases to a document.
        
        Args:
            doc (Document): The document to add test cases to
            test_cases (List[Dict[str, Any]]): Test cases to add
            show_status (bool): Whether to show the status column
        """
        # Create table of contents
        doc.add_heading("Table of Contents", level=1)
        cols = 4 if show_status else 3
        toc_table = doc.add_table(rows=1, cols=cols)
        toc_table.style = 'Table Grid'
        toc_hdr_cells = toc_table.rows[0].cells
        toc_hdr_cells[0].text = 'Test Case ID'
        toc_hdr_cells[1].text = 'Type'
        toc_hdr_cells[2].text = 'Description'
        if show_status:
            toc_hdr_cells[3].text = 'Status'
        
        # Populate table of contents
        for i, test_case in enumerate(test_cases):
            row_cells = toc_table.add_row().cells
            row_cells[0].text = test_case.get('test_case_id', f"TC_{i+1}")
            row_cells[1].text = test_case.get('test_case_type', 'N/A')
            description = test_case.get('test_case_description', 'N/A')
            row_cells[2].text = description[:100] + "..." if len(description) > 100 else description
            if show_status:
                status = test_case.get('status', 'original')
                row_cells[3].text = status.capitalize()
        
        doc.add_page_break()
        
        # Add detailed test cases
        doc.add_heading("Detailed Test Cases", level=1)
        
        for i, test_case in enumerate(test_cases):
            # Test case header
            header_text = f"Test Case {i + 1}: {test_case.get('test_case_id', f'TC_{i+1}')}"
            if show_status and test_case.get('status') == 'regenerated':
                header_text += " [REGENERATED]"
            doc.add_heading(header_text, level=2)
            
            # Test case details table
            rows = 5 if show_status else 4
            details_table = doc.add_table(rows=rows, cols=2)
            details_table.style = 'Table Grid'
            
            # Test case ID
            details_table.rows[0].cells[0].text = "Test Case ID"
            details_table.rows[0].cells[1].text = test_case.get('test_case_id', f'TC_{i+1}')
            
            # Test case type
            details_table.rows[1].cells[0].text = "Type"
            details_table.rows[1].cells[1].text = test_case.get('test_case_type', 'N/A')
            
            # Test case description
            details_table.rows[2].cells[0].text = "Description"
            details_table.rows[2].cells[1].text = test_case.get('test_case_description', 'N/A')
            
            # Priority
            details_table.rows[3].cells[0].text = "Priority"
            details_table.rows[3].cells[1].text = test_case.get('priority', 'Medium')
            
            # Status (if showing status)
            if show_status:
                details_table.rows[4].cells[0].text = "Status"
                status = test_case.get('status', 'original')
                status_text = status.capitalize()
                if status == 'regenerated':
                    reason = test_case.get('regeneration_reason', 'Regenerated')
                    status_text += f" - {reason}"
                details_table.rows[4].cells[1].text = status_text
            
            # Test steps section
            doc.add_heading("Test Steps", level=3)
            steps = test_case.get("test_steps", [])
            
            if steps:
                # Create a table for test steps
                steps_table = doc.add_table(rows=1, cols=3)
                steps_table.style = 'Table Grid'
                steps_hdr_cells = steps_table.rows[0].cells
                steps_hdr_cells[0].text = 'Step No.'
                steps_hdr_cells[1].text = 'Step'
                steps_hdr_cells[2].text = 'Expected Output'

                # Populate the steps table
                for step in steps:
                    row_cells = steps_table.add_row().cells
                    row_cells[0].text = str(step.get('step_number', ''))
                    row_cells[1].text = step.get('step', '')
                    row_cells[2].text = step.get('expected_output', '')
            else:
                doc.add_paragraph("No test steps defined for this test case.")
            
            # Add spacing between test cases
            if i < len(test_cases) - 1:
                doc.add_paragraph("")
                doc.add_paragraph("─" * 50)
                doc.add_paragraph("")