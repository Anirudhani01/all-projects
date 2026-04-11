# -*- coding: utf-8 -*-
"""JIRA issue parser implementation.

This parser fetches a JIRA issue via the REST API and converts it into the
same structured JSON format produced by `DocxParser`, so the rest of the
pipeline can work unchanged.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import requests

from components.common.settings import Settings
from components.parser.parser import BaseParser


class JiraParser(BaseParser):
    """Parse a JIRA issue into the internal story JSON format."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.logger = logging.getLogger(__name__)

        if not (self.settings.jira_url and self.settings.jira_email and self.settings.jira_api_token):
            self.logger.warning(
                "[JIRA PARSER] Jira URL, email, or API token not fully provided – operations may fail."
            )

        # Build a session so we reuse TCP connections
        self.session = requests.Session()
        self.session.auth = (self.settings.jira_email or "", self.settings.jira_api_token or "")
        self.session.headers.update({"Accept": "application/json"})

    # ---------------------------------------------------------------------
    # BaseParser interface
    # ---------------------------------------------------------------------
    def parse_document(self, issue_key: str) -> Dict[str, Any]:
        """Return structured JSON for a given JIRA issue key."""
        issue = self._get_issue(issue_key)
        fields = issue.get("fields", {})

        summary: str = fields.get("summary", "")
        
        # Convert ADF description to structured format
        description_adf = fields.get("description", {})
        sections = self._convert_adf_to_sections(description_adf, summary)
        
        # Extract acceptance criteria if available
        acceptance_criteria_field_id = os.getenv("ACCEPTANCE_CRITERIA_FIELD_ID")
        if acceptance_criteria_field_id:
            try:
                acceptance_criteria = fields.get(acceptance_criteria_field_id, {})
                if acceptance_criteria:
                    ac_sections = self._convert_adf_to_sections(acceptance_criteria, "Acceptance Criteria")
                    sections.extend(ac_sections)
                    self.logger.info(f"[JIRA PARSER] Successfully extracted acceptance criteria from custom field: {acceptance_criteria_field_id}")
            except Exception as e:
                self.logger.warning(f"[JIRA PARSER] Failed to extract acceptance criteria from custom field {acceptance_criteria_field_id}: {e}")
                self.logger.info("[JIRA PARSER] Falling back to parsing acceptance criteria from description content")

        # Convert to unified story format
        story: Dict[str, Any] = {
            "sections": sections,
            "headers": [],
            "footers": [],
            "metadata": {"source_path": issue_key},
        }

        return story

    def extract_plain_text(self, issue_key: str) -> str:
        """Get plain-text representation of the issue for RAG."""
        issue = self._get_issue(issue_key)
        fields = issue.get("fields", {})
        summary = fields.get("summary", "")
        desc = self._extract_description(fields)
        return "\n".join(part for part in [summary, desc] if part)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Fetch an issue; returns empty dict on failure instead of raising."""
        if not self.settings.jira_url:
            self.logger.error("[JIRA PARSER] JIRA_URL missing – cannot fetch %s", issue_key)
            return {}
        url = f"{self.settings.jira_url}/rest/api/3/issue/{issue_key}?expand=renderedFields"
        self.logger.info("[JIRA PARSER] Fetching issue %s from %s", issue_key, self.settings.jira_url)
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            self.logger.warning("[JIRA PARSER] Could not retrieve issue %s: %s", issue_key, exc)
            return {}

    def _convert_adf_to_sections(self, adf_content: Dict[str, Any], default_title: str = "") -> List[Dict[str, Any]]:
        """Convert ADF (Atlassian Document Format) to structured sections."""
        if not isinstance(adf_content, dict) or "content" not in adf_content:
            return []
        
        sections = []
        current_section = {"title": default_title, "content": []}
        
        for block in adf_content.get("content", []):
            block_type = block.get("type", "")
            
            if block_type == "heading":
                # Save current section if it has content
                if current_section["content"] or current_section["title"]:
                    sections.append(current_section)
                
                # Start new section with heading title
                heading_text = self._extract_text_from_adf_node(block)
                current_section = {"title": heading_text, "content": []}
                
            elif block_type == "paragraph":
                content_item = self._convert_adf_paragraph(block)
                if content_item:
                    current_section["content"].append(content_item)
                    
            elif block_type == "bulletList":
                for list_item in block.get("content", []):
                    if list_item.get("type") == "listItem":
                        content_item = self._convert_adf_list_item(list_item, "bullet")
                        if content_item:
                            current_section["content"].append(content_item)
                            
            elif block_type == "orderedList":
                for list_item in block.get("content", []):
                    if list_item.get("type") == "listItem":
                        content_item = self._convert_adf_list_item(list_item, "numbered")
                        if content_item:
                            current_section["content"].append(content_item)
                            
            elif block_type == "table":
                table_item = self._convert_adf_table(block)
                if table_item:
                    current_section["content"].append(table_item)
        
        # Add the last section
        if current_section["content"] or current_section["title"]:
            sections.append(current_section)
        
        return sections
    
    def _extract_text_from_adf_node(self, node: Dict[str, Any]) -> str:
        """Extract plain text from any ADF node."""
        if node.get("type") == "text":
            return node.get("text", "")
        
        text_parts = []
        for child in node.get("content", []):
            text_parts.append(self._extract_text_from_adf_node(child))
        
        return "".join(text_parts)
    
    def _convert_adf_paragraph(self, paragraph: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ADF paragraph to structured format."""
        runs = []
        
        for content_item in paragraph.get("content", []):
            if content_item.get("type") == "text":
                run = {
                    "text": content_item.get("text", ""),
                    "bold": False,
                    "italic": False,
                    "underline": False
                }
                
                # Check for marks (formatting)
                marks = content_item.get("marks", [])
                for mark in marks:
                    mark_type = mark.get("type", "")
                    if mark_type == "strong":
                        run["bold"] = True
                    elif mark_type == "em":
                        run["italic"] = True
                    elif mark_type == "underline":
                        run["underline"] = True
                
                runs.append(run)
        
        return {
            "type": "text",
            "runs": runs,
            "style": "Normal"
        }
    
    def _convert_adf_list_item(self, list_item: Dict[str, Any], list_type: str) -> Dict[str, Any]:
        """Convert ADF list item to structured format."""
        # Extract text from the list item's paragraphs
        runs = []
        
        for content_item in list_item.get("content", []):
            if content_item.get("type") == "paragraph":
                paragraph_runs = self._convert_adf_paragraph(content_item).get("runs", [])
                runs.extend(paragraph_runs)
        
        return {
            "type": list_type,
            "runs": runs,
            "style": "Normal",
            "level": 0  # Default level, could be enhanced to handle nested lists
        }
    
    def _convert_adf_table(self, table: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ADF table to structured format."""
        table_data = []
        
        for row in table.get("content", []):
            if row.get("type") == "tableRow":
                row_data = []
                
                for cell in row.get("content", []):
                    if cell.get("type") in ["tableCell", "tableHeader"]:
                        cell_data = {
                            "paragraphs": [],
                            "gridSpan": 1,  # Default span
                            "vMerge": None,
                            "nested_tables": []
                        }
                        
                        # Convert cell content
                        for cell_content in cell.get("content", []):
                            if cell_content.get("type") == "paragraph":
                                paragraph_data = self._convert_adf_paragraph(cell_content)
                                cell_data["paragraphs"].append(paragraph_data)
                        
                        row_data.append(cell_data)
                
                table_data.append(row_data)
        
        return {
            "type": "table",
            "data": table_data
        }

    @staticmethod
    def _extract_description(fields: Dict[str, Any]) -> str:
        """Extract plain description text regardless of how Jira returns it."""
        desc = fields.get("description", "")
        if isinstance(desc, str):
            return desc
        # When "description" is an Atlassian Document Format (ADF) structure
        if isinstance(desc, dict):
            try:
                # Very naive flattening of paragraph nodes
                content: List[str] = []
                for blk in desc.get("content", []):
                    if blk.get("type") == "paragraph":
                        paragraph_text = "".join(
                            span.get("text", "") for span in blk.get("content", []) if isinstance(span, dict)
                        )
                        content.append(paragraph_text)
                return "\n".join(content)
            except Exception:
                # Fallback to string conversion
                return str(desc)
        return str(desc) 