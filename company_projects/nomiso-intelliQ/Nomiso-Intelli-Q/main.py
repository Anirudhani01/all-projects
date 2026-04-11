import os
import logging
from components.common.settings import Settings
from components.common.logging_config import setup_centralized_logging, cleanup_old_logs
from components.common.story_processor import StoryProcessor
from components.common.llm_client import LLMClient
from components.common.workflow_manager import WorkflowManager
from components.story_enhancer.checker_service import CheckerService
from components.story_enhancer.enhancer_service import EnhancerService
from components.common.rag_service import RAGService
from components.story_enhancer.summarizer_service import SummarizerService
from components.common.file_service import FileService
from components.story_validator.validator_service import ValidatorService
from components.story_validator.failed_testcases_regeneration_service import FailedTestCasesRegenerationService
from components.story_validator.accuracy_measure_service import MeasureAccuracyService
from components.test_case_generator.pipeline import TestCasePipeline
from components.story_enhancer.testcase_docx_generator_service import TestCaseDocxGeneratorService
from components.story_enhancer.structured_story_conversion_service import structuredstoryfortestcaseService
from components.parser.parser import DocxParser
from components.parser.jira_parser import JiraParser
from dotenv import load_dotenv
import os
import json

def _replace_failed_test_cases(original_test_cases, validation_data, regeneration_result):
    """
    Replace failed test cases with regenerated ones using test case IDs.
    
    Args:
        original_test_cases: Original list of test cases with IDs
        validation_data: Validation results indicating which cases failed (by ID)
        regeneration_result: Regenerated test cases for failed ones
    
    Returns:
        Updated list of test cases with failed cases replaced
    """
    updated_test_cases = original_test_cases.copy()
    
    # Create a mapping of test case ID to index for quick lookup
    id_to_index = {}
    for i, test_case in enumerate(updated_test_cases):
        if isinstance(test_case, dict):
            # Look for ID in various possible fields
            test_case_id = test_case.get('id') or test_case.get('test_case_id') or test_case.get('testcase_id')
            if test_case_id:
                id_to_index[test_case_id] = i
    
    # Extract failed test case IDs from validation data
    failed_test_case_ids = []
    if isinstance(validation_data, dict) and "validated_test_cases" in validation_data:
        for case in validation_data["validated_test_cases"]:
            if isinstance(case, dict) and case.get("validation_passed") == False:
                # Look for ID in various possible fields
                test_case_id = case.get('id') or case.get('test_case_id') or case.get('testcase_id')
                if test_case_id:
                    failed_test_case_ids.append(test_case_id)
    
    # Extract regenerated test cases
    regenerated_cases = []
    if isinstance(regeneration_result, dict) and "test_cases" in regeneration_result:
        regenerated_cases = regeneration_result["test_cases"]
    elif isinstance(regeneration_result, list):
        regenerated_cases = regeneration_result
    
    # Replace failed test cases with regenerated ones using IDs
    import logging
    logger = logging.getLogger(__name__)
    
    regenerated_index = 0
    replaced_ids = []
    
    for failed_id in failed_test_case_ids:
        if failed_id in id_to_index and regenerated_index < len(regenerated_cases):
            original_index = id_to_index[failed_id]
            regenerated_case = regenerated_cases[regenerated_index].copy()
            
            # Preserve the original ID in the regenerated case
            # Use the same ID field that was found in the original test case
            original_test_case = updated_test_cases[original_index]
            if 'test_case_id' in original_test_case:
                regenerated_case['test_case_id'] = failed_id
            elif 'id' in original_test_case:
                regenerated_case['id'] = failed_id
            else:
                regenerated_case['testcase_id'] = failed_id
            
            # Replace the failed test case
            updated_test_cases[original_index] = regenerated_case
            replaced_ids.append(failed_id)
            regenerated_index += 1
    
    if replaced_ids:
        logger.info(f"Replaced test cases with IDs: {', '.join(replaced_ids)}")
    
    return updated_test_cases

def _get_current_timestamp():
    """Get current timestamp in ISO format"""
    from datetime import datetime
    return datetime.now().isoformat()

# Load environment variables from the .env file
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(env_path)
openai_api_key = os.getenv("OPENAI_API_KEY")


