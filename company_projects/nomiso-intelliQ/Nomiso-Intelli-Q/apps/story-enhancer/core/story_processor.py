import os
import logging
from typing import List, Optional
from datetime import datetime
from config.settings import Settings
from core.llm_client import LLMClient
from core.workflow_manager import WorkflowManager
from services.rag_service import RAGService
from services.checker_service import CheckerService
from services.enhancer_service import EnhancerService
from services.file_service import FileService
from models.story_state import StoryState
from utils.cache_manager import cache_manager
import concurrent.futures


class StoryProcessor:
    """
    A class to process stories from documents.

    This class orchestrates the entire story processing workflow, including setting up logging,
    initializing services, and processing documents individually or in parallel.
    It manages dependencies and coordinates the different components of the system.
    """
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initializes the StoryProcessor.

        Args:
            settings (Optional[Settings]): A Settings object containing application configuration.
                                           If not provided, a new one will be created.
        """
        self.settings = settings or Settings()
        self._setup_logging()
        self._initialize_services()
    
    def _setup_logging(self):
        """
        Configure logging to both console and file.

        This method sets up a logging system that writes logs to both the console and a timestamped
        log file in the 'logs' directory. It ensures that the root logger is configured correctly.
        """
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"story_processor_{timestamp}.log")

        # Get root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Clear existing handlers to avoid duplicate logs
        if logger.hasHandlers():
            logger.handlers.clear()

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Create formatter and add it to the handlers (remove logger name for cleaner output)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("[INIT] Logging initialized. Log file at: %s", log_file)
    
    def _initialize_services(self):
        """
        Initialize all services required for the story processing workflow.

        This method creates instances of all the necessary services, such as the LLM client,
        RAG service, checker service, enhancer service, and file service. It also initializes
        the workflow manager with these services.
        """
        self.logger.info("[INIT] Initializing core and business services...")

        # Choose parser implementation based on settings
        if self.settings.parser_type == "JIRA":
            from external.jira_parser import JiraParser
            parser_instance = JiraParser(self.settings)
        else:
            from external.parser import DocxParser
            parser_instance = DocxParser()

        # Core services
        self.llm_client = LLMClient(
            self.settings.openai_api_key or "",
            self.settings.model_name
        )
        self.logger.info("[SUCCESS] LLM Client initialized")
        
        # Business services
        self.rag_service = RAGService(parser_instance)
        self.checker_service = CheckerService(self.llm_client)
        self.enhancer_service = EnhancerService(self.llm_client)
        self.file_service = FileService(
            self.settings.input_dir,
            self.settings.output_dir,
            self.settings,
            parser_instance
        )
        self.logger.info("[SUCCESS] Domain services (RAG, Checker, Enhancer, File) initialized")
        
        # Workflow manager
        self.workflow_manager = WorkflowManager(
            self.rag_service,
            self.checker_service,
            self.enhancer_service,
            self.settings.max_attempts,
            self.settings.output_dir,
            self.settings.enable_graph_png,
            self.settings.max_step_retries,
            self.settings.retry_backoff_seconds
        )
        self.logger.info("[SUCCESS] Enhanced Pipeline initialized successfully")
    
    def process_single_document(self, filename: str) -> bool:
        """
        Process a single document from the input directory.

        This method handles the entire workflow for a single document, including parsing,
        state management (with caching), executing the processing workflow, and saving the results.

        Args:
            filename (str): The name of the file to be processed.

        Returns:
            bool: True if the document was processed successfully, False otherwise.
        """
        self.logger.info("[PROCESS] Processing: %s", filename)
        
        try:
            base_name = os.path.splitext(filename)[0]
            
            # Check for cached state
            initial_state = cache_manager.get(base_name)
            
            if initial_state:
                self.logger.info("[CACHE] Resuming from cached state for: %s", filename)
            else:
                self.logger.info("[CACHE] No cached state found. Starting new process for: %s", filename)
                # Parse document
                parsed_story = self.file_service.parse_document(filename)
                
                # Create initial state
                initial_state = StoryState({
                    "story": parsed_story,
                    "attempts": 0,
                    "cache_key": base_name
                })
            
            # Execute workflow
            result = self.workflow_manager.execute(initial_state)
            
            # Save results
            final_story = result.get("story")
            if final_story:
                base_name = os.path.splitext(filename)[0]
                self.file_service.save_results(final_story, base_name)
            
                # Clean up cache on successful completion
                if cache_manager.is_redis:
                    cache_manager.delete(base_name)
                    self.logger.info("[CACHE] Removed cached state for completed process: %s", filename)
            else:
                self.logger.error("[WORKFLOW] Workflow finished for %s but no story was produced.", filename)

            return True
            
        except Exception as e:
            self.logger.exception("[PROCESS] Failed to process %s", filename)
            return False
    

    def process_all_documents(self) -> None:
        """
        Process all .docx documents in the input directory in parallel.

        This method discovers all .docx files in the configured input directory and processes them
        concurrently using a thread pool. It logs the overall progress and success rate.
        """
        inputs = self.file_service.get_inputs()
        
        if not inputs:
            self.logger.warning("[PROCESS] No input items found to process.")
            return

        success_count = 0
        total = len(inputs)

        self.logger.info("[PROCESS] Starting parallel processing of %s documents...", total)

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, total)) as executor:
            futures = {executor.submit(self.process_single_document, identifier): identifier for identifier in inputs}

            for future in concurrent.futures.as_completed(futures):
                identifier = futures[future]
                try:
                    if future.result():
                        success_count += 1
                except Exception:
                    self.logger.exception(f"Exception occurred while processing {identifier}")

        self.logger.info("[PROCESS] Successfully processed %s/%s documents", success_count, total)
