"""
Script Writer Module

Handles writing and managing test script files. This module is extracted from
the TestExecutor to follow single responsibility principle - TestExecutor
should only handle test execution, not file operations.
"""

import logging
from pathlib import Path
from typing import Optional
from .test_context import TestContext


class ScriptWriter:
    """
    Handles writing test scripts to the filesystem.
    
    This class is responsible for all file writing operations related to
    test scripts, including validation, formatting, and error handling.
    """
    
    def __init__(self, context: TestContext, logger: logging.Logger = None):
        """
        Initialize the script writer.
        
        Args:
            context (TestContext): Test execution context
            logger (logging.Logger): Logger instance for logging operations
        """
        self.context = context
        self.logger = logger or context.get_logger(__name__)
        self._ensure_scripts_directory()
    
    def _ensure_scripts_directory(self) -> None:
        """Ensure the scripts directory exists."""
        scripts_path = Path(self.context.scripts_dir)
        scripts_path.mkdir(exist_ok=True)
        self.logger.debug(f"Scripts directory ensured: {scripts_path}")
    
    def save_script(self, code: str, test_case_id: str) -> Path:
        """
        Save generated script code to a file.
        
        Args:
            code (str): The generated script code
            test_case_id (str): Test case identifier for filename
            
        Returns:
            Path: Path to the saved script file
            
        Raises:
            ValueError: If code is empty or test_case_id is invalid
            IOError: If file cannot be written
        """
        if not code or not code.strip():
            raise ValueError("Script code cannot be empty")
        
        if not test_case_id or not test_case_id.strip():
            raise ValueError("Test case ID cannot be empty")
        
        # Get the script path from context
        script_path = self.context.get_script_path(test_case_id)
        
        try:
            # Write the script code to file
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            self.logger.info(f"Script saved successfully: {script_path}")
            return script_path
            
        except Exception as e:
            self.logger.error(f"Failed to save script {script_path}: {str(e)}")
            raise IOError(f"Failed to save script: {str(e)}")
    
    def validate_script_syntax(self, code: str) -> bool:
        """
        Validate Python script syntax.
        
        Args:
            code (str): Script code to validate
            
        Returns:
            bool: True if syntax is valid, False otherwise
        """
        if not code or not code.strip():
            self.logger.warning("Empty script code provided for validation")
            return False
        
        try:
            compile(code, '<script>', 'exec')
            self.logger.debug("Script syntax validation passed")
            return True
        except SyntaxError as e:
            self.logger.error(f"Script syntax validation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during syntax validation: {e}")
            return False
    
    def read_script(self, script_path: Path) -> str:
        """
        Read script content from file.
        
        Args:
            script_path (Path): Path to the script file
            
        Returns:
            str: Script content
            
        Raises:
            FileNotFoundError: If script file doesn't exist
            IOError: If file cannot be read
        """
        if not script_path.exists():
            raise FileNotFoundError(f"Script file not found: {script_path}")
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.debug(f"Script read successfully: {script_path}")
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read script {script_path}: {str(e)}")
            raise IOError(f"Failed to read script: {str(e)}")
    
    def backup_script(self, script_path: Path) -> Path:
        """
        Create a backup of an existing script.
        
        Args:
            script_path (Path): Path to the script to backup
            
        Returns:
            Path: Path to the backup file
            
        Raises:
            FileNotFoundError: If original script doesn't exist
            IOError: If backup cannot be created
        """
        if not script_path.exists():
            raise FileNotFoundError(f"Original script not found: {script_path}")
        
        # Create backup filename with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = script_path.with_suffix(f'.backup_{timestamp}.py')
        
        try:
            # Read original and write backup
            original_content = self.read_script(script_path)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            self.logger.info(f"Script backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup {backup_path}: {str(e)}")
            raise IOError(f"Failed to create backup: {str(e)}")
    
    def delete_script(self, script_path: Path) -> bool:
        """
        Delete a script file.
        
        Args:
            script_path (Path): Path to the script to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            if script_path.exists():
                script_path.unlink()
                self.logger.info(f"Script deleted: {script_path}")
                return True
            else:
                self.logger.warning(f"Script file not found for deletion: {script_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete script {script_path}: {str(e)}")
            return False
    
    def list_scripts(self) -> list[Path]:
        """
        List all script files in the scripts directory.
        
        Returns:
            list[Path]: List of script file paths
        """
        scripts_path = Path(self.context.scripts_dir)
        
        if not scripts_path.exists():
            self.logger.warning(f"Scripts directory not found: {scripts_path}")
            return []
        
        try:
            script_files = list(scripts_path.glob('*.py'))
            self.logger.debug(f"Found {len(script_files)} script files")
            return script_files
            
        except Exception as e:
            self.logger.error(f"Failed to list scripts: {str(e)}")
            return []
    
    def get_script_info(self, script_path: Path) -> dict:
        """
        Get information about a script file.
        
        Args:
            script_path (Path): Path to the script file
            
        Returns:
            dict: Script information including size, modified time, etc.
        """
        if not script_path.exists():
            return {}
        
        try:
            stat = script_path.stat()
            return {
                'name': script_path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'is_valid': self.validate_script_syntax(self.read_script(script_path))
            }
        except Exception as e:
            self.logger.error(f"Failed to get script info for {script_path}: {str(e)}")
            return {}