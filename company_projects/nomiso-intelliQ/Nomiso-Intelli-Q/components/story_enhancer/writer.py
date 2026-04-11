import os
import requests
import json
import logging
from docx import Document
from docx.shared import Pt
from dotenv import load_dotenv
import re
from docx.oxml.ns import qn
from typing import Dict, Any, List

# Regular expression to match characters disallowed in XML 1.0 (except \t, \n, \r)
_INVALID_XML_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")

def _sanitize_text(text: str) -> str:
    """Remove characters that are not permitted in XML 1.0.

    This helper is defined at module level so it can be reused by multiple
    functions within this file.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    return _INVALID_XML_CHARS.sub("", text)

class JiraWriter:
    """Handles writing documents to JIRA issues"""
    
    def __init__(self):
        """Initialize JiraWriter with environment configuration"""
        load_dotenv()
        self.jira_url = os.getenv("JIRA_URL")
        self.email = os.getenv("JIRA_EMAIL") or os.getenv("EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN") or os.getenv("API_TOKEN")
        self.project_key = os.getenv("PROJECT_KEY") or os.getenv("JIRA_PROJECT_KEY")
        self.acceptance_criteria_field_id = os.getenv("ACCEPTANCE_CRITERIA_FIELD_ID")
        self.logger = logging.getLogger(__name__)
        
    def create_or_update_issue(self, story_data, issue_key=None):
        """
        Create a new JIRA issue or update an existing one with processed story data.
        
        Args:
            story_data (Dict[str, Any]): The processed story data
            issue_key (str, optional): If provided, update existing issue; otherwise create new
        """
        if not (self.jira_url and self.email and self.api_token and self.project_key):
            self.logger.warning("[JIRA WRITER] Missing Jira configuration – skipping issue creation/update.")
            return
            
        try:
            # Extract summary from story data
            summary = self._extract_summary_from_story(story_data)
            
            # Extract acceptance criteria if present
            acceptance_adf = self._extract_acceptance_criteria_adf(story_data)
            
            # Try to use custom field first, fall back to including in description
            use_custom_field = self.acceptance_criteria_field_id is not None
            
            if use_custom_field:
                # Convert story data to ADF format (without acceptance criteria)
                description_adf = self._convert_story_to_adf(self._remove_acceptance_criteria_from_story(story_data))
            else:
                # Convert story data to ADF format (with acceptance criteria included)
                description_adf = self._convert_story_to_adf(story_data)
            
            if issue_key:
                # Update existing issue
                success = self._update_issue(issue_key, summary, description_adf, acceptance_adf, use_custom_field)
                if not success and use_custom_field:
                    # Fallback: include acceptance criteria in description
                    self.logger.info("[JIRA WRITER] Retrying with acceptance criteria in description")
                    description_adf = self._convert_story_to_adf(story_data)
                    self._update_issue(issue_key, summary, description_adf, None, False)
            else:
                # Create new issue
                success = self._create_issue(summary, description_adf, acceptance_adf, use_custom_field)
                if not success and use_custom_field:
                    # Fallback: include acceptance criteria in description
                    self.logger.info("[JIRA WRITER] Retrying with acceptance criteria in description")
                    description_adf = self._convert_story_to_adf(story_data)
                    self._create_issue(summary, description_adf, None, False)
                
        except Exception:
            self.logger.exception("Exception during Jira issue creation/update")
    
    def _convert_story_to_adf(self, story_data):
        """Convert processed story data to ADF format"""
        # Use the existing convert_to_adf method from DocumentWriter
        writer = DocumentWriter()
        return writer.convert_to_adf(story_data)
    
    def _extract_summary_from_story(self, story_data):
        """Extract summary from story data"""
        # Check if there's a document summary
        if "document_summary" in story_data:
            return story_data["document_summary"][:255]  # Jira summary has 255 char limit
            
        # Look for title in headings or sections
        if "headings" in story_data and story_data["headings"]:
            return story_data["headings"][0].get("title", "Enhanced Story")[:255]
        elif "sections" in story_data and story_data["sections"]:
            return story_data["sections"][0].get("title", "Enhanced Story")[:255]
            
        return "Enhanced Story"
    
    def _extract_acceptance_criteria_adf(self, story_data):
        """Extract acceptance criteria from story data and convert to ADF"""
        # Look for acceptance criteria in headings or sections
        acceptance_section = None
        
        if "headings" in story_data:
            for heading in story_data["headings"]:
                if "acceptance criteria" in heading.get("title", "").lower():
                    acceptance_section = heading
                    break
        elif "sections" in story_data:
            for section in story_data["sections"]:
                if "acceptance criteria" in section.get("title", "").lower():
                    acceptance_section = section
                    break
        
        if acceptance_section:
            writer = DocumentWriter()
            return writer.convert_to_adf({"sections": [acceptance_section]})
        
        return None
    
    def _remove_acceptance_criteria_from_story(self, story_data):
        """Remove acceptance criteria sections from story data"""
        if not isinstance(story_data, dict):
            return story_data
            
        filtered_story = story_data.copy()
        if "sections" in filtered_story:
            filtered_sections = []
            for section in filtered_story["sections"]:
                if section.get("title", "").lower().find("acceptance criteria") == -1:
                    filtered_sections.append(section)
            filtered_story["sections"] = filtered_sections
        
        return filtered_story
    
    def _create_issue(self, summary, description_adf, acceptance_adf, use_custom_field=True):
        """Create a new JIRA issue"""
        self.logger.info("Creating new Jira issue: %s", summary)
        
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description_adf,
                "issuetype": {"name": "Story"}
            }
        }
        
        # Add acceptance criteria if available and field ID is configured
        if acceptance_adf and use_custom_field and self.acceptance_criteria_field_id:
            try:
                payload["fields"][self.acceptance_criteria_field_id] = acceptance_adf
                self.logger.info(f"[JIRA WRITER] Added acceptance criteria to custom field: {self.acceptance_criteria_field_id}")
            except Exception as e:
                self.logger.warning(f"[JIRA WRITER] Failed to add acceptance criteria to custom field {self.acceptance_criteria_field_id}: {e}")
                return False
        
        url = f"{self.jira_url}/rest/api/3/issue"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=(self.email, self.api_token)
        )
        
        if response.status_code == 201:
            issue_key = response.json()["key"]
            self.logger.info("Jira issue created: %s", issue_key)
            return True
        else:
            self.logger.error("Jira issue creation failed: %s %s", 
                            response.status_code, response.text)
            return False
    
    def _update_issue(self, issue_key, summary, description_adf, acceptance_adf, use_custom_field=True):
        """Update an existing JIRA issue"""
        self.logger.info("Updating Jira issue: %s", issue_key)
        
        payload = {
            "fields": {
                "summary": summary,
                "description": description_adf
            }
        }
        
        # Add acceptance criteria if available and field ID is configured
        if acceptance_adf and use_custom_field and self.acceptance_criteria_field_id:
            try:
                payload["fields"][self.acceptance_criteria_field_id] = acceptance_adf
                self.logger.info(f"[JIRA WRITER] Added acceptance criteria to custom field: {self.acceptance_criteria_field_id}")
            except Exception as e:
                self.logger.warning(f"[JIRA WRITER] Failed to add acceptance criteria to custom field {self.acceptance_criteria_field_id}: {e}")
                return False
        
        url = f"{self.jira_url}/rest/api/3/issue/{issue_key}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.put(
            url,
            json=payload,
            headers=headers,
            auth=(self.email, self.api_token)
        )
        
        if response.status_code == 204:
            self.logger.info("Jira issue updated: %s", issue_key)
            return True
        else:
            self.logger.error("Jira issue update failed: %s %s", 
                            response.status_code, response.text)
            return False


class DocumentWriter:
    """Handles writing documents to various formats (DOCX, JIRA)"""
    
    def __init__(self):
        """
        Initializes the DocumentWriter.

        Loads environment variables for JIRA integration, such as URL, credentials,
        and project details.
        """
        load_dotenv()
        self.jira_url = os.getenv("JIRA_URL")
        # Support either legacy EMAIL/API_TOKEN or new JIRA_EMAIL/JIRA_API_TOKEN
        self.email = os.getenv("JIRA_EMAIL") or os.getenv("EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN") or os.getenv("API_TOKEN")
        self.project_key = os.getenv("PROJECT_KEY") or os.getenv("JIRA_PROJECT_KEY")
        self.acceptance_criteria_field_id = os.getenv("ACCEPTANCE_CRITERIA_FIELD_ID")
        self.logger = logging.getLogger(__name__)
    
    def convert_to_adf(self, json_data):
        """
        Convert a structured document JSON into Atlassian Document Format (ADF).

        This method recursively traverses the JSON structure of a document and
        builds a corresponding ADF structure, which is used for creating JIRA issues.

        Args:
            json_data (Dict[str, Any]): The structured JSON data of the document.

        Returns:
            Dict[str, Any]: The document content in Atlassian Document Format.
        """
        def convert_runs(runs):
            """
            Convert a list of runs into ADF text nodes with marks.

            Args:
                runs (List[Dict[str, Any]]): A list of run objects.

            Returns:
                List[Dict[str, Any]]: A list of ADF text nodes.
            """
            adf_text = []
            for run in runs:
                if not run.get("text"):
                    continue
                text_node = {"type": "text", "text": run["text"]}
                marks = []
                if run.get("bold"): marks.append({"type": "strong"})
                if run.get("italic"): marks.append({"type": "em"})
                if run.get("underline"): marks.append({"type": "underline"})
                if marks:
                    text_node["marks"] = marks
                adf_text.append(text_node)
            return adf_text
        
        def convert_paragraph(paragraph):
            """
            Convert a paragraph object into an ADF paragraph node.

            Args:
                paragraph (Dict[str, Any] or str): A paragraph object or string.

            Returns:
                Dict[str, Any]: An ADF paragraph node.
            """
            # Handle string paragraphs
            if isinstance(paragraph, str):
                return {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": paragraph}]
                }
            
            # Handle dictionary paragraphs
            if isinstance(paragraph, dict) and "runs" in paragraph:
                return {
                    "type": "paragraph",
                    "content": convert_runs(paragraph["runs"])
                }
            
            # Handle dictionary paragraphs without runs
            if isinstance(paragraph, dict):
                text = paragraph.get("text", str(paragraph))
                return {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": text}]
                }
            
            # Fallback for any other type
            return {
                "type": "paragraph",
                "content": [{"type": "text", "text": str(paragraph)}]
            }
        
        def convert_table(table_data):
            """
            Convert a table structure into an ADF table node.

            Args:
                table_data (List[List[Dict[str, Any]]]): A nested list representing the table.

            Returns:
                Dict[str, Any]: An ADF table node.
            """
            rows = []
            for row_index, row in enumerate(table_data):
                row_adf = []
                for col_index, cell in enumerate(row):
                    try:
                        if isinstance(cell, dict):
                            cell_content = []
                            for para in cell.get("paragraphs", []):
                                cell_content.append(convert_paragraph(para))
                        else:
                            cell_content = [{
                                "type": "paragraph",
                                "content": [{"type": "text", "text": str(cell)}]
                            }]
                        row_adf.append({
                            "type": "tableCell",
                            "content": cell_content or [{"type": "paragraph", "content": []}]
                        })
                    except Exception:
                        self.logger.exception(f"Failed to convert cell at ({row_index}, {col_index})")
                        continue
                rows.append({"type": "tableRow", "content": row_adf})
            return {"type": "table", "content": rows}
        
        content = []
        for section in json_data.get("sections", []):
            title = section.get("title", "")
            content.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": title}]
            })
            
            for block in section.get("content", []):
                block_type = block.get("type")
                
                if block_type == "text":
                    content.append(convert_paragraph(block))
                elif block_type == "bullet":
                    content.append({
                        "type": "bulletList",
                        "content": [{
                            "type": "listItem",
                            "content": [convert_paragraph(block)]
                        }]
                    })
                elif block_type == "table":
                    content.append(convert_table(block.get("data", [])))
                elif isinstance(block, dict) and "runs" in block:
                    content.append(convert_paragraph(block))
                else:
                    content.append({
                        "type": "paragraph",
                        "content": [{"type": "text", "text": str(block)}]
                    })
        
        return {"type": "doc", "version": 1, "content": content}
    
    def extract_acceptance_criteria(self, parsed_data):
        """
        Extract the 'Acceptance Criteria' section from parsed document data.

        This method finds the section titled 'Acceptance Criteria', removes it
        from the parsed data, and returns it.

        Args:
            parsed_data (Dict[str, Any]): The structured JSON data of the document.

        Returns:
            Optional[Dict[str, Any]]: The acceptance criteria section, or None if not found.
        """
        for i, section in enumerate(parsed_data.get("sections", [])):
            if "Acceptance Criteria" in section.get("title", ""):
                return parsed_data["sections"].pop(i)
        return None
    
    def extract_summary(self, parsed_data):
        """
        Extract a summary or title from the parsed document data.

        It looks for a line starting with "Title:" to use as the summary.
        If not found, it returns a default title.

        Args:
            parsed_data (Dict[str, Any]): The structured JSON data of the document.

        Returns:
            str: The extracted summary or a default title.
        """
        for section in parsed_data.get("sections", []):
            for block in section.get("content", []):
                if "runs" in block:
                    for run in block["runs"]:
                        text = run.get("text", "")
                        if text.lower().startswith("title:"):
                            return text.split("Title:", 1)[-1].strip()
        return "Untitled Story"
    
    def create_jira_story(self, parsed_data):
        """
        Create a JIRA story from parsed document data.

        This method orchestrates the creation of a JIRA issue by extracting the
        summary and acceptance criteria, converting the content to ADF, and
        sending a request to the JIRA API.

        Args:
            parsed_data (Dict[str, Any]): The structured JSON data of the document.
        """
        # Basic validation – if mandatory pieces missing, abort early
        if not (self.jira_url and self.email and self.api_token and self.project_key):
            self.logger.warning("[JIRA WRITER] Missing Jira configuration – skipping story creation.")
            return

        try:
            summary = self.extract_summary(parsed_data)
            acceptance_section = self.extract_acceptance_criteria(parsed_data)
            
            description_adf = self.convert_to_adf(parsed_data)
            acceptance_adf = self.convert_to_adf(
                {"sections": [acceptance_section]} if acceptance_section else {"sections": []}
            )
            
            self.logger.info("Creating Jira story: %s", summary)
            
            payload = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": description_adf,
                    "issuetype": {"name": "Story"},
                    self.acceptance_criteria_field_id: acceptance_adf
                }
            }
            
            url = f"{self.jira_url}/rest/api/3/issue"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                auth=(self.email, self.api_token)
            )
            
            if response.status_code == 201:
                issue_key = response.json()["key"]
                self.logger.info("Jira issue created: %s", issue_key)
            else:
                self.logger.error("Jira issue creation failed: %s %s", 
                                response.status_code, response.text)
        
        except Exception:
            self.logger.exception("Exception during Jira story creation")
    
    def add_runs(self, paragraph, runs):
        """
        Add a series of formatted text runs to a DOCX paragraph.

        Args:
            paragraph: The DOCX paragraph object to add runs to.
            runs (List[Dict[str, Any]]): A list of run objects with text and formatting.
        """
        for run in runs:
            # Clean the text to avoid ValueError from lxml when illegal control
            # characters (e.g., NULL bytes) are present.
            safe_text = _sanitize_text(run.get("text", ""))

            r = paragraph.add_run(safe_text)
            r.bold = run.get("bold", False)
            r.italic = run.get("italic", False)
            r.underline = run.get("underline", False)
    
    def is_valid_style(self, doc_or_cell, style_name):
        """
        Check if a given style name exists in the document's styles.

        Args:
            doc_or_cell: The document or cell object containing the styles.
            style_name (str): The name of the style to check.

        Returns:
            bool: True if the style exists, False otherwise.
        """
        return style_name in [s.name for s in doc_or_cell.styles]
    
    def build_table(self, doc_or_cell, table_data):
        """
        Recursively build a table in a DOCX document from structured data.

        This method creates a table and populates its cells with paragraphs,
        nested tables, and formatted text based on the provided data.

        Args:
            doc_or_cell: The document or cell object to add the table to.
            table_data (List[List[Dict[str, Any]]]): A nested list representing the table.
        """
        rows = len(table_data)
        cols = max(len(r) for r in table_data) if rows else 0
        table = doc_or_cell.add_table(rows=rows, cols=cols)
        table.style = 'Table Grid'
        
        for i, row_data in enumerate(table_data):
            for j, cell_data in enumerate(row_data):
                cell = table.cell(i, j)
                
                if isinstance(cell_data, dict):
                    for para_data in cell_data.get("paragraphs", []):
                        para = cell.add_paragraph()
                        
                        # Handle case where para_data might be a string instead of dict
                        if isinstance(para_data, str):
                            # If para_data is a string, create a simple text run
                            run = para.add_run(para_data)
                            para.style = "Normal"
                        elif isinstance(para_data, dict):
                            self.add_runs(para, para_data.get("runs", []))
                            
                            style_name = para_data.get("style")
                            if style_name and self.is_valid_style(doc_or_cell, style_name):
                                para.style = style_name
                            else:
                                para.style = "Normal"
                            
                            if para_data.get("type") in ["bullet", "numbered"]:
                                level = para_data.get("level", 0)
                                list_prefix = "List Bullet" if para_data["type"] == "bullet" else "List Number"
                                para.style = f"{list_prefix} {level + 1}" if level > 0 else list_prefix
                    
                    for nested in cell_data.get("nested_tables", []):
                        self.build_table(cell, nested)
                    
                    grid_span = cell_data.get("gridSpan")
                    if grid_span and grid_span > 1:
                        try:
                            tcPr = cell._tc.get_or_add_tcPr()
                            from docx.oxml import OxmlElement
                            grid_span_el = OxmlElement('w:gridSpan')
                            grid_span_el.set(qn('w:val'), str(grid_span))  # type: ignore[name-defined]
                            tcPr.append(grid_span_el)
                        except Exception as e:
                            # Fallback: log and proceed without grid span to avoid crash
                            self.logger.warning("Could not set gridSpan on DOCX cell: %s", e)
                else:
                    cell.text = _sanitize_text(str(cell_data))
    
    def create_docx(self, json_data, output_path):
        """
        Convert structured JSON document data into a .docx file.

        This method creates a new DOCX document and populates it with content
        from the structured JSON data, including headings, paragraphs, lists,
        tables, and headers/footers.

        Args:
            json_data (Dict[str, Any]): The structured JSON data of the document.
            output_path (str): The file path to save the generated .docx file.
        """
        doc = Document()
        
        font = doc.styles['Normal'].font  # type: ignore[attr-defined]
        font.name = 'Calibri'
        font.size = Pt(11)
        
        for section in doc.sections:
            if json_data.get("headers"):
                section.header.paragraphs[0].text = _sanitize_text(json_data["headers"][0])
            if json_data.get("footers"):
                section.footer.paragraphs[0].text = _sanitize_text(json_data["footers"][0])
        
        # Determine whether we're dealing with the new heading-wise structure or legacy sections
        iterable_blocks = []
        if "headings" in json_data:
            # Sort by position to preserve original order
            iterable_blocks = sorted(json_data["headings"], key=lambda h: h.get("position", 0))
        else:
            iterable_blocks = json_data.get("sections", [])

        for section in iterable_blocks:
            title = _sanitize_text(section.get("title", ""))
            if title:
                doc.add_heading(title, level=1)
            
            for item in section.get("content", []):
                item_type = item.get("type", "text")
                if item_type in ["text", "bullet", "numbered"]:
                    para = doc.add_paragraph()
                    self.add_runs(para, item.get("runs", []))
                    
                    style_name = item.get("style")
                    if style_name and self.is_valid_style(doc, style_name):
                        para.style = style_name
                    else:
                        para.style = "Normal"
                    
                    if item_type in ["bullet", "numbered"]:
                        level = item.get("level", 0)
                        list_prefix = "List Bullet" if item["type"] == "bullet" else "List Number"
                        para.style = f"{list_prefix} {level + 1}" if level > 0 else list_prefix
                
                elif item_type == "table":
                    self.build_table(doc, item.get("data", []))
        
        doc.save(output_path)
        self.logger.info(f"Document saved to {output_path}")

    def create_plain_text(self, json_data: Dict[str, Any], output_path: str) -> None:
        """
        Convert structured JSON document data into a plain text file.
        Handles tables by converting them into ASCII-style text tables.

        Args:
            json_data (Dict[str, Any]): The structured JSON data of the document
            output_path (str): The file path to save the generated .txt file
        """
        def format_table(table_data: List[List[Dict[str, Any]]]) -> str:
            """Format a table as ASCII text with proper alignment."""
            if not table_data:
                return ""

            # Calculate max width for each column
            col_widths = []
            for row in table_data:
                while len(col_widths) < len(row):
                    col_widths.append(0)
                for i, cell in enumerate(row):
                    # Handle both string and dict cell formats
                    if isinstance(cell, dict):
                        # Join all paragraphs in the cell
                        cell_text = "\n".join(
                            " ".join(run.get("text", "") for run in para.get("runs", []))
                            for para in cell.get("paragraphs", [])
                        )
                    else:
                        cell_text = str(cell)
                    # Update column width based on the longest line in the cell
                    width = max(len(line) for line in cell_text.split("\n"))
                    col_widths[i] = max(col_widths[i], width)

            # Build the table string
            table_str = []
            separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

            for row_idx, row in enumerate(table_data):
                # Split cells into lines
                row_lines = []
                max_lines = 1
                for i, cell in enumerate(row):
                    if isinstance(cell, dict):
                        cell_text = "\n".join(
                            " ".join(run.get("text", "") for run in para.get("runs", []))
                            for para in cell.get("paragraphs", [])
                        )
                    else:
                        cell_text = str(cell)
                    lines = cell_text.split("\n")
                    max_lines = max(max_lines, len(lines))
                    row_lines.append(lines)

                # Add separator before each row
                table_str.append(separator)

                # Build each line of the row
                for line_idx in range(max_lines):
                    row_str = "|"
                    for col_idx, lines in enumerate(row_lines):
                        content = lines[line_idx] if line_idx < len(lines) else ""
                        row_str += f" {content:<{col_widths[col_idx]}} |"
                    table_str.append(row_str)

            # Add final separator
            table_str.append(separator)
            return "\n".join(table_str)

        with open(output_path, "w", encoding="utf-8") as f:
            # Write headers if present
            if json_data.get("headers"):
                f.write(f"{json_data['headers'][0]}\n\n")

            # Determine whether we're dealing with heading-wise or section-wise structure
            iterable_blocks = []
            if "headings" in json_data:
                # Sort by position to preserve original order
                iterable_blocks = sorted(json_data["headings"], 
                                      key=lambda h: h.get("position", 0))
            else:
                iterable_blocks = json_data.get("sections", [])

            # Process each block
            for block in iterable_blocks:
                # Write title
                title = _sanitize_text(block.get("title", ""))
                if title:
                    f.write(f"\n{title}\n{'='*len(title)}\n\n")

                # Process content
                for item in block.get("content", []):
                    item_type = item.get("type", "text")
                    
                    if item_type in ["text", "bullet"]:
                        # Handle text and bullet points
                        if isinstance(item.get("content"), str):
                            content = item["content"]
                        else:
                            content = " ".join(run.get("text", "") for run in item.get("runs", []))
                        
                        if item_type == "bullet":
                            f.write(f"  • {content}\n")
                        else:
                            f.write(f"{content}\n")
                        
                    elif item_type == "table":
                        # Format and write table
                        table_str = format_table(item.get("data", []))
                        f.write(f"\n{table_str}\n\n")
                
                f.write("\n")  # Add spacing between sections

            # Write footers if present
            if json_data.get("footers"):
                f.write(f"\n{json_data['footers'][0]}\n")

        self.logger.info(f"Plain text document saved to {output_path}")

# Legacy functions for backward compatibility
def create_jira_story(parsed_data):
    """
    Legacy function wrapper for DocumentWriter.create_jira_story.

    Args:
        parsed_data (Dict[str, Any]): The structured JSON data of the document.
    """
    return DocumentWriter().create_jira_story(parsed_data)

def create_docx(json_data, output_path):
    """
    Legacy function wrapper for DocumentWriter.create_docx.

    Args:
        json_data (Dict[str, Any]): The structured JSON data of the document.
        output_path (str): The file path to save the generated .docx file.
    """
    return DocumentWriter().create_docx(json_data, output_path)
