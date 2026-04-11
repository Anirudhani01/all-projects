import os
import json
import logging
from typing import List, Dict, Any, Optional
from config.settings import Settings
from external.parser import BaseParser, DocxParser
from external.jira_parser import JiraParser
from external.writer import DocumentWriter

class FileService:
    """
    A service for handling file operations, such as reading, parsing, and saving documents.

    This class provides a high-level interface for interacting with the file system,
    including finding, parsing, and saving story documents in different formats.
    """
    def __init__(self, input_dir: str, output_dir: str, settings: Optional[Settings] = None, parser: Optional[BaseParser] = None):
        """Initializes the FileService with configurable parser/writer."""

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)

        self.settings = settings or Settings()

        # Select parser implementation
        if parser is not None:
            self.parser = parser
        else:
            if self.settings.parser_type == "JIRA":
                self.parser = JiraParser(self.settings)
            else:
                self.parser = DocxParser()

        # Writer remains the same for now (DocumentWriter), but could be
        # extended later to JiraWriter etc.
        self.writer = DocumentWriter()
    
    def get_inputs(self) -> List[str]:
        """
        Get a list of all .docx files in the input directory.

        Returns:
            List[str]: A list of filenames for the .docx files found, or an empty
                       list if the directory is not found.
        """
        if self.settings.parser_type == "JIRA":
            if not self.settings.jira_issues:
                self.logger.warning("[JIRA PARSER] No JIRA_ISSUES provided in .env")
            return self.settings.jira_issues

        # Default DOCX discovery
        try:
            files = [f for f in os.listdir(self.input_dir) if f.lower().endswith(".docx")]
            return files
        except FileNotFoundError:
            self.logger.error(f"Input directory not found: {self.input_dir}")
            return []
    
    def parse_document(self, identifier: str) -> Dict[str, Any]:
        """
        Parse a document and return it as a structured dictionary.

        This method reads a document file, parses its content into a structured
        format, and adds metadata such as the source path.

        Args:
            identifier (str): The name of the file to parse.

        Returns:
            Dict[str, Any]: A dictionary representing the parsed story.
        """
        if self.settings.parser_type == "JIRA":
            # identifier is issue key
            parsed_story = self.parser.parse_document(identifier)
            # Ensure metadata is present
            if not isinstance(parsed_story, dict):
                parsed_story = {}  # fallback
            if "metadata" not in parsed_story:  # type: ignore[operator]
                parsed_story["metadata"] = {"source_path": identifier}  # type: ignore[index]
            return parsed_story

        # DOCX path
        input_path = os.path.join(self.input_dir, identifier)
        parsed_story = self.parser.parse_document(input_path)
        if not isinstance(parsed_story, dict):
            parsed_story = {}
        parsed_story["metadata"] = {"source_path": input_path}  # type: ignore[index]
        return parsed_story
    
    def save_results(self, story: Dict[str, Any], base_name: str) -> None:
        """
        Save the processed story to JSON and DOCX files, and optionally to JIRA.

        This method writes the structured story data to a JSON file, generates a
        new .docx file from it, and attempts to create a new JIRA issue with the story.

        Args:
            story (Dict[str, Any]): The story data to be saved.
            base_name (str): The base name to use for the output files.
        """
        # Save JSON (always)
        json_path = os.path.join(self.output_dir, f"enhanced_{base_name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(story, f, indent=2, ensure_ascii=False)
        self.logger.info(f"JSON saved to {json_path}")
        
        # Conditionally save DOCX
        if self.settings.enable_docx_output:
            docx_path = os.path.join(self.output_dir, f"enhanced_{base_name}.docx")
            self.writer.create_docx(story, docx_path)
            self.logger.info(f"DOCX saved to {docx_path}")
        
        # Conditionally create JIRA issue
        if self.settings.enable_jira_output:
            try:
                self.writer.create_jira_story(story)
                self.logger.info("Story uploaded to JIRA.")
            except Exception as jira_error:
                self.logger.warning(f"Could not upload story to JIRA: {jira_error}")
