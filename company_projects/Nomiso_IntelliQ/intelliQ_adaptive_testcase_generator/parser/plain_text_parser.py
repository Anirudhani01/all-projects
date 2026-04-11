import re
from typing import Dict, Any, List
import docx
import logging

logger = logging.getLogger(__name__)

class PlainTextParser:
    """
    A parser that converts Word documents into a simple JSON structure,
    focusing on plain text representation while preserving heading hierarchy.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Word document into a JSON structure with plain text content.

        Args:
            file_path (str): Path to the Word document

        Returns:
            Dict[str, Any]: JSON structure with headings and content
        """
        try:
            doc = docx.Document(file_path)
            headings = self._extract_headings(doc)
            return {"headings": headings}
        except Exception as e:
            self.logger.error(f"Failed to parse document: {e}")
            return {"headings": []}

    def _extract_headings(self, doc: docx.Document) -> List[Dict[str, Any]]:
        """
        Extract headings and their content from the document.

        Args:
            doc (docx.Document): Word document

        Returns:
            List[Dict[str, Any]]: List of headings with their content
        """
        headings = []
        current_heading = None
        current_content = []
        heading_pattern = re.compile(r'^(?:\d+\.)*\d+\s+')

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Check if this is a heading
            if heading_pattern.match(text) or para.style.name.startswith('Heading'):
                # Save previous heading if exists
                if current_heading:
                    headings.append({
                        "heading_id": str(len(headings) + 1),
                        "title": current_heading,
                        "content": "\n".join(current_content)
                    })

                current_heading = text
                current_content = []
            else:
                current_content.append(text)

        # Add the last heading
        if current_heading:
            headings.append({
                "heading_id": str(len(headings) + 1),
                "title": current_heading,
                "content": "\n".join(current_content)
            })

        # Sort headings by their numeric position
        return sorted(headings, key=self._parse_heading_position)

    def _parse_heading_position(self, heading: Dict[str, Any]) -> tuple:
        """
        Parse heading position for proper sorting (e.g., "7.1" comes before "7.10").

        Args:
            heading (Dict[str, Any]): Heading dictionary

        Returns:
            tuple: Tuple of integers representing the position
        """
        title = heading["title"]
        parts = []
        number_part = ""
        
        for char in title:
            if char.isdigit() or char == '.':
                number_part += char
            else:
                break
                
        if number_part:
            # Split by dots and convert to integers
            parts = [int(p) if p.isdigit() else 0 for p in number_part.split('.')]
        
        # Pad with zeros for consistent sorting
        return tuple(parts + [0] * (5 - len(parts))) 