def main():
    # Initialize settings
    settings = Settings()

    # Set up centralized logging with date-wise log files
    setup_centralized_logging()
    
    # Clean up old log files (older than 7 days)
    cleanup_old_logs(days_to_keep=7)
    
    # Get logger for main module
    logger = logging.getLogger(__name__)

    try:
        # Validate OpenAI API key
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not found in settings")

        # Initialize LLM client with API key and model name from settings
        llm_client = LLMClient(
            api_key=settings.openai_api_key,
            model=settings.model_name
        )

        # Initialize parser based on settings
        if settings.parser_type == "JIRA":
            parser = JiraParser(settings)
        else:
            parser = DocxParser()

        # Initialize services
        checker_service = CheckerService(llm_client, settings)
        enhancer_service = EnhancerService(llm_client, settings)
        rag_service = RAGService(parser=parser)
        summarizer_service = SummarizerService(llm_client, settings)
        file_service = FileService(
            input_dir=settings.input_dir,
            output_dir=settings.output_dir,
            settings=settings
        )
        
        # Initialize new configurable services
        testcase_generation_service = None
        validator_service = None
        failed_testcases_regeneration_service = None
        accuracy_measure_service = None
        testcase_docx_generator_service = None
        
        # Ensure output directory exists
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Dynamic file names - look for input files to determine base filename
        input_dir = os.path.join(os.getcwd(), "input")
        base_filename = settings.base_filename
        
        # Look for input files (docx or other formats) in input directory
        if os.path.exists(input_dir):
            input_files = [f for f in os.listdir(input_dir) if f.endswith(('.docx', '.txt', '.json'))]
            if input_files:
                # Use the first found input file as base name (remove extension)
                input_file = input_files[0]
                base_filename = os.path.splitext(input_file)[0]  # Remove file extension
                logger.info(f"Found input file: {input_file}, using base filename: {base_filename}")
        
        # Check if structured text file already exists in output directory  
        structured_text_file = os.path.join(output_dir, f"{base_filename}_structured_text.json")
        
        input_file_path = structured_text_file
        output_file_path = os.path.join(output_dir, f"{base_filename}_testcases.json")

        # Load OpenAI API key from environment variables
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
                
        # Initialize services that will be used after test case generation
        if settings.testcasegeneration:
            testcase_generation_service = structuredstoryfortestcaseService(llm_client, settings)
            
        if settings.validatoranddebugger:
            validator_service = ValidatorService(llm_client, settings)
            
        if settings.failed_testcases_regenerator:
            failed_testcases_regeneration_service = FailedTestCasesRegenerationService(llm_client, settings)
            
        if settings.testcases_accuracy:
            accuracy_measure_service = MeasureAccuracyService(llm_client, settings)
            
        if settings.enable_testcase_docx:
            testcase_docx_generator_service = TestCaseDocxGeneratorService(settings)
            
        # Test case integration service not needed - using TestCasePipeline directly

        # Initialize workflow manager
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        workflow_manager = WorkflowManager(
            rag_service=rag_service,
            checker_service=checker_service,
            enhancer_service=enhancer_service,
            max_attempts=settings.max_attempts,
            output_dir=output_dir
        )

        # Initialize story processor with all required services
        processor = StoryProcessor(
            checker_service=checker_service,
            enhancer_service=enhancer_service,
            rag_service=rag_service,
            summarizer_service=summarizer_service,
            file_service=file_service,
            workflow_manager=workflow_manager,
            settings=settings,
            testcase_generation_service=testcase_generation_service,
            validator_service=validator_service,
            failed_testcases_regeneration_service=failed_testcases_regeneration_service,
            accuracy_measure_service=accuracy_measure_service,
            test_case_integration_service=None,
            testcase_docx_generator_service=testcase_docx_generator_service
        )

        # Process all documents
        processor.process_documents()
        logger.info("Document processing completed successfully")
        
        # Now generate test cases using the structured text file created by document processing
        # NOTE: Test case generation is now handled within StoryProcessor._process_additional_services
        # if settings.testcasegeneration and os.path.exists(input_file_path):
        #     logger.info("Starting test case generation...")
        #     
        #     # Initialize the test case pipeline
        #     pipeline = TestCasePipeline(document_path=input_file_path, api_key=openai_api_key, logger=logger)

        #     # Step 1: Load flows and business context from the input file
        #     flows, business_context = pipeline.load_input_file()

        #     # Step 2: Generate test cases for each flow using chunks and business context knowledge
        #     generated_test_cases = pipeline.generate_test_cases(flows, business_context)

        #     # Step 3: Save the generated test cases to a JSON file with metadata
        #     initial_test_cases_data = {
        #         "generated_test_cases": generated_test_cases,
        #         "test_case_metadata": {
        #             "total_test_cases": len(generated_test_cases),
        #             "test_case_ids": [tc.get('test_case_id') or tc.get('id') or tc.get('testcase_id') for tc in generated_test_cases],
        #             "generation_timestamp": _get_current_timestamp(),
        #             "contains_regenerated_cases": False
        #         }
        #     }
        #     
        #     with open(output_file_path, 'w', encoding='utf-8') as f:
        #         json.dump(initial_test_cases_data, f, indent=2, ensure_ascii=False)
        #     
        #     logger.info("Test case generation completed successfully")
        
        # NOTE: Validation and DOCX generation are now handled within StoryProcessor._process_additional_services()
        # The following code is commented out to avoid duplication:
        
        # if settings.validatoranddebugger and os.path.exists(output_file_path):
        #     logger.info("Starting multi-iteration validation pipeline...")
        #     # Validation logic moved to StoryProcessor
        # 
        # if settings.enable_testcase_docx and testcase_docx_generator_service:
        #     logger.info("Generating test cases DOCX...")
        #     # DOCX generation logic moved to StoryProcessor
        
        # NOTE: All validation and DOCX generation logic is now handled within StoryProcessor
        
        # elif settings.testcasegeneration:
        #     logger.warning(f"Test case generation enabled but structured text file not found: {input_file_path}")
        #     logger.info("Make sure document processing completed successfully first")
        
        logger.info("All processing completed successfully")

    except Exception as e:
        logger.exception(f"Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    main()