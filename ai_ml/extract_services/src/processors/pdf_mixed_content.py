"""
PDF Mixed Content Processor
Handles PDFs with both text and images using PyMuPDF + OCR
"""
import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import cv2
import numpy as np
from PIL import Image
import pytesseract
import io

from .base_processor import BaseProcessor
from config import settings

logger = logging.getLogger(__name__)

class PDFMixedContentProcessor(BaseProcessor):
    """Processor for PDFs with mixed text and image content"""
    
    def __init__(self):
        super().__init__()
        self.processor_name = "PDFMixedContentProcessor"
    
    def process(self, input_file: Path) -> Dict[str, Any]:
        """
        Process PDF file with mixed content (text + images)
        
        Args:
            input_file: Path to the PDF file
            
        Returns:
            Dictionary containing extracted data
        """
        self.log_step("Starting PDF mixed content processing", "INFO", f"File: {input_file.name}")
        
        try:
            # Extract using PyMuPDF for better mixed content handling
            extracted_data = self._extract_with_pymupdf(input_file)
            
            # Post-process the extracted data
            extracted_data = self._post_process_data(extracted_data)
            
            self.log_step("PDF mixed content processing completed", "SUCCESS", 
                         f"Extracted {len(extracted_data.get('pages', []))} pages")
            
            return extracted_data
            
        except Exception as e:
            self.log_step("PDF mixed content processing failed", "ERROR", str(e))
            raise
    
    def _extract_with_pymupdf(self, input_file: Path) -> Dict[str, Any]:
        """Extract text and images using PyMuPDF"""
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
                
                # Extract images
                images = self._extract_images_from_page(page, page_num)
                
                # Process text blocks
                processed_blocks = self._process_text_blocks(blocks)
                
                # Extract tables from text
                tables = self._extract_tables_from_text(text, page_num)
                
                page_data = {
                    "page_number": page_num + 1,
                    "text": text,
                    "width": rect.width,
                    "height": rect.height,
                    "blocks": processed_blocks,
                    "images": images,
                    "tables": tables,
                    "confidence": 0.9  # Mixed content has slightly lower confidence
                }
                
                pages.append(page_data)
                self.log_step(f"Processed page {page_num + 1}", "INFO", 
                             f"Text: {len(text)} chars, Images: {len(images)}, Tables: {len(tables)}")
            
            doc.close()
            
            return {
                "pages": pages,
                "metadata": {
                    "processor": "PyMuPDF + OCR",
                    "total_pages": len(pages),
                    "file_info": {
                        "filename": input_file.name,
                        "file_size": input_file.stat().st_size
                    }
                }
            }
            
        except Exception as e:
            self.log_step("PyMuPDF mixed content extraction failed", "ERROR", str(e))
            raise
    
    def _extract_images_from_page(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Extract and process images from a PDF page"""
        images = []
        
        try:
            # Get image list
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(page.parent, xref)
                    
                    # Convert to PIL Image
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        pil_image = Image.open(io.BytesIO(img_data))
                        
                        # Convert to OpenCV format for processing
                        cv_image = self._pil_to_cv2(pil_image)
                        
                        # Preprocess image for OCR
                        processed_image = self._preprocess_image_for_ocr(cv_image)
                        
                        # Perform OCR on the image
                        ocr_text = self._perform_ocr(processed_image)
                        
                        # Detect tables in the image
                        table_data = self._detect_tables_in_image(processed_image)
                        
                        # Save intermediate image if needed
                        intermediate_path = None
                        if settings.KEEP_INTERMEDIATE_FILES:
                            intermediate_path = f"page_{page_num + 1}_image_{img_index + 1}.png"
                        
                        image_info = {
                            "image_index": img_index + 1,
                            "bbox": img[1:5] if len(img) > 4 else [0, 0, 0, 0],
                            "width": pil_image.width,
                            "height": pil_image.height,
                            "ocr_text": ocr_text,
                            "tables": table_data,
                            "confidence": 0.8,  # OCR confidence
                            "intermediate_file": intermediate_path
                        }
                        
                        images.append(image_info)
                        
                        # Save intermediate file if requested
                        if intermediate_path and settings.KEEP_INTERMEDIATE_FILES:
                            self._save_intermediate_image(processed_image, intermediate_path)
                        
                    pix = None  # Free memory
                    
                except Exception as e:
                    self.log_step(f"Error processing image {img_index + 1} on page {page_num + 1}", "WARNING", str(e))
                    continue
            
        except Exception as e:
            self.log_step(f"Error extracting images from page {page_num + 1}", "WARNING", str(e))
        
        return images
    
    def _pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format"""
        try:
            # Convert PIL to numpy array
            numpy_image = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV
            if len(numpy_image.shape) == 3:
                return cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
            else:
                return numpy_image
                
        except Exception as e:
            self.log_step("Error converting PIL to OpenCV", "WARNING", str(e))
            return np.array(pil_image)
    
    def _preprocess_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            self.log_step("Error preprocessing image for OCR", "WARNING", str(e))
            return image
    
    def _perform_ocr(self, image: np.ndarray) -> str:
        """Perform OCR on the image"""
        try:
            # Convert back to PIL for pytesseract
            pil_image = Image.fromarray(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(pil_image, config='--psm 6')
            
            return text.strip()
            
        except Exception as e:
            self.log_step("OCR failed", "WARNING", str(e))
            return ""
    
    def _detect_tables_in_image(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect tables in the image"""
        try:
            tables = []
            
            # Find horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            # Detect horizontal lines
            horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combine lines
            table_mask = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
            
            # Find contours (potential table cells)
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area and aspect ratio
            table_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Filter based on area and aspect ratio
                if area > 1000 and 0.1 < aspect_ratio < 10:
                    table_contours.append({
                        "bbox": [x, y, x + w, y + h],
                        "area": area,
                        "aspect_ratio": aspect_ratio
                    })
            
            # Group contours into potential tables
            if table_contours:
                tables.append({
                    "type": "detected_table",
                    "cells": table_contours,
                    "confidence": 0.7,
                    "method": "morphological_analysis"
                })
            
            return tables
            
        except Exception as e:
            self.log_step("Table detection failed", "WARNING", str(e))
            return []
    
    def _save_intermediate_image(self, image: np.ndarray, filename: str):
        """Save intermediate image file"""
        try:
            # This would be called from the main processing loop
            # The actual saving is handled by the base processor
            pass
        except Exception as e:
            self.log_step(f"Error saving intermediate image {filename}", "WARNING", str(e))
    
    def _extract_tables_from_text(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables from text using pattern matching"""
        try:
            tables = []
            
            # Simple table detection based on text patterns
            lines = text.split('\n')
            table_lines = []
            current_table = []
            
            for line in lines:
                # Check if line looks like a table row (contains multiple separators)
                if '|' in line or '\t' in line or (line.count('  ') > 2 and len(line.strip()) > 10):
                    current_table.append(line.strip())
                else:
                    if len(current_table) > 1:  # At least 2 rows for a table
                        table_data = self._parse_table_text(current_table)
                        if table_data:
                            tables.append({
                                "type": "text_table",
                                "data": table_data,
                                "confidence": 0.6,
                                "method": "pattern_matching"
                            })
                    current_table = []
            
            # Check for remaining table
            if len(current_table) > 1:
                table_data = self._parse_table_text(current_table)
                if table_data:
                    tables.append({
                        "type": "text_table",
                        "data": table_data,
                        "confidence": 0.6,
                        "method": "pattern_matching"
                    })
            
            # Enhanced structured table detection
            structured_tables = self._extract_structured_tables(text)
            tables.extend(structured_tables)
            
            return tables
            
        except Exception as e:
            self.log_step(f"Error extracting tables from text on page {page_num + 1}", "WARNING", str(e))
            return []
    
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
                
                # Start of differential section
                if 'DIFFERENTIAL' in line.upper() and 'LEUKOCYTE' in line.upper():
                    in_diff_section = True
                    # Add header row
                    table_data.append(['Cell Type', 'Result (%)', 'Normal Range (%)', 'Status'])
                    continue
                
                # End of differential section
                if in_diff_section and ('METHOD:' in line.upper() or 'NOTES:' in line.upper() or line.startswith('***')):
                    break
                
                # Extract differential rows
                if in_diff_section and line:
                    parts = self._parse_differential_line(line)
                    if parts:
                        table_data.append(parts)
            
            if len(table_data) > 1:  # Has header + data
                return {
                    "type": "medical_table",
                    "data": table_data,
                    "confidence": 0.9,
                    "method": "medical_differential_extraction",
                    "title": "Differential Leukocyte Count"
                }
            
            return None
            
        except Exception as e:
            self.log_step("Error extracting differential table", "WARNING", str(e))
            return None
    
    def _parse_medical_line(self, line: str) -> Optional[List[str]]:
        """Parse a medical report line to extract structured data"""
        try:
            # Look for patterns like "Hb (Hemoglobin) 8.7 g/dL 12.0 - 15.0 g/dL"
            import re
            
            # Pattern for medical values with units and ranges
            pattern = r'([A-Za-z\s\(\)]+?)\s+([0-9\.\-\s]+[A-Za-z\/%]+)\s+([0-9\.\-\s]+[A-Za-z\/%]+)'
            match = re.search(pattern, line)
            
            if match:
                investigation = match.group(1).strip()
                result = match.group(2).strip()
                reference_range = match.group(3).strip()
                
                # Determine status
                status = self._determine_medical_status(result, reference_range)
                
                return [investigation, result, reference_range, status]
            
            return None
            
        except Exception as e:
            return None
    
    def _parse_differential_line(self, line: str) -> Optional[List[str]]:
        """Parse a differential count line"""
        try:
            import re
            
            # Pattern for differential counts like "Neutrophils: 47.2 % (40 - 80%)"
            pattern = r'([A-Za-z]+):\s+([0-9\.]+)\s*%\s*\(([0-9\.\-\s]+)%\)'
            match = re.search(pattern, line)
            
            if match:
                cell_type = match.group(1).strip()
                result = match.group(2).strip() + ' %'
                normal_range = match.group(3).strip() + '%'
                
                # Determine status
                status = self._determine_medical_status(match.group(2), match.group(3))
                
                return [cell_type, result, normal_range, status]
            
            return None
            
        except Exception as e:
            return None
    
    def _determine_medical_status(self, result: str, reference_range: str) -> str:
        """Determine if medical value is normal, high, or low"""
        try:
            import re
            
            # Extract numeric value from result
            result_match = re.search(r'([0-9\.]+)', result)
            if not result_match:
                return "Unknown"
            
            result_value = float(result_match.group(1))
            
            # Extract range from reference
            range_match = re.search(r'([0-9\.]+)\s*-\s*([0-9\.]+)', reference_range)
            if not range_match:
                return "Unknown"
            
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            
            if result_value < min_val:
                return "Low"
            elif result_value > max_val:
                return "High"
            else:
                return "Normal"
                
        except Exception as e:
            return "Unknown"
    
    def _extract_single_test_results(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract single test results like HbA1c"""
        try:
            tables = []
            current_test = None
            test_data = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Look for test patterns
                if self._is_single_test_line(line):
                    # If we have a previous test, save it
                    if current_test and test_data:
                        table = self._create_single_test_table(current_test, test_data)
                        if table:
                            tables.append(table)
                    
                    # Start new test
                    current_test = self._extract_test_name(line)
                    test_data = [['Test Parameter', 'Result', 'Reference Range', 'Status']]
                    
                    # Extract result and range from the same line or next lines
                    result_info = self._extract_result_info(line, lines, i)
                    if result_info:
                        test_data.append(result_info)
                
                elif current_test and line and not line.startswith('***'):
                    # Try to extract additional info for current test
                    result_info = self._extract_result_info(line, lines, i)
                    if result_info:
                        test_data.append(result_info)
            
            # Save last test if exists
            if current_test and test_data:
                table = self._create_single_test_table(current_test, test_data)
                if table:
                    tables.append(table)
            
            return tables
            
        except Exception as e:
            self.log_step("Error extracting single test results", "WARNING", str(e))
            return []
    
    def _is_single_test_line(self, line: str) -> bool:
        """Check if line contains a single test result"""
        import re
        
        # Patterns for single test results
        patterns = [
            r'HbA1c.*\d+\.?\d*\s*%',  # HbA1c with percentage
            r'HbAlc.*\d+\.?\d*\s*%',   # HbAlc (typo variant)
            r'Result.*\d+\.?\d*\s*%',  # Result with percentage
            r'Biological Reference Interval',  # Reference interval line
        ]
        
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_test_name(self, line: str) -> str:
        """Extract test name from line"""
        import re
        
        # Look for HbA1c or similar
        if 'HBA1C' in line.upper() or 'HBALC' in line.upper():
            return 'HbA1c'
        elif 'RESULT' in line.upper():
            return 'Test Result'
        else:
            return 'Medical Test'
    
    def _extract_result_info(self, line: str, lines: List[str], current_index: int) -> Optional[List[str]]:
        """Extract result information from line and surrounding context"""
        try:
            import re
            
            # Look for HbA1c pattern: "5.9 %" and "4 - 6 %"
            hba1c_pattern = r'(\d+\.?\d*)\s*%'
            range_pattern = r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*%'
            
            # Check current line for result
            result_match = re.search(hba1c_pattern, line)
            range_match = re.search(range_pattern, line)
            
            if result_match and range_match:
                result_value = result_match.group(1) + ' %'
                min_range = range_match.group(1)
                max_range = range_match.group(2)
                reference_range = f"{min_range} - {max_range} %"
                
                # Determine status
                status = self._determine_medical_status(result_value, reference_range)
                
                return ['HbA1c', result_value, reference_range, status]
            
            # Check if this line has a result and next line has range
            elif result_match:
                result_value = result_match.group(1) + ' %'
                
                # Look ahead for range
                for j in range(current_index + 1, min(current_index + 3, len(lines))):
                    next_line = lines[j].strip()
                    range_match = re.search(range_pattern, next_line)
                    if range_match:
                        min_range = range_match.group(1)
                        max_range = range_match.group(2)
                        reference_range = f"{min_range} - {max_range} %"
                        status = self._determine_medical_status(result_value, reference_range)
                        return ['HbA1c', result_value, reference_range, status]
            
            return None
            
        except Exception as e:
            return None
    
    def _create_single_test_table(self, test_name: str, test_data: List[List[str]]) -> Optional[Dict[str, Any]]:
        """Create a table for single test results"""
        try:
            if len(test_data) > 1:  # Has header + data
                return {
                    "type": "medical_table",
                    "data": test_data,
                    "confidence": 0.8,
                    "method": "single_test_extraction",
                    "title": test_name
                }
            return None
            
        except Exception as e:
            return None
    
    def _parse_table_text(self, table_lines: List[str]) -> List[List[str]]:
        """Parse table text into structured data"""
        try:
            parsed_data = []
            
            for line in table_lines:
                # Try different separators
                if '|' in line:
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                elif '\t' in line:
                    cells = [cell.strip() for cell in line.split('\t') if cell.strip()]
                else:
                    # Try to split by multiple spaces
                    cells = [cell.strip() for cell in line.split('  ') if cell.strip()]
                
                if cells:
                    parsed_data.append(cells)
            
            return parsed_data
            
        except Exception as e:
            self.log_step("Error parsing table text", "WARNING", str(e))
            return []
    
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
                
                # Calculate text statistics
                page["text_stats"] = {
                    "char_count": len(cleaned_text),
                    "word_count": len(cleaned_text.split()),
                    "line_count": len(cleaned_text.split('\n')),
                    "paragraph_count": len([p for p in cleaned_text.split('\n\n') if p.strip()])
                }
                
                # Add OCR text from images to main text
                ocr_texts = []
                for image in page.get("images", []):
                    ocr_text = image.get("ocr_text", "")
                    if ocr_text.strip():
                        ocr_texts.append(ocr_text.strip())
                
                if ocr_texts:
                    page["ocr_text"] = "\n".join(ocr_texts)
                    page["combined_text"] = f"{cleaned_text}\n\n[OCR from images]\n{page['ocr_text']}"
                else:
                    page["combined_text"] = cleaned_text
            
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
        total_images = sum(len(page.get("images", [])) for page in pages)
        total_tables = sum(len(page.get("tables", [])) for page in pages)
        
        return {
            "total_characters": total_chars,
            "total_words": total_words,
            "total_lines": total_lines,
            "total_images": total_images,
            "total_tables": total_tables,
            "average_chars_per_page": total_chars / len(pages) if pages else 0,
            "average_words_per_page": total_words / len(pages) if pages else 0,
            "average_images_per_page": total_images / len(pages) if pages else 0,
            "average_tables_per_page": total_tables / len(pages) if pages else 0
        }
    
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
                
                # Look for table headers (lines with multiple columns separated by spaces/tabs)
                if self._is_table_header(line):
                    # Save previous table if exists
                    if current_table and len(table_data) > 1:
                        tables.append(current_table)
                    
                    # Start new table
                    current_table = {
                        "type": "data_table",
                        "data": [line.split()],
                        "confidence": 0.7,
                        "method": "data_table_extraction",
                        "title": f"Data Table {len(tables) + 1}"
                    }
                    table_data = [line.split()]
                    in_table = True
                    continue
                
                # Look for data rows (lines with multiple values)
                elif in_table and self._is_data_row(line):
                    row_data = self._parse_data_row(line)
                    if row_data:
                        table_data.append(row_data)
                
                # End of table (empty line or different pattern)
                elif in_table and (not line or not self._is_data_row(line)):
                    if current_table and len(table_data) > 1:
                        current_table["data"] = table_data
                        tables.append(current_table)
                    current_table = None
                    table_data = []
                    in_table = False
            
            # Save last table if exists
            if current_table and len(table_data) > 1:
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
        
        # Check for common header patterns
        header_patterns = [
            r'^[A-Z\s]+$',  # All caps words
            r'^[A-Za-z\s]+\s+[A-Za-z\s]+$',  # Multiple words
            r'.*\s+.*\s+.*',  # At least 3 parts
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _is_data_row(self, line: str) -> bool:
        """Check if line looks like a data row"""
        import re
        
        # Look for lines with multiple values (numbers, words, etc.)
        words = line.split()
        if len(words) < 2:
            return False
        
        # Check for data patterns (mix of text and numbers)
        has_text = any(re.search(r'[A-Za-z]', word) for word in words)
        has_numbers = any(re.search(r'[0-9]', word) for word in words)
        
        return has_text or has_numbers
    
    def _parse_data_row(self, line: str) -> List[str]:
        """Parse a data row into columns"""
        import re
        
        # Split by multiple spaces or tabs
        parts = re.split(r'\s{2,}|\t+', line)
        
        # If that doesn't work, try splitting by single spaces but be smarter
        if len(parts) < 2:
            parts = line.split()
        
        return [part.strip() for part in parts if part.strip()]
    
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
