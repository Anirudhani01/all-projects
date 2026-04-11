import json
from abc import ABC, abstractmethod
from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.shared import Pt

class BaseParser(ABC):
    """Interface for parser implementations."""

    @abstractmethod
    def parse_document(self, source: str):
        """Return structured representation of document/story."""

    @abstractmethod
    def extract_plain_text(self, source: str) -> str:
        """Return plain-text version used for RAG context."""


class DocxParser(BaseParser):
    """Parses DOCX documents into structured data"""
    
    def __init__(self):
        """Initializes the DocxParser."""
        pass
    
    def iter_block_items(self, parent):
        """
        Generate each block-level item in a document's body.

        This generator yields Paragraph and Table objects, allowing iteration
        over the main content blocks of a document or a table cell.

        Args:
            parent: The parent object, typically a Document or a Cell.

        Yields:
            Union[DocxParagraph, DocxTable]: The next block-level item.
        """
        for child in parent.element.body.iterchildren():
            if isinstance(child, CT_P):
                yield DocxParagraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield DocxTable(child, parent)
    
    def get_paragraph_list_level(self, paragraph):
        """
        Determine the indentation level of a list item paragraph.

        This method inspects the numbering properties of a paragraph to find its
        list level. It is useful for parsing nested lists.

        Args:
            paragraph (DocxParagraph): The paragraph to inspect.

        Returns:
            Optional[int]: The list level (0-based) or None if it's not a list item.
        """
        p = paragraph._element
        numPr = p.find('.//w:numPr', namespaces=p.nsmap)
        if numPr is None:
            return None
        ilvl = numPr.find('.//w:ilvl', namespaces=p.nsmap)
        if ilvl is not None:
            return int(ilvl.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'))
        return 0
    
    def parse_runs(self, paragraph):
        """
        Extract text and styling information from each run in a paragraph.

        A run is a contiguous sequence of characters with the same formatting. This
        method breaks a paragraph down into its constituent runs.

        Args:
            paragraph (DocxParagraph): The paragraph to parse.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a run.
        """
        runs_data = []
        for run in paragraph.runs:
            runs_data.append({
                "text": run.text,
                "bold": run.bold,
                "italic": run.italic,
                "underline": run.underline
            })
        return runs_data
    
    def get_vmerge_val(self, cell):
        """
        Retrieve the vertical merge value from a table cell.

        This is used to identify cells that are vertically merged in a table.
        The value can be 'restart' for the top cell of a merge or 'continue'
        for subsequent cells in the merge.

        Args:
            cell: The table cell object.

        Returns:
            Optional[str]: The vertical merge value or None if not merged.
        """
        vmerge = cell._tc.xpath(".//w:vMerge")
        if not vmerge:
            return None
        val = vmerge[0].get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val")
        return val if val else "continue"
    
    def parse_table(self, table):
        """
        Parse a DOCX table into a structured nested list format.

        This method iterates through the rows and cells of a table, extracting
        paragraphs, nested tables, and cell merging information.

        Args:
            table (DocxTable): The table to parse.

        Returns:
            List[List[Dict[str, Any]]]: A nested list representing the table's structure and content.
        """
        table_data = []
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                cell_data = {
                    "paragraphs": [],
                    "gridSpan": cell._tc.grid_span,
                    "vMerge": self.get_vmerge_val(cell),
                    "nested_tables": []
                }
                
                for para in cell.paragraphs:
                    list_level = self.get_paragraph_list_level(para)
                    para_type = None
                    if list_level is not None:
                        para_type = "numbered" if "Number" in para.style.name else "bullet"
                    else:
                        para_type = "text"
                    
                    para_entry = {
                        "type": para_type,
                        "runs": self.parse_runs(para),
                        "style": para.style.name or ""
                    }
                    
                    if list_level is not None:
                        para_entry["level"] = list_level
                    
                    cell_data["paragraphs"].append(para_entry)
                
                for nested_tbl in cell._tc.xpath('.//w:tbl'):
                    nested_table = DocxTable(nested_tbl, table._parent)
                    cell_data["nested_tables"].append(self.parse_table(nested_table))
                
                row_data.append(cell_data)
            table_data.append(row_data)
        return table_data
    
    def extract_headers_footers(self, doc):
        """
        Extract all text from the headers and footers of a document.

        Args:
            doc (Document): The DOCX document object.

        Returns:
            Tuple[List[str], List[str]]: A tuple containing a list of header texts
                                         and a list of footer texts.
        """
        headers = []
        footers = []
        for section in doc.sections:
            headers += [p.text for p in section.header.paragraphs]
            footers += [p.text for p in section.footer.paragraphs]
        return headers, footers
    
    def parse_document(self, doc_path):
        """
        Parse a full DOCX document into a structured JSON-like format.

        This is the main parsing method. It reads a .docx file and converts its
        content, including headings, paragraphs, lists, and tables, into a
        hierarchical dictionary.

        Args:
            doc_path (str): The file path to the DOCX document.

        Returns:
            Dict[str, Any]: A dictionary representing the structured content of the document.
        """
        doc = Document(doc_path)
        
        result = {
            "sections": [],
            "headers": [],
            "footers": [],
        }
        
        headers, footers = self.extract_headers_footers(doc)
        result["headers"] = headers
        result["footers"] = footers
        
        current_title = ""
        current_content = []
        
        def save_section():
            if current_title != "" or current_content:
                result["sections"].append({
                    "title": current_title,
                    "content": current_content.copy()
                })
        
        for block in self.iter_block_items(doc):
            if isinstance(block, DocxParagraph):
                text = block.text.strip()
                if not text:
                    continue
                
                style = block.style.name or ""
                list_level = self.get_paragraph_list_level(block)
                
                if style.startswith("Heading"):
                    save_section()
                    current_title = text
                    current_content = []
                elif list_level is not None:
                    para_type = "numbered" if "Number" in style else "bullet"
                    current_content.append({
                        "type": para_type,
                        "runs": self.parse_runs(block),
                        "style": style,
                        "level": list_level
                    })
                else:
                    current_content.append({
                        "type": "text",
                        "runs": self.parse_runs(block),
                        "style": style
                    })
            
            elif isinstance(block, DocxTable):
                current_content.append({
                    "type": "table",
                    "data": self.parse_table(block)
                })
        
        save_section()
        return result
    
    def extract_plain_text(self, doc_path):
        """
        Extract plain text from a DOCX document for RAG processing.

        This method converts the entire document content, including headers, footers,
        and tables, into a single string of plain text.

        Args:
            doc_path (str): The file path to the DOCX document.

        Returns:
            str: The concatenated plain text from the document.
        """
        doc = Document(doc_path)
        paragraphs = []
        
        headers, footers = self.extract_headers_footers(doc)
        for h in headers:
            if h.strip():
                paragraphs.append(h.strip())
        
        def extract_from_cell(cell):
            for para in cell.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
            for nested_tbl in cell._tc.xpath('.//w:tbl'):
                nested = DocxTable(nested_tbl, cell._parent)
                self.extract_from_table(nested)
        
        def extract_from_table(table):
            for row in table.rows:
                for cell in row.cells:
                    extract_from_cell(cell)
        
        self.extract_from_table = extract_from_table
        
        for block in self.iter_block_items(doc):
            if isinstance(block, DocxParagraph):
                text = block.text.strip()
                if text:
                    paragraphs.append(text)
            elif isinstance(block, DocxTable):
                extract_from_table(block)
        
        for f in footers:
            if f.strip():
                paragraphs.append(f.strip())
        
        return "\n".join(paragraphs)

# Alias for backward compatibility
DocumentParser = DocxParser

# Legacy functions for backward compatibility
def parser(doc_path):
    """
    Legacy function wrapper for DocumentParser.parse_document.

    This function provides backward compatibility for older code that uses a
    standalone parser function.

    Args:
        doc_path (str): The file path to the DOCX document.

    Returns:
        Dict[str, Any]: A dictionary representing the structured content of the document.
    """
    return DocumentParser().parse_document(doc_path)

def plain_text_parser(doc_path):
    """
    Legacy function wrapper for DocumentParser.extract_plain_text.

    This function provides backward compatibility for older code that uses a
    standalone plain text parser function.

    Args:
        doc_path (str): The file path to the DOCX document.

    Returns:
        str: The concatenated plain text from the document.
    """
    return DocumentParser().extract_plain_text(doc_path)
