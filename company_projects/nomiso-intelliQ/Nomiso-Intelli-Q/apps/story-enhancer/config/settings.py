import os
from typing import Optional
from dotenv import load_dotenv

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
        self.model_name: str = os.getenv("CHECKER_ENHENCER_MODEL", "gpt-4.1-mini")
        self.max_attempts: int = int(os.getenv("MAX_ATTEMPTS", "3"))
        # Retry settings for transient errors inside a single workflow step
        self.max_step_retries: int = int(os.getenv("MAX_STEP_RETRIES", "3"))
        self.retry_backoff_seconds: int = int(os.getenv("RETRY_BACKOFF_SECONDS", "5"))
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

        os.makedirs(self.output_dir, exist_ok=True)

