# -*- coding: utf-8 -*-
"""JIRA issue parser implementation.

This parser fetches a JIRA issue via the REST API and converts it into the
same structured JSON format produced by `DocxParser`, so the rest of the
pipeline can work unchanged.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests

from config.settings import Settings
from external.parser import BaseParser


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
        description_plain = self._extract_description(fields)

        # Convert to unified story format
        story: Dict[str, Any] = {
            "sections": [
                {
                    "title": summary,
                    "content": [
                        {
                            "type": "text",
                            "runs": [
                                {
                                    "text": description_plain,
                                    "bold": False,
                                    "italic": False,
                                    "underline": False,
                                }
                            ],
                            "style": "Normal",
                        }
                    ],
                }
            ],
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