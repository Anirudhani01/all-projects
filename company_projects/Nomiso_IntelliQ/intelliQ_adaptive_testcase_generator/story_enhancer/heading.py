from dataclasses import dataclass
from typing import List, Any

@dataclass
class Heading:
    """Represents a top-level heading and its scoped content."""

    heading_id: str  # e.g. "h1", "h2" or UUID
    title: str       # Heading text
    content: List[Any]  # Mixed list: paragraphs, tables, etc.
    position: int    # Original order in the document 