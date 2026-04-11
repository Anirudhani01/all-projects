import os
import json
import logging
from typing import List, Dict, Any, Optional
from common.settings import Settings
from parser.parser import BaseParser, DocxParser
from parser.jira_parser import JiraParser
from story_enhancer.writer import DocumentWriter, JiraWriter

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

        # Select writer based on settings
        if self.settings.enable_jira_output:
            self.jira_writer = JiraWriter()
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
        Save the processed story results to files.
        
        Args:
            story (Dict[str, Any]): The processed story data
            base_name (str): Base name for output files
        """
        # Handle bypass mode - direct file copy without processing
        if story.get("bypass_mode", False):
            self._handle_direct_file_copy(story, base_name)
            return
        
        # Handle Jira output if enabled
        if self.settings.enable_jira_output:
            self._save_to_jira(story, base_name)
            return  # Only save to Jira, skip file outputs
        
        # Continue with regular file outputs
        # Save enhanced story as JSON (if enabled)
        if self.settings.enable_enhanced_json:
            json_path = os.path.join(self.output_dir, f"enhanced_{base_name}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(story, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved enhanced story JSON to: {json_path}")
        
        # Save enhanced story as text (if enabled)
        if self.settings.enable_enhanced_txt:
            txt_path = os.path.join(self.output_dir, f"enhanced_{base_name}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                # Write document summary if available
                if "document_summary" in story:
                    f.write("Document Summary\n")
                    f.write("=" * 80 + "\n")
                    f.write(story["document_summary"])
                    f.write("\n" + "=" * 80 + "\n\n")
                
                # Process each heading
                for heading in story.get("headings", []):
                    heading_id = heading.get("heading_id", "Unknown")
                    title = heading.get("title", "Untitled")
                    
                    f.write(f"Heading: {title} (ID: {heading_id})\n")
                    f.write("=" * 80 + "\n\n")
                    
                    # Write original content
                    f.write("Original Content:\n")
                    f.write("-" * 40 + "\n")
                    content = heading.get("content", [])
                    if isinstance(content, list):
                        content = "\n".join(str(item) for item in content)
                    f.write(content)
                    f.write("\n\n")
                    
                    # Write checker feedback
                    if "checker_feedback" in heading:
                        f.write("Checker Feedback:\n")
                        f.write("-" * 40 + "\n")
                        feedback = heading["checker_feedback"]
                        f.write(f"Rating: {feedback.get('rating', 'Not provided')}\n")
                        f.write(f"Reason: {feedback.get('reason', 'Not provided')}\n")
                        if "suggestions" in feedback:
                            f.write("\nSuggested Improvements:\n")
                            for idx, suggestion in enumerate(feedback["suggestions"], 1):
                                f.write(f"{idx}. {suggestion}\n")
                        f.write("\n")
                    
                    # Write enhancement changes
                    if "changes_made" in heading:
                        f.write("Enhancement Changes:\n")
                        f.write("-" * 40 + "\n")
                        changes = heading["changes_made"]
                        if changes:
                            for idx, change in enumerate(changes, 1):
                                f.write(f"{idx}. {change}\n")
                        else:
                            f.write("No changes made to this heading.\n")
                        f.write("\n")
                    
                    # Write enhanced content
                    if "enhanced_content" in heading:
                        f.write("Enhanced Content:\n")
                        f.write("-" * 40 + "\n")
                        enhanced_content = heading["enhanced_content"]
                        if isinstance(enhanced_content, list):
                            enhanced_content = "\n".join(str(item) for item in enhanced_content)
                        f.write(enhanced_content)
                        f.write("\n")
                    
                    f.write("\n" + "=" * 80 + "\n\n")
            
            self.logger.info(f"Saved enhanced story text to: {txt_path}")
        
        # Save enhancement log if configured
        if hasattr(self.settings, 'save_enhancement_log') and self.settings.save_enhancement_log:
            log_path = os.path.join(self.output_dir, f"enhancement_log_{base_name}.txt")
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("Enhancement Process Log\n")
                f.write("=" * 80 + "\n\n")
                
                for heading in story.get("headings", []):
                    heading_id = heading.get("heading_id", "Unknown")
                    title = heading.get("title", "Untitled")
                    
                    f.write(f"Heading: {title} (ID: {heading_id})\n")
                    f.write("-" * 40 + "\n")
                    
                    if "enhancement_status" in heading:
                        status = heading["enhancement_status"]
                        f.write(f"Status: {status.get('status', 'Unknown')}\n")
                        if "reason" in status:
                            f.write(f"Reason: {status['reason']}\n")
                        if "changes" in status and status["changes"]:
                            f.write("\nChanges Made:\n")
                            for idx, change in enumerate(status["changes"], 1):
                                f.write(f"{idx}. {change}\n")
                    else:
                        f.write("No enhancement status available.\n")
                    
                    f.write("\n" + "=" * 80 + "\n\n")
            
            self.logger.info(f"Saved enhancement log to: {log_path}")
        
        # Save as DOCX if configured
        if self.settings.enable_docx_output:
            # Use "enhanced_" prefix only if enhancement is enabled
            if hasattr(self.settings, 'enable_enhancement') and self.settings.enable_enhancement:
                docx_path = os.path.join(self.output_dir, f"enhanced_{base_name}.docx")
                log_message = f"Saved enhanced story DOCX to: {docx_path}"
            else:
                docx_path = os.path.join(self.output_dir, f"{base_name}.docx")
                log_message = f"Saved story DOCX to: {docx_path}"
            
            self.writer.create_docx(story, docx_path)
            self.logger.info(log_message)
    
    def _handle_direct_file_copy(self, story: Dict[str, Any], base_name: str) -> None:
        """
        Handle direct file copy without processing when in bypass mode.
        
        Args:
            story (Dict[str, Any]): The story data containing source path info
            base_name (str): Base name for output files
        """
        import shutil
        
        source_path = story.get("metadata", {}).get("source_path")
        if not source_path or not os.path.exists(source_path):
            self.logger.error(f"[BYPASS] Source file not found: {source_path}")
            return
        
        # Only copy DOCX files if DOCX output is enabled
        if self.settings.enable_docx_output:
            output_path = os.path.join(self.output_dir, f"{base_name}.docx")
            try:
                shutil.copy2(source_path, output_path)
                self.logger.info(f"[BYPASS] Copied original document to: {output_path}")
            except Exception as e:
                self.logger.error(f"[BYPASS] Error copying file: {str(e)}")
        else:
            self.logger.info("[BYPASS] DOCX output disabled, skipping direct file copy")
    
    def _save_to_jira(self, story: Dict[str, Any], base_name: str) -> None:
        """
        Save the processed story to Jira as an issue.
        
        Args:
            story (Dict[str, Any]): The processed story data
            base_name (str): Base name (issue key if updating existing issue)
        """
        if not hasattr(self, 'jira_writer'):
            self.logger.error("JiraWriter not initialized - cannot save to Jira")
            return
        
        # If base_name looks like a Jira issue key (e.g., KAN-23), update existing issue
        if self.settings.parser_type == "JIRA" and base_name:
            # Update existing issue
            self.jira_writer.create_or_update_issue(story, issue_key=base_name)
        else:
            # Create new issue
            self.jira_writer.create_or_update_issue(story)
