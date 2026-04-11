import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Base paths - point to project root (two levels up from components/common)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
DOCUMENTS_DIR = BASE_DIR / "documents"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [INPUT_DIR, OUTPUT_DIR, DOCUMENTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# Processing settings
ENABLE_ENHANCEMENT = os.getenv("ENABLE_ENHANCEMENT", "true").lower() == "true"
ENABLE_PARALLEL_PROCESSING = os.getenv("ENABLE_PARALLEL_PROCESSING", "true").lower() == "true"
MAX_PARALLEL_WORKERS = int(os.getenv("MAX_PARALLEL_WORKERS", "4").split()[0])

# Enhancement tracking settings
SAVE_ENHANCEMENT_LOG = os.getenv("SAVE_ENHANCEMENT_LOG", "true").lower() == "true"
ENHANCEMENT_LOG_FILE = "enhancement_log.txt"

# Document processing settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Cache settings
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
CACHE_DIR = BASE_DIR / "cache"
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default

# Create cache directory if enabled
if ENABLE_CACHE:
    CACHE_DIR.mkdir(exist_ok=True)


class Settings:
    """
    A class to manage settings for the application.
    
    This class loads environment variables from a .env file and sets them as attributes.
    It provides default values for some settings if they are not found in the environment variables.
    """
    def __init__(self):
        """
        Initializes the Settings class.

        This method loads environment variables from a .env file, sets up attributes for the application settings,
        and creates the output directory if it doesn't exist.
        """
        load_dotenv()
        self.model_name: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.domain: str = os.getenv("DOMAIN")
        self.max_attempts: int = int(os.getenv("MAX_ATTEMPTS", "3"))
        # Retry settings for transient errors inside a single workflow step
        self.max_step_retries: int = int(os.getenv("MAX_STEP_RETRIES", "3"))
        self.retry_backoff_seconds: int = int(os.getenv("RETRY_BACKOFF_SECONDS", "5"))

        # Enable experimental heading-wise processing pipeline
        self.heading_mode: bool = os.getenv("HEADING_MODE", "true").lower() == "true"

        
        # Feature flags for enhancement and parallel processing
        self.enable_enhancement: bool = os.getenv("ENABLE_ENHANCEMENT", "true").lower() == "true"
        self.enable_parallel_processing: bool = os.getenv("ENABLE_PARALLEL_PROCESSING", "false").lower() == "true"
        self.max_parallel_workers: int = int(os.getenv("MAX_PARALLEL_WORKERS", "4").split()[0])
        
        # Enhancement tracking settings
        self.save_enhancement_log: bool = os.getenv("SAVE_ENHANCEMENT_LOG", "false").lower() == "true"
        self.enhancement_log_file: str = os.getenv("ENHANCEMENT_LOG_FILE", "enhancement_log.txt")
        
        self.input_dir: str = os.getenv("INPUT_DIR", "input")
        self.output_dir: str = os.getenv("OUTPUT_DIR", "output")
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.enable_graph_png: bool = os.getenv("ENABLE_GRAPH_PNG", "false").lower() == "true"
        # Parser/Writer selection
        self.parser_type: str = os.getenv("PARSER_TYPE", "DOCX").upper()  # DOCX or JIRA
        self.enable_docx_output: bool = os.getenv("ENABLE_DOCX_OUTPUT", "true").lower() == "true"
        self.enable_jira_output: bool = os.getenv("ENABLE_JIRA_OUTPUT", "false").lower() == "true"

        # JIRA integration settings
        self.jira_url: Optional[str] = os.getenv("JIRA_URL")
        self.jira_email: Optional[str] = os.getenv("JIRA_EMAIL")
        self.jira_api_token: Optional[str] = os.getenv("JIRA_API_TOKEN")
        # Optional comma-separated list of issue keys to process when using JiraParser
        self.jira_issues: list[str] = [k.strip() for k in os.getenv("JIRA_ISSUES", "").split(",") if k.strip()]
        self.redis_host: Optional[str] = os.getenv("REDIS_HOST")
        self.redis_port: Optional[int] = int(os.getenv("REDIS_PORT", "6379")) if os.getenv("REDIS_HOST") else None
        self.redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")

        # New service configuration flags
        self.testcasegeneration: bool = os.getenv("TESTCASEGENERATION", "false").lower() == "true"
        self.validatoranddebugger: bool = os.getenv("VALIDATORANDDEBUGGER", "false").lower() == "true"
        self.failed_testcases_regenerator: bool = os.getenv("FAILED_TESTCASES_REGENERATOR", "false").lower() == "true"
        self.testcases_accuracy: bool = os.getenv("TESTCASES_ACCURACY", "false").lower() == "true"
        
        # Test case processing configuration
        self.test_case_chunk_size: int = int(os.getenv("TEST_CASE_CHUNK_SIZE", "20"))
        self.validation_iteration_count: int = int(os.getenv("VALIDATION_ITERATION_COUNT", "1"))
        self.enable_testcase_docx: bool = os.getenv("ENABLE_TESTCASE_DOCX", "false").lower() == "true"
        
        # Output file configuration flags
        self.enable_enhanced_json: bool = os.getenv("ENABLE_ENHANCED_JSON", "false").lower() == "true"
        self.enable_enhanced_txt: bool = os.getenv("ENABLE_ENHANCED_TXT", "false").lower() == "true"
        self.enable_enhancement_log: bool = os.getenv("ENABLE_ENHANCEMENT_LOG", "false").lower() == "true"
        
        # File naming configuration
        self.base_filename: str = os.getenv("BASE_FILENAME", "processed_story")

        os.makedirs(self.output_dir, exist_ok=True)

