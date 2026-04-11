"""
Test Context Management

Manages test execution context including environment settings, credentials,
and configuration parameters. This replaces passing individual parameters
and improves security by centralizing sensitive data handling.
"""

import os
from typing import Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field
import logging


@dataclass
class TestContext:
    """
    Encapsulates all test execution context and configuration.
    
    This class centralizes test configuration management and provides
    secure handling of sensitive data like credentials.
    """
    
    # Environment settings
    base_url: str = ""
    test_framework: str = "selenium"
    application_profile: str = "dynamic"
    
    # Timeouts and waits
    element_wait_timeout: int = 10
    page_load_timeout: int = 30
    step_wait_time: int = 1
    execution_timeout: int = 120
    
    # Directory paths
    screenshots_dir: str = "screenshots"
    scripts_dir: str = "scripts"
    reports_dir: str = "reports"
    logs_dir: str = "logs"
    
    # LLM configuration
    api_key: str = ""
    model_name: str = ""
    
    # Locator configuration
    locator_extraction_mode: str = "dynamic"  # Best default: dynamic locator generation
    locators: Dict[str, Any] = field(default_factory=dict)
    
    # Application-specific settings
    application_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization to load environment variables and validate settings."""
        self._load_from_environment()
        self._create_directories()
        self._validate_required_settings()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # Core settings
        self.base_url = os.getenv('BASE_URL', self.base_url)
        self.test_framework = os.getenv('TEST_FRAMEWORK', self.test_framework)
        # application_profile is set to best default: dynamic
        
        # Timeouts
        self.element_wait_timeout = int(os.getenv('DEFAULT_TIMEOUT', self.element_wait_timeout))
        self.page_load_timeout = int(os.getenv('PAGE_LOAD_TIMEOUT', self.page_load_timeout))
        self.step_wait_time = int(os.getenv('STEP_WAIT_TIME', self.step_wait_time))
        self.execution_timeout = int(os.getenv('EXECUTION_TIMEOUT', self.execution_timeout))
        
        # Directory paths
        self.screenshots_dir = os.getenv('SCREENSHOTS_DIRECTORY', self.screenshots_dir)
        self.scripts_dir = os.getenv('SCRIPTS_DIRECTORY', self.scripts_dir)
        self.reports_dir = os.getenv('REPORTS_DIRECTORY', self.reports_dir)
        self.logs_dir = os.getenv('LOGS_DIRECTORY', self.logs_dir)
        
        # LLM settings
        self.api_key = os.getenv('OPENAI_API_KEY', self.api_key)
        self.model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # Default fallback only
        
        # locator_extraction_mode is set to best default: dynamic
    
    def _create_directories(self) -> None:
        """Create necessary directories for test execution."""
        directories = [
            self.screenshots_dir,
            self.scripts_dir, 
            self.reports_dir,
            self.logs_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def _validate_required_settings(self) -> None:
        """Validate that required settings are present."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if not self.base_url:
            raise ValueError("BASE_URL environment variable is required")
        
        if self.test_framework not in ['selenium', 'appium']:
            raise ValueError(f"Unsupported test framework: {self.test_framework}")
    
    def get_credentials(self) -> Dict[str, str]:
        """
        Get credentials from secure sources (environment variables only).
        
        Returns:
            Dict[str, str]: Dictionary containing credentials
        """
        return {
            'username': os.getenv('APP_USERNAME', ''),
            'password': os.getenv('APP_PASSWORD', '')
        }
    
    def get_script_path(self, test_case_id: str) -> Path:
        """
        Get the full path for a test script file.
        
        Args:
            test_case_id (str): Test case identifier
            
        Returns:
            Path: Full path to the script file
        """
        script_filename = f"test_{test_case_id.lower().replace('-', '_').replace(' ', '_')}.py"
        return Path(self.scripts_dir) / script_filename
    
    def get_screenshot_path(self, test_case_id: str, step_name: str) -> Path:
        """
        Get the full path for a screenshot file.
        
        Args:
            test_case_id (str): Test case identifier
            step_name (str): Name of the test step
            
        Returns:
            Path: Full path to the screenshot file
        """
        screenshot_filename = f"{test_case_id}_{step_name}.png"
        return Path(self.screenshots_dir) / screenshot_filename
    
    def get_report_path(self, timestamp: str) -> Path:
        """
        Get the full path for a test report file.
        
        Args:
            timestamp (str): Timestamp for the report
            
        Returns:
            Path: Full path to the report file
        """
        report_filename = f"test_report_{timestamp}.json"
        return Path(self.reports_dir) / report_filename
    
    def update_locators(self, locators: Dict[str, Any]) -> None:
        """
        Update the locators configuration.
        
        Args:
            locators (Dict[str, Any]): New locators to use
        """
        self.locators = locators
    
    def get_application_setting(self, key: str, default: Any = None) -> Any:
        """
        Get an application-specific setting.
        
        Args:
            key (str): Setting key
            default (Any): Default value if key not found
            
        Returns:
            Any: Setting value or default
        """
        return self.application_settings.get(key, default)
    
    def set_application_setting(self, key: str, value: Any) -> None:
        """
        Set an application-specific setting.
        
        Args:
            key (str): Setting key
            value (Any): Setting value
        """
        self.application_settings[key] = value
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """
        Get a configured logger instance.
        
        Args:
            name (str): Logger name (optional)
            
        Returns:
            logging.Logger: Configured logger
        """
        logger_name = name or __name__
        logger = logging.getLogger(logger_name)
        
        if not logger.handlers:
            # Create logs directory if it doesn't exist
            Path(self.logs_dir).mkdir(exist_ok=True)
            
            # Set up file handler
            log_file = Path(self.logs_dir) / "test_framework.log"
            file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            
            # Set up console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers to logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            logger.setLevel(logging.DEBUG)
        
        return logger
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary (excluding sensitive data).
        
        Returns:
            Dict[str, Any]: Context as dictionary
        """
        return {
            'base_url': self.base_url,
            'test_framework': self.test_framework,
            'element_wait_timeout': self.element_wait_timeout,
            'page_load_timeout': self.page_load_timeout,
            'step_wait_time': self.step_wait_time,
            'execution_timeout': self.execution_timeout,
            'screenshots_dir': self.screenshots_dir,
            'scripts_dir': self.scripts_dir,
            'reports_dir': self.reports_dir,
            'logs_dir': self.logs_dir,
            'model_name': self.model_name,
            'application_settings': self.application_settings
        }