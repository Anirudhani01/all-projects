import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import concurrent.futures
from pathlib import Path
import json
import multiprocessing

from components.common.settings import Settings
from components.common.llm_client import LLMClient
from components.common.workflow_manager import WorkflowManager
from components.common.rag_service import RAGService
from components.story_enhancer.checker_service import CheckerService
from components.story_enhancer.enhancer_service import EnhancerService
from components.common.file_service import FileService
from components.story_enhancer.summarizer_service import SummarizerService
from components.parser.parser import DocxParser
from components.common.story_state import StoryState
from components.common.cache_manager import cache_manager
from components.story_enhancer.testcase_docx_generator_service import TestCaseDocxGeneratorService
from components.test_case_generator.pipeline import TestCasePipeline

class InitializationError(Exception):
    """Raised when service initialization fails."""
    pass

class StoryProcessor:
    """
    A class for processing stories through the enhancement pipeline.
    """
    def __init__(self, checker_service: CheckerService, 
                 enhancer_service: EnhancerService,
                 rag_service: RAGService,
                 summarizer_service: SummarizerService,
                 file_service: FileService,
                 workflow_manager: WorkflowManager,
                 settings: Any,
                 testcase_generation_service=None,
                 validator_service=None,
                 failed_testcases_regeneration_service=None,
                 accuracy_measure_service=None,
                 test_case_integration_service=None,
                 testcase_docx_generator_service=None):
        """Initialize the story processor."""
        self.checker_service = checker_service
        self.enhancer_service = enhancer_service
        self.rag_service = rag_service
        self.summarizer_service = summarizer_service
        self.file_service = file_service
        self.workflow_manager = workflow_manager
        self.settings = settings
        
        # New configurable services
        self.testcase_generation_service = testcase_generation_service
        self.validator_service = validator_service
        self.failed_testcases_regeneration_service = failed_testcases_regeneration_service
        self.accuracy_measure_service = accuracy_measure_service
        self.test_case_integration_service = test_case_integration_service
        self.testcase_docx_generator_service = testcase_docx_generator_service
        
        self.logger = logging.getLogger(__name__)

    def _setup_logging(self):
        """
        Setup logging - use the existing logger configured in main.py.
        """
        # Use the existing logger configured in main.py
        self.logger = logging.getLogger(__name__)
        self.logger.info("[INIT] StoryProcessor initialized")
    
    def _initialize_services(self):
        """Initialize all required services."""
        try:
            # Initialize LLM client
            self.llm_client = LLMClient(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
            )
            
            # Initialize services with proper paths
            base_dir = os.path.dirname(os.path.dirname(__file__))
            input_dir = os.path.join(base_dir, 'input')
            output_dir = os.path.join(base_dir, 'output')
            
            # Initialize parser for RAG service
            parser = DocxParser()
            
            self.file_service = FileService(input_dir=input_dir, output_dir=output_dir)
            self.rag_service = RAGService(parser=parser)  # Initialize with parser
            self.checker_service = CheckerService(self.llm_client, self.settings)
            self.enhancer_service = EnhancerService(self.llm_client, self.settings)
            self.summarizer_service = SummarizerService(self.llm_client, self.settings)
            
            self.logger.info("All services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            raise InitializationError(f"Service initialization failed: {e}")

    def _process_heading(self, heading: Dict[str, Any], story: Dict[str, Any], 
                        rag_chunks: str, document_summary: str = "") -> Dict[str, Any]:
        """
        Process a single heading with enhancement.
        
        Args:
            heading (Dict[str, Any]): The heading to process
            story (Dict[str, Any]): The full story context
            rag_chunks (str): RAG context chunks for additional information
            document_summary (str): Document summary for additional context
            
        Returns:
            Dict[str, Any]: The processed heading
        """
        if not self.settings.enable_enhancement:
            # If enhancement is disabled, just return the original heading
            return heading

        heading_id = heading["heading_id"]
        max_attempts = getattr(self.settings, 'max_attempts', 3)
        current_heading = heading.copy()
        
        try:
            for attempt in range(1, max_attempts + 1):
                self.logger.info(f"[ITERATION] Heading {heading_id} - Attempt {attempt}/{max_attempts}")
                
                # Get checker feedback using _review_headings with both RAG chunks and summary
                checker_response = self.checker_service._review_headings(
                    [current_heading],  # Pass as a single-item list
                    rag_chunks,
                    None,  # No previous feedback for single heading
                    document_summary  # Pass document summary as well
                )
                
                # Check if heading needs enhancement
                needs_enhancement = checker_response.get('needs_enhancement', {}).get(heading_id, True)
                
                if not needs_enhancement:
                    # Rating is "Excellent" - stop iterating
                    self.logger.info(f"[SUCCESS] Heading {heading_id} achieved excellent rating in {attempt} attempts")
                    return current_heading
                
                # Enhance the heading if it needs improvement
                if needs_enhancement:
                    self.logger.info(f"[ENHANCING] Heading {heading_id} needs improvement (attempt {attempt})")
                    enhanced_story = self.enhancer_service.enhance_story(
                        [current_heading],  # Pass as a single-item list
                        checker_response
                    )
                    
                    if enhanced_story and enhanced_story.get('headings'):
                        current_heading = enhanced_story['headings'][0]
                        self.logger.info(f"[ENHANCED] Heading {heading_id} enhanced for attempt {attempt}")
                    else:
                        self.logger.warning(f"[FAILED] Enhancement failed for heading {heading_id} on attempt {attempt}")
                        return current_heading
                
                # Check if this was the last attempt
                if attempt == max_attempts:
                    self.logger.info(f"[COMPLETED] Heading {heading_id} processing completed after {max_attempts} attempts")
                    return current_heading
            
        except Exception as e:
            self.logger.error(f"Error processing heading {heading_id}: {str(e)}")
            
        return heading
    
    def _process_complete_document(self, story: Dict[str, Any], identifier: str) -> Dict[str, Any]:
        """
        Process a complete document in non-heading mode.
        
        Args:
            story (Dict[str, Any]): The complete story to process
            identifier (str): Document identifier
            
        Returns:
            Dict[str, Any]: The processed complete document
        """
        if not self.settings.enable_enhancement:
            self.logger.info("Enhancement disabled, returning original document")
            return story
        
        try:
            self.logger.info(f"[PROCESSING] Checking document: {identifier}")
            
            # Fetch RAG chunks for context
            self.logger.info("[RAG] Fetching context from knowledge base...")
            rag_chunks = self._fetch_rag_context(story)
            
            max_attempts = getattr(self.settings, 'max_attempts', 3)
            current_story = story.copy()
            previous_checker_response = None
            
            # Iterative enhancement loop
            for attempt in range(1, max_attempts + 1):
                self.logger.info(f"[ITERATION] Complete document - Attempt {attempt}/{max_attempts}")
                
                # Get checker feedback for complete document
                checker_response = self.checker_service.review_story(
                    current_story,
                    rag_chunks,
                    previous_checker_response
                )
                
                # Check if document needs enhancement
                needs_enhancement = checker_response.get('needs_enhancement', {}).get('document', True)
                
                if not needs_enhancement:
                    # All fields rated "Excellent" - stop iterating
                    self.logger.info(f"[SUCCESS] Document achieved excellent rating in {attempt} attempts")
                    return current_story
                
                # Enhance the complete document if it needs improvement
                if needs_enhancement:
                    self.logger.info(f"[ENHANCING] Document needs improvement (attempt {attempt})")
                    enhanced_story = self.enhancer_service.enhance_complete_document(
                        current_story,
                        checker_response,
                        rag_chunks
                    )
                    
                    if enhanced_story:
                        current_story = enhanced_story
                        self.logger.info(f"[ENHANCED] Document enhanced for attempt {attempt}")
                    else:
                        self.logger.warning(f"[FAILED] Enhancement failed for document on attempt {attempt}")
                        return current_story
                
                # Update previous checker response for next iteration
                previous_checker_response = checker_response
                
                # Check if this was the last attempt
                if attempt == max_attempts:
                    self.logger.info(f"[COMPLETED] Document processing completed after {max_attempts} attempts")
                    return current_story
            
        except Exception as e:
            self.logger.error(f"Error processing complete document {identifier}: {str(e)}")
            return story
    
    def _fetch_rag_context(self, story: Dict[str, Any]) -> str:
        """
        Fetch RAG context for the story using the adaptive RAG pipeline.
        
        Args:
            story (Dict[str, Any]): The story to get context for
            
        Returns:
            str: RAG chunks/context
        """
        try:
            # Extract plain text from the story for use as query
            if "headings" in story:
                # For heading-based stories, extract content from all headings
                query_parts = []
                for heading in story["headings"]:
                    title = heading.get('title', '')
                    content = heading.get('content', '')
                    if isinstance(content, list):
                        content = ' '.join(str(item) for item in content)
                    query_parts.append(f"{title} {content}")
                query_text = ' '.join(query_parts)
            else:
                # For section-based stories
                query_parts = []
                for section in story.get("sections", []):
                    title = section.get('title', '')
                    content = section.get('content', '')
                    if isinstance(content, list):
                        content = ' '.join(str(item) for item in content)
                    query_parts.append(f"{title} {content}")
                query_text = ' '.join(query_parts)
            
            # Truncate query to reasonable length
            query_text = query_text[:3000] if query_text else "telecom user story enhancement"
            
            # Use the RAG service to fetch context
            rag_context = self.rag_service.fetch_rag_chunks(query_text)
            
            # Log the retrieved chunks
            self.logger.info(f"[RAG] Retrieved {len(rag_context)} characters of context")
            self.logger.debug(f"[RAG] Context preview: {rag_context[:500]}...")
            
            return rag_context
            
        except Exception as e:
            self.logger.error(f"[RAG] Failed to fetch context: {str(e)}")
            return ""
    
    def _calculate_document_size(self, story: Dict[str, Any]) -> int:
        """
        Calculate the total character count of the document.
        
        Args:
            story (Dict[str, Any]): The story to calculate size for
            
        Returns:
            int: Total character count
        """
        total_chars = 0
        
        if "headings" in story:
            # For heading-based stories
            for heading in story["headings"]:
                title = heading.get('title', '')
                content = heading.get('content', '')
                if isinstance(content, list):
                    content = ' '.join(str(item) for item in content)
                total_chars += len(str(title)) + len(str(content))
        else:
            # For section-based stories
            for section in story.get("sections", []):
                title = section.get('title', '')
                content = section.get('content', '')
                if isinstance(content, list):
                    content = ' '.join(str(item) for item in content)
                total_chars += len(str(title)) + len(str(content))
        
        return total_chars

    def _replace_ids_with_info(self, data: Any, id_to_info_map: Dict[str, Dict[str, str]]) -> None:
        """
        Recursively replace test case IDs with test_case_type and test_case_description.
        
        Args:
            data: The data structure to process (dict, list, or other)
            id_to_info_map: Mapping from test_case_id to info dict
        """
        if isinstance(data, dict):
            # Check if this dict has an 'id' field that matches our test case IDs
            if 'id' in data and data['id'] in id_to_info_map:
                info = id_to_info_map[data['id']]
                # Replace id with test_case_type and test_case_description
                data['test_case_type'] = info['test_case_type']
                data['test_case_description'] = info['test_case_description']
                # Remove the original 'id' field
                del data['id']
            
            # Recursively process all values in the dict
            for value in data.values():
                self._replace_ids_with_info(value, id_to_info_map)
        elif isinstance(data, list):
            # Recursively process all items in the list
            for item in data:
                self._replace_ids_with_info(item, id_to_info_map)

    def _process_test_cases_in_chunks(self, test_cases: List[Dict[str, Any]], service_method, structured_text: str, rag_chunks: str, service_type: str, chunk_size: int = 20) -> Dict[str, Any]:
        """
        Process test cases in chunks using parallel processing to avoid token limits.
        
        Args:
            test_cases: List of test cases to process
            service_method: The service method to call (validator)
            structured_text: Structured story text
            rag_chunks: RAG context
            service_type: "validation" for result formatting
            chunk_size: Number of test cases per chunk
            
        Returns:
            Combined results from all chunks
        """
        if not test_cases:
            return {}
            
        total_chunks = (len(test_cases) + chunk_size - 1) // chunk_size
        max_workers = multiprocessing.cpu_count()
        
        self.logger.info(f"[{service_type.upper()}] Processing {len(test_cases)} test cases in {total_chunks} chunks of {chunk_size} using {max_workers} parallel workers")
        
        # Create chunks
        chunks = []
        for i in range(0, len(test_cases), chunk_size):
            chunk = test_cases[i:i + chunk_size]
            chunk_num = (i // chunk_size) + 1
            chunks.append((chunk, chunk_num))
        
        all_results = []
        
        # Process chunks in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all chunks for processing
            future_to_chunk = {
                executor.submit(self._process_single_chunk, chunk, chunk_num, service_method, structured_text, rag_chunks, service_type, total_chunks): (chunk, chunk_num)
                for chunk, chunk_num in chunks
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_chunk):
                chunk, chunk_num = future_to_chunk[future]
                try:
                    chunk_items = future.result()
                    if chunk_items:
                        all_results.extend(chunk_items)
                        self.logger.info(f"[{service_type.upper()}] Chunk {chunk_num} processed successfully: {len(chunk_items)} results")
                except Exception as e:
                    self.logger.error(f"[{service_type.upper()}] Error processing chunk {chunk_num}: {e}")
                    continue
        
        # Format final result
        if service_type == "validation":
            return {"validated_test_cases": all_results}
        else:
            return {"results": all_results}
    
    def _process_single_chunk(self, chunk: List[Dict[str, Any]], chunk_num: int, service_method, structured_text: str, rag_chunks: str, service_type: str, total_chunks: int) -> List[Dict[str, Any]]:
        """
        Process a single chunk of test cases.
        
        Args:
            chunk: Test cases chunk to process
            chunk_num: Chunk number for logging
            service_method: The service method to call
            structured_text: Structured story text
            rag_chunks: RAG context
            service_type: Type of service for logging
            total_chunks: Total number of chunks for logging
            
        Returns:
            List of processed results from this chunk
        """
        self.logger.info(f"[{service_type.upper()}] Processing chunk {chunk_num}/{total_chunks} ({len(chunk)} test cases)")
        
        try:
            chunk_result = service_method(structured_text, rag_chunks, chunk)
            
            # Parse result if it's a string
            if isinstance(chunk_result, str):
                try:
                    chunk_result = json.loads(chunk_result)
                except json.JSONDecodeError:
                    self.logger.warning(f"[{service_type.upper()}] Failed to parse chunk {chunk_num} result as JSON")
                    return []
            
            # Extract results for validation
            if service_type == "validation" and isinstance(chunk_result, dict):
                chunk_items = chunk_result.get("validated_test_cases", [])
            else:
                chunk_items = chunk_result if isinstance(chunk_result, list) else []
            
            return chunk_items
            
        except Exception as e:
            self.logger.error(f"[{service_type.upper()}] Error processing chunk {chunk_num}: {e}")
            return []

    def _generate_platform_test_cases(self, pipeline, flows, business_context, platform: str, output_dir: str, base_name: str) -> Optional[str]:
        """
        Generate test cases for a specific platform.
        
        Args:
            pipeline: Test case generation pipeline instance
            flows: Flow data for test case generation
            business_context: Business context for test case generation
            platform: Platform name (web, mobile)
            output_dir: Output directory path
            base_name: Base filename
            
        Returns:
            Path to generated test case file, or None if generation failed
        """
        try:
            self.logger.info(f"[TESTCASE_GENERATION_{platform.upper()}] Generating test cases for {platform} platform...")
            
            # Generate test cases for this platform
            test_cases = pipeline.generate_test_cases(flows, business_context, platform=platform)
            
            if not test_cases:
                self.logger.warning(f"[TESTCASE_GENERATION_{platform.upper()}] No test cases generated for {platform} platform")
                return None
                
            # Save test cases to platform-specific file
            testcase_path = os.path.join(output_dir, f"{base_name}_testcases_{platform}.json")
            pipeline.save_test_cases_to_file(test_cases, testcase_path)
            
            self.logger.info(f"[TESTCASE_GENERATION_{platform.upper()}] {len(test_cases)} test cases saved to: {testcase_path}")
            return testcase_path
            
        except Exception as e:
            self.logger.error(f"[TESTCASE_GENERATION_{platform.upper()}] Error generating test cases for {platform}: {e}")
            return None

    def _run_parallel_validation_iterations(self, story: Dict[str, Any], rag_chunks: str, identifier: str, output_dir: str, base_name: str, structured_text: str) -> None:
        """
        Run validation iterations for multiple platform test cases in parallel.
        
        Args:
            story: The story object
            rag_chunks: RAG context chunks
            identifier: Document identifier
            output_dir: Output directory
            base_name: Base filename
            structured_text: Structured story text
        """
        self.logger.info(f"[PARALLEL_VALIDATION] Starting parallel validation for {len(self.testcase_paths)} platforms...")
        
        # Process each platform's test cases in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.testcase_paths)) as executor:
            future_to_platform = {}
            
            for platform, testcase_path in self.testcase_paths.items():
                self.logger.info(f"[PARALLEL_VALIDATION] Submitting validation for {platform} platform...")
                future = executor.submit(
                    self._run_single_platform_validation,
                    testcase_path, platform, story, rag_chunks, identifier, output_dir, base_name, structured_text
                )
                future_to_platform[future] = platform
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    future.result()
                    self.logger.info(f"[PARALLEL_VALIDATION] Validation completed successfully for {platform} platform")
                except Exception as e:
                    self.logger.error(f"[PARALLEL_VALIDATION] Error validating {platform} platform: {e}")
        
        self.logger.info(f"[PARALLEL_VALIDATION] All platform validations completed")

    def _run_single_platform_validation(self, testcase_path: str, platform: str, story: Dict[str, Any], rag_chunks: str, identifier: str, output_dir: str, base_name: str, structured_text: str) -> None:
        """
        Run validation iterations for a single platform's test cases.
        
        Args:
            testcase_path: Path to the test case JSON file
            platform: Platform name (web, mobile)
            story: The story object
            rag_chunks: RAG context chunks
            identifier: Document identifier
            output_dir: Output directory
            base_name: Base filename
            structured_text: Structured story text
        """
        try:
            # Load test cases for this platform
            with open(testcase_path, 'r', encoding='utf-8') as f:
                test_cases = json.load(f)
            
            if not test_cases:
                self.logger.warning(f"[VALIDATION_{platform.upper()}] No test cases found for {platform} platform")
                return
            
            platform_base_name = f"{base_name}_{platform}"
            self.logger.info(f"[VALIDATION_{platform.upper()}] Running {self.settings.validation_iteration_count} validation iterations for {len(test_cases)} test cases...")
            
            # Run validation iterations for this platform
            for iteration in range(1, self.settings.validation_iteration_count + 1):
                self.logger.info(f"[VALIDATION_{platform.upper()}] Starting iteration {iteration}/{self.settings.validation_iteration_count}")
                
                validation_result = self._run_single_validation_iteration(
                    test_cases, structured_text, rag_chunks, iteration, output_dir, platform_base_name
                )
                
                # Run failed test case regeneration if enabled
                if self.settings.failed_testcases_regenerator and self.failed_testcases_regeneration_service:
                    regeneration_result = self._run_single_failed_regeneration_iteration(
                        validation_result, structured_text, rag_chunks, iteration, output_dir, platform_base_name
                    )
                    # Update test cases with regenerated ones
                    if regeneration_result and "regenerated_test_cases" in regeneration_result:
                        test_cases = regeneration_result["regenerated_test_cases"]
                
                # Run accuracy measurement if enabled
                if self.settings.testcases_accuracy and self.accuracy_measure_service:
                    self._run_single_accuracy_iteration(
                        test_cases, validation_result, iteration, output_dir, platform_base_name
                    )
            
            # Save final updated test cases for this platform
            final_testcase_path = os.path.join(output_dir, f"{platform_base_name}_updated_testcases.json")
            with open(final_testcase_path, 'w', encoding='utf-8') as f:
                json.dump(test_cases, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"[VALIDATION_{platform.upper()}] Final updated test cases saved to {final_testcase_path}")
            
        except Exception as e:
            self.logger.error(f"[VALIDATION_{platform.upper()}] Error in platform validation: {e}")
            raise

    def _run_validation_iterations(self, story: Dict[str, Any], rag_chunks: str, identifier: str, output_dir: str, base_name: str, structured_text: str) -> None:
        """
        Run multiple validation iterations as configured.
        
        Args:
            story (Dict[str, Any]): The processed story
            rag_chunks (str): RAG context chunks
            identifier (str): Document identifier
            output_dir (str): Output directory path
            base_name (str): Base filename
            structured_text (str): Structured text for test services
        """
        iteration_count = self.settings.validation_iteration_count
        self.logger.info(f"[VALIDATION_ITERATIONS] Running {iteration_count} validation iterations...")
        
        # Initialize data structures for tracking iterations
        all_validation_results = []
        all_accuracy_results = []
        current_test_cases = None
        
        # Load the initial test cases
        testcase_file = os.path.join(output_dir, f"{base_name}_testcases.json")
        if os.path.exists(testcase_file):
            with open(testcase_file, 'r', encoding='utf-8') as f:
                testcase_data = json.load(f)
                if isinstance(testcase_data, list):
                    current_test_cases = testcase_data
                elif isinstance(testcase_data, dict):
                    current_test_cases = testcase_data.get("test_cases", testcase_data.get("generated_test_cases", []))
        
        if not current_test_cases:
            self.logger.warning("[VALIDATION_ITERATIONS] No test cases found for validation")
            return
        
        # Add sequential IDs to test cases if they don't have them
        for i, test_case in enumerate(current_test_cases, 1):
            if "test_case_id" not in test_case:
                test_case["test_case_id"] = f"TESTCASE_{i}"
        
        for iteration in range(1, iteration_count + 1):
            self.logger.info(f"[VALIDATION_ITERATIONS] Starting iteration {iteration}/{iteration_count}...")
            
            # Run validation for current iteration
            validation_result = self._run_single_validation_iteration(
                current_test_cases, structured_text, rag_chunks, iteration, output_dir, base_name
            )
            all_validation_results.append({
                "iteration": iteration,
                "validation_result": validation_result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Run failed test case regeneration if enabled and there are failed cases
            regenerated_cases = None
            if self.settings.failed_testcases_regenerator and self.failed_testcases_regeneration_service:
                regenerated_cases = self._run_single_failed_regeneration_iteration(
                    validation_result, structured_text, rag_chunks, iteration, output_dir, base_name
                )
                
                # Update current test cases with regenerated ones for next iteration
                if regenerated_cases:
                    current_test_cases = self._merge_regenerated_test_cases(current_test_cases, regenerated_cases)
                    
                    # Save updated test cases after merging regenerated ones
                    if iteration == 1:
                        updated_file = os.path.join(output_dir, f"{base_name}_updated_testcases.json")
                    else:
                        updated_file = os.path.join(output_dir, f"{base_name}_updated_testcases_iter_{iteration-1}.json")
                    
                    updated_data = {
                        "updated_test_cases": current_test_cases,
                        "total_test_cases": len(current_test_cases),
                        "iteration": iteration,
                        "timestamp": datetime.now().isoformat(),
                        "description": f"Test cases updated after iteration {iteration} with regenerated cases"
                    }
                    
                    with open(updated_file, 'w', encoding='utf-8') as f:
                        json.dump(updated_data, f, indent=2, ensure_ascii=False)
                    
                    self.logger.info(f"[VALIDATION_ITERATIONS] Updated test cases saved to {updated_file}")
            
            # Measure accuracy for current iteration if enabled
            if self.settings.testcases_accuracy and self.accuracy_measure_service:
                accuracy_result = self._run_single_accuracy_iteration(
                    current_test_cases, validation_result, iteration, output_dir, base_name
                )
                all_accuracy_results.append({
                    "iteration": iteration,
                    "accuracy_result": accuracy_result,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Save final cumulative validation results
        if all_validation_results:
            final_validation_file = os.path.join(output_dir, f"{base_name}_validation.json")
            final_validation_data = {
                "all_iterations": all_validation_results,
                "total_iterations": len(all_validation_results),
                "latest_validation_result": all_validation_results[-1]["validation_result"] if all_validation_results else None
            }
            with open(final_validation_file, 'w', encoding='utf-8') as f:
                json.dump(final_validation_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"[VALIDATION_ITERATIONS] Final validation results saved to {final_validation_file}")
        
        # Save final cumulative accuracy results if enabled
        if self.settings.testcases_accuracy and all_accuracy_results:
            self._save_cumulative_accuracy_results(all_accuracy_results, output_dir, base_name)
        
        self.logger.info(f"[VALIDATION_ITERATIONS] Completed all {iteration_count} iterations")

    def _run_single_validation_iteration(self, test_cases: List[Dict[str, Any]], structured_text: str, rag_chunks: str, iteration: int, output_dir: str, base_name: str) -> Dict[str, Any]:
        """
        Run a single validation iteration.
        
        Args:
            test_cases: Test cases to validate
            structured_text: Structured story text
            rag_chunks: RAG context chunks
            iteration: Current iteration number
            output_dir: Output directory
            base_name: Base filename
            
        Returns:
            Validation results
        """
        self.logger.info(f"[VALIDATION_ITERATIONS] Running validation for iteration {iteration}...")
        
        # Process test cases in chunks to avoid token limits
        validation_result = self._process_test_cases_in_chunks(
            test_cases, self.validator_service.test_case_validator_with_text, 
            structured_text, rag_chunks, "validation", self.settings.test_case_chunk_size)
        
        # Create mapping from test_case_id to test_case_type and test_case_description
        id_to_info_map = {}
        for test_case in test_cases:
            test_case_id = test_case.get("test_case_id", "")
            test_case_type = test_case.get("test_case_type", "")
            test_case_description = test_case.get("test_case_description", "")
            if test_case_id:
                id_to_info_map[test_case_id] = {
                    "test_case_type": test_case_type,
                    "test_case_description": test_case_description
                }
        
        # Update validation result with test_case_type and description
        if isinstance(validation_result, dict):
            self._replace_ids_with_info(validation_result, id_to_info_map)
        
        # Save validation results for this iteration
        if iteration == 1:
            validation_file = os.path.join(output_dir, f"{base_name}_validation.json")
        else:
            validation_file = os.path.join(output_dir, f"{base_name}_validation_iter_{iteration-1}.json")
        with open(validation_file, 'w', encoding='utf-8') as f:
            json.dump(validation_result, f, indent=2, ensure_ascii=False)
        
        # Individual iteration validation files are saved above
        # Main validation file will be saved after all iterations complete
        
        self.logger.info(f"[VALIDATION_ITERATIONS] Validation iteration {iteration} completed")
        return validation_result

    def _run_single_failed_regeneration_iteration(self, validation_result: Dict[str, Any], structured_text: str, rag_chunks: str, iteration: int, output_dir: str, base_name: str) -> Dict[str, Any]:
        """
        Run a single failed test case regeneration iteration.
        
        Args:
            validation_result: Results from validation
            structured_text: Structured story text
            rag_chunks: RAG context chunks
            iteration: Current iteration number
            output_dir: Output directory
            base_name: Base filename
            
        Returns:
            Regenerated test cases
        """
        self.logger.info(f"[VALIDATION_ITERATIONS] Running failed test case regeneration for iteration {iteration}...")
        
        # Extract failed test cases from validation result
        failed_cases = []
        if isinstance(validation_result, dict) and "validated_test_cases" in validation_result:
            for case in validation_result["validated_test_cases"]:
                if isinstance(case, dict) and case.get("validation_passed") == False:
                    failed_cases.append(case)
                    self.logger.info(f"[VALIDATION_ITERATIONS] Found failed test case in iteration {iteration}: {case.get('test_case_type', 'Unknown')} - {case.get('test_case_description', 'No description')}")
        
        if failed_cases:
            # Regenerate failed test cases
            self.logger.info(f"[VALIDATION_ITERATIONS] Regenerating {len(failed_cases)} failed test cases for iteration {iteration}...")
            regenerated_cases = self.failed_testcases_regeneration_service.failed_test_cases_regenerator(
                structured_text, 
                validation_result, 
                rag_chunks
            )
            
            # Save regenerated test cases for this iteration - only containing regenerated cases
            if iteration == 1:
                regenerated_file = os.path.join(output_dir, f"{base_name}_regenerated_testcases.json")
            else:
                regenerated_file = os.path.join(output_dir, f"{base_name}_regenerated_testcases_iter_{iteration-1}.json")
            
            # Extract only the regenerated test cases from the response
            regenerated_only = {}
            if isinstance(regenerated_cases, dict) and "test_cases" in regenerated_cases:
                regenerated_only = {
                    "regenerated_test_cases": regenerated_cases["test_cases"],
                    "total_regenerated": len(regenerated_cases["test_cases"]),
                    "iteration": iteration,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                regenerated_only = {
                    "regenerated_test_cases": regenerated_cases if isinstance(regenerated_cases, list) else [],
                    "total_regenerated": len(regenerated_cases) if isinstance(regenerated_cases, list) else 0,
                    "iteration": iteration,
                    "timestamp": datetime.now().isoformat()
                }
                
            with open(regenerated_file, 'w', encoding='utf-8') as f:
                json.dump(regenerated_only, f, indent=2, ensure_ascii=False)
                    
            self.logger.info(f"[VALIDATION_ITERATIONS] Regenerated test cases for iteration {iteration} saved")
            return regenerated_cases
        else:
            self.logger.info(f"[VALIDATION_ITERATIONS] No failed test cases found in iteration {iteration} - skipping regeneration")
            return {"message": f"No failed test cases to regenerate in iteration {iteration}"}

    def _run_single_accuracy_iteration(self, test_cases: List[Dict[str, Any]], validation_result: Dict[str, Any], iteration: int, output_dir: str, base_name: str) -> Dict[str, Any]:
        """
        Run a single accuracy measurement iteration.
        
        Args:
            test_cases: Test cases to measure
            validation_result: Validation results
            iteration: Current iteration number
            output_dir: Output directory
            base_name: Base filename
            
        Returns:
            Accuracy measurement results
        """
        self.logger.info(f"[VALIDATION_ITERATIONS] Running accuracy measurement for iteration {iteration}...")
        
        # Use the programmatic accuracy measurement
        accuracy_result = self.accuracy_measure_service.measure_accuracy_programmatically(
            test_cases, validation_result
        )
        
        # Add iteration metadata
        accuracy_result["iteration"] = iteration
        accuracy_result["timestamp"] = datetime.now().isoformat()
        
        # Save individual accuracy results for this iteration
        if iteration == 1:
            accuracy_file = os.path.join(output_dir, f"{base_name}_accuracy_measure.json")
        else:
            accuracy_file = os.path.join(output_dir, f"{base_name}_accuracy_measure_iter_{iteration-1}.json")
        
        with open(accuracy_file, 'w', encoding='utf-8') as f:
            json.dump(accuracy_result, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"[VALIDATION_ITERATIONS] Accuracy measurement for iteration {iteration} completed and saved to {accuracy_file}")
        return accuracy_result

    def _merge_regenerated_test_cases(self, original_test_cases: List[Dict[str, Any]], regenerated_cases: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Merge regenerated test cases with original ones by replacing failed cases.
        
        Args:
            original_test_cases: Original test cases
            regenerated_cases: Regenerated test cases (should contain only regenerated cases)
            
        Returns:
            Merged test cases for next iteration with failed cases replaced
        """
        merged_cases = original_test_cases.copy()
        
        if isinstance(regenerated_cases, dict) and "test_cases" in regenerated_cases:
            new_cases = regenerated_cases["test_cases"]
            if isinstance(new_cases, list) and len(new_cases) > 0:
                # Simply append the regenerated test cases (they are replacements for failed ones)
                # Give them new sequential IDs to avoid conflicts
                next_id = max(
                    [int(case.get("test_case_id", "0").split("_")[-1]) 
                     for case in merged_cases 
                     if case.get("test_case_id", "").startswith("TESTCASE_")], 
                    default=0
                ) + 1
                
                for new_case in new_cases:
                    if isinstance(new_case, dict):
                        # Assign a new unique ID for the regenerated test case
                        new_case["test_case_id"] = f"TESTCASE_{next_id}"
                        new_case["regenerated"] = True  # Mark as regenerated for tracking
                        merged_cases.append(new_case)
                        next_id += 1
                
                self.logger.info(f"[VALIDATION_ITERATIONS] Added {len(new_cases)} regenerated test cases to the test suite")
                return merged_cases
        
        # If no valid regenerated cases, return original
        self.logger.info("[VALIDATION_ITERATIONS] No regenerated cases to merge")
        return original_test_cases

    def _save_cumulative_accuracy_results(self, all_accuracy_results: List[Dict[str, Any]], output_dir: str, base_name: str) -> None:
        """
        Save cumulative accuracy results from all iterations.
        
        Args:
            all_accuracy_results: All accuracy results from iterations
            output_dir: Output directory
            base_name: Base filename
        """
        # Calculate overall statistics
        total_iterations = len(all_accuracy_results)
        
        # Create cumulative accuracy data
        cumulative_data = {
            "total_iterations": total_iterations,
            "iterations": all_accuracy_results,
            "summary": {
                "overall_accuracy": 0.0,
                "total_test_cases_across_iterations": 0,
                "total_passed_across_iterations": 0,
                "accuracy_trend": []
            },
            "generated_at": datetime.now().isoformat()
        }
        
        # Calculate summary statistics
        total_passed = 0
        total_cases = 0
        
        for result in all_accuracy_results:
            if "accuracy_result" in result:
                accuracy_data = result["accuracy_result"]
                if "total_test_cases" in accuracy_data:
                    total_cases += accuracy_data["total_test_cases"]
                if "passed_test_cases" in accuracy_data:
                    total_passed += accuracy_data["passed_test_cases"]
                if "accuracy_percentage" in accuracy_data:
                    cumulative_data["summary"]["accuracy_trend"].append({
                        "iteration": result["iteration"],
                        "accuracy": accuracy_data["accuracy_percentage"]
                    })
        
        if total_cases > 0:
            cumulative_data["summary"]["overall_accuracy"] = (total_passed / total_cases) * 100
            cumulative_data["summary"]["total_test_cases_across_iterations"] = total_cases
            cumulative_data["summary"]["total_passed_across_iterations"] = total_passed
        
        # Save cumulative accuracy results
        accuracy_file = os.path.join(output_dir, f"{base_name}_accuracy_measure.json")
        with open(accuracy_file, 'w', encoding='utf-8') as f:
            json.dump(cumulative_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"[VALIDATION_ITERATIONS] Cumulative accuracy results saved to {accuracy_file}")
        self.logger.info(f"[VALIDATION_ITERATIONS] Overall accuracy across {total_iterations} iterations: {cumulative_data['summary']['overall_accuracy']:.2f}%")

    def _process_additional_services(self, story: Dict[str, Any], rag_chunks: str, identifier: str) -> None:
        """
        Process additional services based on configuration flags.
        
        Args:
            story (Dict[str, Any]): The processed story
            rag_chunks (str): RAG context chunks
            identifier (str): Document identifier
        """
        try:
            base_name = os.path.splitext(identifier)[0]
            output_dir = self.settings.output_dir
            
            # Generate structured text once for all services
            structured_text = ""
            if any([
                self.settings.testcasegeneration and self.testcase_generation_service,
                self.settings.validatoranddebugger and self.validator_service,
                self.settings.validatoranddebugger and self.validator_service
            ]):
                self.logger.info("[PROCESSING] Generating structured text for test services...")
                if self.testcase_generation_service:
                    structured_text = self.testcase_generation_service.story_to_structured_json(story)
                    # Calculate actual character count for logging
                    if isinstance(structured_text, dict):
                        char_count = len(json.dumps(structured_text))
                    else:
                        char_count = len(structured_text)
                    self.logger.debug(f"[PROCESSING] Structured text generated: {char_count} chars")
                    
                    # Save structured text to separate JSON file
                    structured_text_file = os.path.join(output_dir, f"{base_name}_structured_text.json")
                    with open(structured_text_file, 'w', encoding='utf-8') as f:
                        if isinstance(structured_text, dict):
                            f.write(json.dumps(structured_text, indent=2))
                        else:
                            f.write(structured_text)

            # Integrated test case generation within story processing pipeline
            if self.settings.testcasegeneration:
                self.logger.info("Starting test case generation...")
                
                # Initialize the test case pipeline
                pipeline = TestCasePipeline(document_path=structured_text_file,
                                            api_key=os.getenv("OPENAI_API_KEY", ""),
                                            logger=self.logger)

                # Step 1: Load flows and business context from the input file
                flows, business_context = pipeline.load_input_file()

                # Step 2: Generate test cases for both platforms in parallel
                testcase_paths = {}
                # Configure which platforms to generate (can be made configurable via environment variable)
                platforms = ["web", "mobile"]  # Add or remove platforms as needed
                
                self.logger.info(f"[PARALLEL_TESTCASE_GENERATION] Starting parallel test case generation for {len(platforms)} platforms...")
                
                # Process both platforms in parallel
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(platforms)) as executor:
                    future_to_platform = {}
                    
                    for platform in platforms:
                        self.logger.info(f"[PARALLEL_TESTCASE_GENERATION] Submitting test case generation for {platform} platform...")
                        future = executor.submit(
                            self._generate_platform_test_cases,
                            pipeline, flows, business_context, platform, output_dir, base_name
                        )
                        future_to_platform[future] = platform
                    
                    # Collect results as they complete
                    for future in concurrent.futures.as_completed(future_to_platform):
                        platform = future_to_platform[future]
                        try:
                            platform_testcase_path = future.result()
                            if platform_testcase_path:
                                testcase_paths[platform] = platform_testcase_path
                                self.logger.info(f"[PARALLEL_TESTCASE_GENERATION] {platform.capitalize()} test case generation completed successfully")
                        except Exception as e:
                            self.logger.error(f"[PARALLEL_TESTCASE_GENERATION] Error generating {platform} test cases: {e}")
                
                # Store testcase paths for validation
                self.testcase_paths = testcase_paths
                self.logger.info(f"[PARALLEL_TESTCASE_GENERATION] All platform test case generations completed. Generated {len(testcase_paths)} platform files.")
                
                # Generate initial DOCX if enabled (before validation iterations)
                if self.settings.enable_testcase_docx and self.testcase_docx_generator_service:
                    for platform, testcase_path in testcase_paths.items():
                        try:
                            initial_base_name = f"{base_name}_testcases_{platform}"
                            self.logger.info(f"[DOCX_GENERATION] Generating initial DOCX test case document for {platform}...")
                            success = self.testcase_docx_generator_service.generate_from_json_file(
                                testcase_path, output_dir, initial_base_name
                            )
                            if success:
                                self.logger.info(f"[DOCX_GENERATION] Initial DOCX test cases generated: {initial_base_name}.docx")
                            else:
                                self.logger.warning(f"[DOCX_GENERATION] Failed to generate initial DOCX test cases for {platform}")
                        except Exception as e:
                            self.logger.error(f"[TESTCASE_DOCX] Error generating DOCX from JSON file: {e}")
                            self.logger.warning(f"[DOCX_GENERATION] Failed to generate initial DOCX test cases for {platform}")
                
                self.logger.info("Test case generation completed successfully")
            
            # Run validation iterations if enabled (includes validator, failed regeneration, and accuracy)
            if self.settings.validatoranddebugger and self.validator_service:
                if hasattr(self, 'testcase_paths') and self.testcase_paths:
                    # Validate multiple platform test cases in parallel
                    self._run_parallel_validation_iterations(story, rag_chunks, identifier, output_dir, base_name, structured_text)
                else:
                    # Fallback to original single validation (for backward compatibility)
                    self._run_validation_iterations(story, rag_chunks, identifier, output_dir, base_name, structured_text)
            
            # Generate final DOCX test cases if validation iterations were run
            if (self.settings.enable_testcase_docx and 
                self.testcase_docx_generator_service and 
                self.settings.testcasegeneration and
                self.settings.validatoranddebugger and self.validator_service):
                
                if hasattr(self, 'testcase_paths') and self.testcase_paths:
                    # Generate final DOCX for each platform
                    for platform in self.testcase_paths.keys():
                        try:
                            platform_base_name = f"{base_name}_{platform}"
                            final_base_name = f"final_{platform_base_name}_testcases"
                            
                            # Look for the latest updated test cases file for this platform
                            updated_file = os.path.join(output_dir, f"{platform_base_name}_updated_testcases.json")
                            
                            if os.path.exists(updated_file):
                                self.logger.info(f"[DOCX_GENERATION] Generating final DOCX for {platform} platform...")
                                success = self.testcase_docx_generator_service.generate_from_json_file(
                                    updated_file, output_dir, final_base_name
                                )
                                if success:
                                    self.logger.info(f"[DOCX_GENERATION] Final DOCX test cases generated successfully for {platform}")
                                else:
                                    self.logger.warning(f"[DOCX_GENERATION] Failed to generate final DOCX test cases for {platform}")
                            else:
                                self.logger.debug(f"[DOCX_GENERATION] Updated test cases file not found for {platform}, skipping final DOCX generation")
                        except Exception as e:
                            self.logger.error(f"[DOCX_GENERATION] Error generating final DOCX test cases for {platform}: {str(e)}")
                else:
                    # Fallback to original single platform logic
                    try:
                        # Use the final updated test cases if validation iterations were run
                        testcase_json_path = None
                        final_base_name = f"final_{base_name}_testcases"
                        
                        if self.settings.validatoranddebugger and self.settings.validation_iteration_count > 1:
                            # Look for the latest updated test cases file
                            updated_file = os.path.join(output_dir, f"{base_name}_updated_testcases_iter_{self.settings.validation_iteration_count-1}.json")
                            if os.path.exists(updated_file):
                                testcase_json_path = updated_file
                                self.logger.info(f"[DOCX_GENERATION] Using final updated test cases from iteration {self.settings.validation_iteration_count}")
                            else:
                                # Fallback to single iteration updated file
                                updated_file = os.path.join(output_dir, f"{base_name}_updated_testcases.json")
                                if os.path.exists(updated_file):
                                    testcase_json_path = updated_file
                                    self.logger.info("[DOCX_GENERATION] Using updated test cases from single iteration")
                        
                        # Fallback to original test cases if no updated ones exist
                        if not testcase_json_path:
                            testcase_json_path = os.path.join(output_dir, f"{base_name}_testcases.json")
                            final_base_name = f"final_{base_name}_testcases"
                            
                        if os.path.exists(testcase_json_path):
                            self.logger.info("[DOCX_GENERATION] Generating final DOCX test case document...")
                            success = self.testcase_docx_generator_service.generate_from_json_file(
                                testcase_json_path, output_dir, final_base_name
                            )
                            if success:
                                self.logger.info(f"[DOCX_GENERATION] DOCX test cases generated successfully")
                            else:
                                self.logger.warning("[DOCX_GENERATION] Failed to generate DOCX test cases")
                        else:
                            self.logger.debug("[DOCX_GENERATION] Test cases JSON file not found, skipping DOCX generation")
                    except Exception as e:
                        self.logger.error(f"[DOCX_GENERATION] Error generating DOCX test cases: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Error in additional services processing: {str(e)}")

    def _should_bypass_parsing(self) -> bool:
        """
        Determine if we should bypass parsing and use direct file copy.
        
        Returns True when:
        - Enhancement is disabled AND
        - No additional services requiring JSON processing are enabled
        """
        if self.settings.enable_enhancement:
            return False
            
        # Check if any services that require JSON processing are enabled
        services_requiring_json = [
            self.settings.testcasegeneration and self.testcase_generation_service,
            self.settings.validatoranddebugger and self.validator_service
        ]
        
        return not any(services_requiring_json)

    def process_story(self, story: Dict[str, Any], identifier: str) -> Optional[Dict[str, Any]]:
        """
        Process a story through the enhancement pipeline.
        
        Args:
            story (Dict[str, Any]): The story to process
            identifier (str): Unique identifier for the story
            
        Returns:
            Optional[Dict[str, Any]]: The processed story, or None if processing fails
        """
        try:
            # Check if we should bypass parsing and use direct file copy
            if self._should_bypass_parsing():
                self.logger.info(f"[BYPASS] Enhancement disabled and no services require JSON processing. Using direct file copy for: {identifier}")
                # Create a minimal story object that signals direct copy mode
                return {
                    "metadata": {"source_path": os.path.join(self.settings.input_dir, identifier)},
                    "bypass_mode": True,
                    "original_identifier": identifier
                }
            
            # Initialize variables
            original_heading_mode = self.settings.heading_mode
            
            # Only perform auto-mode detection and summary generation if enhancement is enabled
            if self.settings.enable_enhancement:
                # Auto-detect heading mode based on document size
                document_size = self._calculate_document_size(story)
                
                if document_size > 40000:
                    self.logger.info(f"[AUTO-MODE] Document size: {document_size} chars")
                    self.settings.heading_mode = True
                else:
                    self.logger.info(f"[AUTO-MODE] Document size: ({document_size} chars")
                    self.settings.heading_mode = False
                
                # Generate summary and fetch RAG context based on mode
                if self.settings.heading_mode:
                    document_summary = self.summarizer_service.summarize_document(story.get("headings", []))
                    self.logger.info("[SUMMARY] Document summary generated")
                    # Log detailed summary to debug only
                    self.logger.debug("Document Summary:")
                    self.logger.debug("=" * 80)
                    self.logger.debug(document_summary)
                    self.logger.debug("=" * 80)
                    
                    # Fetch RAG context for heading mode too
                    self.logger.info("[RAG] Fetching context for heading-wise processing...")
                    rag_chunks = self._fetch_rag_context(story)
                else:
                    document_summary = ""  # No summary needed for complete document processing
                    rag_chunks = ""  # RAG will be fetched in _process_complete_document
                    self.logger.info("[MODE] Non-heading mode: Processing complete document")
            else:
                # Enhancement disabled - skip summary and heading mode detection
                self.logger.info("Enhancement disabled, returning original document")
                document_summary = ""
                rag_chunks = ""

            # Process based on heading mode setting (only if enhancement is enabled)
            if self.settings.enable_enhancement and self.settings.heading_mode and "headings" in story:
                # Heading mode: process individual headings
                if self.settings.enable_parallel_processing:
                    # Process headings in parallel
                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=self.settings.max_parallel_workers
                    ) as executor:
                        # Create tasks for each heading
                        future_to_heading = {
                            executor.submit(
                                self._process_heading, 
                                heading, 
                                story, 
                                rag_chunks,
                                document_summary
                            ): heading 
                            for heading in story["headings"]
                        }
                        
                        # Collect results in order
                        processed_headings = []
                        for future in concurrent.futures.as_completed(future_to_heading):
                            try:
                                processed_heading = future.result()
                                processed_headings.append(processed_heading)
                            except Exception as e:
                                heading = future_to_heading[future]
                                self.logger.error(f"Error processing heading {heading.get('heading_id', 'unknown')}: {str(e)}")
                                processed_headings.append(heading)  # Keep original on error
                        
                        # Sort headings back to original order
                        processed_headings.sort(key=lambda h: h.get("position", 0))
                        story["headings"] = processed_headings
                else:
                    # Process headings sequentially
                    processed_headings = []
                    for heading in story["headings"]:
                        processed_heading = self._process_heading(heading, story, rag_chunks, document_summary)
                        processed_headings.append(processed_heading)
                    story["headings"] = processed_headings
            elif self.settings.enable_enhancement and not self.settings.heading_mode:
                # Non-heading mode: process complete document
                story = self._process_complete_document(story, identifier)
            elif self.settings.enable_enhancement:
                self.logger.warning("No headings found in story for heading mode processing")

            # Restore original heading mode setting (only if enhancement was enabled)
            if self.settings.enable_enhancement:
                self.settings.heading_mode = original_heading_mode
            
            # Process additional services if any are enabled (regardless of enhancement setting)
            if any([
                self.settings.testcasegeneration and self.testcase_generation_service,
                self.settings.validatoranddebugger and self.validator_service,
                self.settings.failed_testcases_regenerator and self.failed_testcases_regeneration_service,
                self.settings.testcases_accuracy and self.accuracy_measure_service
            ]):
                # For services, we need RAG chunks regardless of enhancement mode
                if self.settings.enable_enhancement and self.settings.heading_mode:
                    # Use RAG chunks already fetched during enhancement
                    self._process_additional_services(story, rag_chunks, identifier)
                else:
                    # Fetch RAG chunks for services when enhancement is disabled or non-heading mode
                    rag_chunks_for_additional = self._fetch_rag_context(story)
                    self._process_additional_services(story, rag_chunks_for_additional, identifier)
            
            return story

        except Exception as e:
            # Restore original heading mode setting on error
            self.settings.heading_mode = original_heading_mode
            self.logger.exception(f"Error processing document {identifier}: {str(e)}")
            return None

    def process_document(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Process a single document, either with enhancement or just plain text conversion.

        Args:
            identifier (str): The name/identifier of the document to process.

        Returns:
            Optional[Dict[str, Any]]: The processed story data, or None if processing fails.
        """
        try:
            # Check if we should bypass parsing completely
            if self._should_bypass_parsing():
                self.logger.info(f"[BYPASS] Skipping document parsing for: {identifier}")
                # Return the bypass story object directly
                return {
                    "metadata": {"source_path": os.path.join(self.settings.input_dir, identifier)},
                    "bypass_mode": True,
                    "original_identifier": identifier
                }
            
            # Parse the document
            story = self.file_service.parse_document(identifier)
            if not story:
                self.logger.error(f"Failed to parse document: {identifier}")
                return None

            # Process the story using the new process_story method
            return self.process_story(story, identifier)

        except Exception as e:
            self.logger.exception(f"Error processing document {identifier}: {str(e)}")
            return None

    def process_documents(self) -> None:
        """
        Process all documents in the input directory.
        """
        self.logger.info("[PROCESS] Starting document processing...")
        
        # Get list of documents to process
        documents = self.file_service.get_inputs()
        if not documents:
            self.logger.warning("No documents found to process.")
            return
            
        self.logger.info(f"[PROCESS] Found {len(documents)} documents to process.")
        
        for doc in documents:
            self.logger.info(f"[PROCESS] Processing: {doc}")
            
            try:
                # Check cache first
                cache_key = doc
                if self.settings.enable_enhancement:
                    cached_state = cache_manager.get(cache_key)
                    if cached_state:
                        self.logger.info(f"[CACHE] Resuming from cached state for: {doc}")
                        story = cached_state
                    else:
                        self.logger.info(f"[CACHE] No cached state found. Starting new process for: {doc}")
                        story = self.process_document(doc)
                else:
                    self.logger.info(f"[PROCESS] Processing without enhancement: {doc}")
                    story = self.process_document(doc)
                
                if story:
                    # Save results
                    base_name = os.path.splitext(doc)[0]
                    self.file_service.save_results(story, base_name)
                else:
                    self.logger.error(f"[PROCESS] Failed to process document: {doc}")
                    
            except Exception as e:
                self.logger.exception(f"[PROCESS] Error processing document {doc}: {str(e)}")
                continue
