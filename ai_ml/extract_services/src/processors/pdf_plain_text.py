"""
PDF Plain Text Processor
Handles PDFs with plain text content using PyMuPDF and pdfplumber
"""
import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from .base_processor import BaseProcessor
from config import settings

logger = logging.getLogger(__name__)

class PDFPlainTextProcessor(BaseProcessor):
    """Processor for PDFs with plain text content"""
    
    def __init__(self):
        super().__init__()
        self.processor_name = "PDFPlainTextProcessor"
    
    def process(self, input_file: Path) -> Dict[str, Any]:
        """
        Process PDF file and extract plain text
        
        Args:
            input_file: Path to the PDF file
            
        Returns:
            Dictionary containing extracted data
        """
        self.log_step("Starting PDF plain text processing", "INFO", f"File: {input_file.name}")
        
        try:
            # Try PyMuPDF first for better performance
            extracted_data = self._extract_with_pymupdf(input_file)
            
            # If PyMuPDF fails or returns poor results, try pdfplumber
            if not extracted_data.get("pages") or not any(page.get("text", "").strip() for page in extracted_data.get("pages", [])):
                self.log_step("PyMuPDF extraction poor, trying pdfplumber", "INFO")
                extracted_data = self._extract_with_pdfplumber(input_file)
            
            # Post-process the extracted data
            extracted_data = self._post_process_data(extracted_data)
            
            self.log_step("PDF processing completed", "SUCCESS", 
                         f"Extracted {len(extracted_data.get('pages', []))} pages")
            
            return extracted_data
            
        except Exception as e:
            self.log_step("PDF processing failed", "ERROR", str(e))
            raise
    
    def _extract_with_pymupdf(self, input_file: Path) -> Dict[str, Any]:
        """Extract text using PyMuPDF"""
        try:
            doc = fitz.open(input_file)
            pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text
                text = page.get_text()
                
                # Get page dimensions
                rect = page.rect
                
                # Extract text blocks with coordinates
                blocks = page.get_text("dict")
                
                page_data = {
                    "page_number": page_num + 1,
                    "text": text,
                    "width": rect.width,
                    "height": rect.height,
                    "blocks": self._process_text_blocks(blocks),
                    "confidence": 1.0  # PyMuPDF text extraction is highly reliable
                }
                
                pages.append(page_data)
                self.log_step(f"Processed page {page_num + 1}", "INFO", f"Text length: {len(text)}")
            
            doc.close()
            
            return {
                "pages": pages,
                "metadata": {
                    "processor": "PyMuPDF",
                    "total_pages": len(pages),
                    "file_info": {
                        "filename": input_file.name,
                        "file_size": input_file.stat().st_size
                    }
                }
            }
            
        except Exception as e:
            self.log_step("PyMuPDF extraction failed", "WARNING", str(e))
            return {"pages": [], "metadata": {}}
    
    def _extract_with_pdfplumber(self, input_file: Path) -> Dict[str, Any]:
        """Extract text using pdfplumber as fallback"""
        try:
            pages = []
            
            with pdfplumber.open(input_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text() or ""
                    
                    # Get page dimensions
                    width = page.width
                    height = page.height
                    
                    # Extract text objects with more detail
                    text_objects = page.chars
                    
                    page_data = {
                        "page_number": page_num + 1,
                        "text": text,
                        "width": width,
                        "height": height,
                        "text_objects": self._process_text_objects(text_objects),
                        "confidence": 0.9  # pdfplumber is also reliable
                    }
                    
                    pages.append(page_data)
                    self.log_step(f"Processed page {page_num + 1} with pdfplumber", "INFO", f"Text length: {len(text)}")
            
            return {
                "pages": pages,
                "metadata": {
                    "processor": "pdfplumber",
                    "total_pages": len(pages),
                    "file_info": {
                        "filename": input_file.name,
                        "file_size": input_file.stat().st_size
                    }
                }
            }
            
        except Exception as e:
            self.log_step("pdfplumber extraction failed", "ERROR", str(e))
            raise
    
    def _process_text_blocks(self, blocks: Dict) -> List[Dict[str, Any]]:
        """Process text blocks from PyMuPDF"""
        processed_blocks = []
        
        try:
            for block in blocks.get("blocks", []):
                if "lines" in block:  # Text block
                    block_text = ""
                    for line in block["lines"]:
                        for span in line["spans"]:
                            block_text += span["text"]
                        block_text += "\n"
                    
                    processed_blocks.append({
                        "type": "text",
                        "text": block_text.strip(),
                        "bbox": block.get("bbox", [0, 0, 0, 0]),
                        "font_info": self._extract_font_info(block)
                    })
                elif "image" in block:  # Image block
                    processed_blocks.append({
                        "type": "image",
                        "bbox": block.get("bbox", [0, 0, 0, 0])
                    })
            
        except Exception as e:
            self.log_step("Error processing text blocks", "WARNING", str(e))
        
        return processed_blocks
    
    def _process_text_objects(self, text_objects: List) -> List[Dict[str, Any]]:
        """Process text objects from pdfplumber"""
        processed_objects = []
        
        try:
            for obj in text_objects:
                processed_objects.append({
                    "text": obj.get("text", ""),
                    "x0": obj.get("x0", 0),
                    "y0": obj.get("y0", 0),
                    "x1": obj.get("x1", 0),
                    "y1": obj.get("y1", 0),
                    "fontname": obj.get("fontname", ""),
                    "size": obj.get("size", 0)
                })
        except Exception as e:
            self.log_step("Error processing text objects", "WARNING", str(e))
        
        return processed_objects
    
    def _extract_font_info(self, block: Dict) -> Dict[str, Any]:
        """Extract font information from text block"""
        try:
            font_info = {
                "fonts": set(),
                "sizes": set(),
                "colors": set()
            }
            
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font_info["fonts"].add(span.get("font", ""))
                    font_info["sizes"].add(span.get("size", 0))
                    font_info["colors"].add(span.get("color", 0))
            
            # Convert sets to lists for JSON serialization
            return {
                "fonts": list(font_info["fonts"]),
                "sizes": list(font_info["sizes"]),
                "colors": list(font_info["colors"])
            }
            
        except Exception as e:
            self.log_step("Error extracting font info", "WARNING", str(e))
            return {"fonts": [], "sizes": [], "colors": []}
    
    def _post_process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process extracted data"""
        try:
            # Clean up text in each page
            for page in data.get("pages", []):
                # Clean and normalize text
                text = page.get("text", "")
                cleaned_text = self._clean_text(text)
                page["text"] = cleaned_text
                
                # Extract structured tables from text
                structured_tables = self._extract_structured_tables(cleaned_text)
                if structured_tables:
                    page["tables"] = structured_tables
                
                # Calculate text statistics
                page["text_stats"] = {
                    "char_count": len(cleaned_text),
                    "word_count": len(cleaned_text.split()),
                    "line_count": len(cleaned_text.split('\n')),
                    "paragraph_count": len([p for p in cleaned_text.split('\n\n') if p.strip()])
                }
            
            # Add overall statistics
            data["metadata"]["extraction_stats"] = self._calculate_overall_stats(data)
            
            return data
            
        except Exception as e:
            self.log_step("Error in post-processing", "WARNING", str(e))
            return data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = ' '.join(line.split())  # Remove extra spaces
            if cleaned_line.strip():
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _calculate_overall_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall extraction statistics"""
        pages = data.get("pages", [])
        
        if not pages:
            return {}
        
        total_chars = sum(page.get("text_stats", {}).get("char_count", 0) for page in pages)
        total_words = sum(page.get("text_stats", {}).get("word_count", 0) for page in pages)
        total_lines = sum(page.get("text_stats", {}).get("line_count", 0) for page in pages)
        
        return {
            "total_characters": total_chars,
            "total_words": total_words,
            "total_lines": total_lines,
            "average_chars_per_page": total_chars / len(pages) if pages else 0,
            "average_words_per_page": total_words / len(pages) if pages else 0
        }
    
    def _extract_structured_tables(self, text: str) -> List[Dict[str, Any]]:
        """Extract structured tables from text using generic patterns"""
        try:
            tables = []
            lines = text.split('\n')
            
            # Extract key-value pairs (like patient info, metadata)
            kv_table = self._extract_key_value_table(lines)
            if kv_table:
                tables.append(kv_table)
            
            # Extract data tables (structured rows with headers)
            data_tables = self._extract_data_tables(lines)
            if data_tables:
                tables.extend(data_tables)
            
            # Extract single value tables (like test results)
            single_value_tables = self._extract_single_value_tables(lines)
            if single_value_tables:
                tables.extend(single_value_tables)
            
            return tables
            
        except Exception as e:
            self.log_step("Error extracting structured tables", "WARNING", str(e))
            return []
    
    def _extract_key_value_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Extract key-value pairs from text"""
        try:
            table_data = []
            kv_pairs = {}
            
            # Look for key-value patterns (Field: Value)
            for line in lines:
                line = line.strip()
                
                # Generic key-value pattern: "Key: Value" or "Key - Value"
                if ':' in line and len(line.split(':', 1)) == 2:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        kv_pairs[key] = value
                elif ' - ' in line and len(line.split(' - ', 1)) == 2:
                    key, value = line.split(' - ', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        kv_pairs[key] = value
            
            if kv_pairs:
                # Create table with key-value pairs
                table_data.append(['Field', 'Value'])
                for field, value in kv_pairs.items():
                    table_data.append([field, value])
                
                return {
                    "type": "key_value_table",
                    "data": table_data,
                    "confidence": 0.8,
                    "method": "key_value_extraction",
                    "title": "Document Information"
                }
            
            return None
            
        except Exception as e:
            self.log_step("Error extracting key-value table", "WARNING", str(e))
            return None
    
    def _extract_data_tables(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract structured data tables from text"""
        try:
            tables = []
            current_table = None
            table_data = []
            in_table = False
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Look for table headers (lines with multiple columns separated by spaces/tabs)
                if self._is_table_header(line):
                    # Save previous table if exists
                    if current_table and len(table_data) > 0:
                        current_table["data"] = table_data
                        tables.append(current_table)
                    
                    # Start new table
                    current_table = {
                        "type": "data_table",
                        "data": [],
                        "confidence": 0.7,
                        "method": "data_table_extraction",
                        "title": f"Data Table {len(tables) + 1}"
                    }
                    table_data = []
                    in_table = True
                    
                    # Add header row
                    header_data = self._parse_data_row(line)
                    if header_data:
                        table_data.append(header_data)
                    continue
                
                # Look for data rows (lines with multiple values)
                if in_table and self._is_data_row(line):
                    row_data = self._parse_data_row(line)
                    if row_data:
                        table_data.append(row_data)
                elif in_table and not self._is_data_row(line):
                    # End of table - save it
                    if current_table and len(table_data) > 0:
                        current_table["data"] = table_data
                        tables.append(current_table)
                    current_table = None
                    table_data = []
                    in_table = False
                elif not in_table and self._is_data_row(line):
                    # Start a new table without explicit header
                    current_table = {
                        "type": "data_table",
                        "data": [],
                        "confidence": 0.6,
                        "method": "data_table_extraction",
                        "title": f"Data Table {len(tables) + 1}"
                    }
                    table_data = []
                    in_table = True
                    
                    # Add this row as data
                    row_data = self._parse_data_row(line)
                    if row_data:
                        table_data.append(row_data)
            
            # Save last table if exists
            if current_table and len(table_data) > 0:
                current_table["data"] = table_data
                tables.append(current_table)
            
            return tables
            
        except Exception as e:
            self.log_step("Error extracting data tables", "WARNING", str(e))
            return []
    
    def _is_table_header(self, line: str) -> bool:
        """Check if line looks like a table header"""
        import re
        
        # Look for lines with multiple words/columns
        words = line.split()
        if len(words) < 2:
            return False
        
        # More flexible header patterns
        header_patterns = [
            r'^[A-Z\s]+$',  # All caps words
            r'^[A-Za-z\s]+\s+[A-Za-z\s]+$',  # Multiple words
            r'.*\s+.*\s+.*',  # At least 3 parts
            r'.*\|.*',  # Contains pipe separators
            r'.*:.*',  # Contains colon separators
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, line):
                return True
        
        # Also check for lines that look like structured data
        if len(words) >= 2 and any(char in line for char in ['|', ':', '-', '=']):
            return True
        
        return False
    
    def _is_data_row(self, line: str) -> bool:
        """Check if line looks like a data row"""
        import re
        
        # Look for lines with multiple values (numbers, words, etc.)
        words = line.split()
        if len(words) < 1:
            return False
        
        # More flexible data row detection
        # Check for data patterns (mix of text and numbers)
        has_text = any(re.search(r'[A-Za-z]', word) for word in words)
        has_numbers = any(re.search(r'[0-9]', word) for word in words)
        
        # Also check for structured data patterns
        has_separators = any(char in line for char in ['|', ':', '-', '='])
        
        # Check for key-value patterns
        has_colon = ':' in line and len(line.split(':', 1)) == 2
        
        return has_text or has_numbers or has_separators or has_colon
    
    def _parse_data_row(self, line: str) -> List[str]:
        """Parse a data row into columns"""
        import re
        
        # Try different splitting methods based on content
        
        # Method 1: Pipe separators
        if '|' in line:
            parts = [part.strip() for part in line.split('|') if part.strip()]
            if len(parts) > 1:
                return parts
        
        # Method 2: Colon separators (key: value)
        if ':' in line and len(line.split(':', 1)) == 2:
            key, value = line.split(':', 1)
            return [key.strip(), value.strip()]
        
        # Method 3: Multiple spaces or tabs
        parts = re.split(r'\s{2,}|\t+', line)
        if len(parts) > 1:
            return [part.strip() for part in parts if part.strip()]
        
        # Method 4: Single spaces (fallback)
        parts = line.split()
        if len(parts) > 1:
            return parts
        
        # Method 5: Any non-empty content
        return [line.strip()] if line.strip() else []
    
    def _extract_single_value_tables(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract single value tables (like test results)"""
        try:
            tables = []
            current_table = None
            table_data = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Look for single value patterns (Name: Value or Name - Value)
                if ':' in line and len(line.split(':', 1)) == 2:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key and value:
                        if not current_table:
                            current_table = {
                                "type": "single_value_table",
                                "data": [['Parameter', 'Value']],
                                "confidence": 0.8,
                                "method": "single_value_extraction",
                                "title": "Single Values"
                            }
                            table_data = [['Parameter', 'Value']]
                        
                        table_data.append([key, value])
                
                # End of single value section
                elif current_table and not line:
                    if len(table_data) > 1:
                        current_table["data"] = table_data
                        tables.append(current_table)
                    current_table = None
                    table_data = []
            
            # Save last table if exists
            if current_table and len(table_data) > 1:
                current_table["data"] = table_data
                tables.append(current_table)
            
            return tables
            
        except Exception as e:
            self.log_step("Error extracting single value tables", "WARNING", str(e))
            return []
    
