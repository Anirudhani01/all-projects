"""
PDF Image Content Processor
Handles PDFs with image content containing tables/text using pdf2image + OCR
"""
from pathlib import Path
from typing import Dict, Any, List
import logging
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import camelot
import pandas as pd

from .base_processor import BaseProcessor
from config import settings

logger = logging.getLogger(__name__)

class PDFImageContentProcessor(BaseProcessor):
    """Processor for PDFs with image content (tables/text)"""
    
    def __init__(self):
        super().__init__()
        self.processor_name = "PDFImageContentProcessor"
    
    def process(self, input_file: Path) -> Dict[str, Any]:
        """
        Process PDF file with image content
        
        Args:
            input_file: Path to the PDF file
            
        Returns:
            Dictionary containing extracted data
        """
        self.log_step("Starting PDF image content processing", "INFO", f"File: {input_file.name}")
        
        try:
            # Convert PDF to images
            images = self._convert_pdf_to_images(input_file)
            
            # Process each page image
            pages = []
            for page_num, pil_image in enumerate(images):
                page_data = self._process_page_image(pil_image, page_num, input_file)
                pages.append(page_data)
            
            # Post-process the extracted data
            extracted_data = {
                "pages": pages,
                "metadata": {
                    "processor": "pdf2image + OCR + Table Detection",
                    "total_pages": len(pages),
                    "file_info": {
                        "filename": input_file.name,
                        "file_size": input_file.stat().st_size
                    }
                }
            }
            
            extracted_data = self._post_process_data(extracted_data)
            
            self.log_step("PDF image content processing completed", "SUCCESS", 
                         f"Extracted {len(pages)} pages")
            
            return extracted_data
            
        except Exception as e:
            self.log_step("PDF image content processing failed", "ERROR", str(e))
            raise
    
    def _convert_pdf_to_images(self, input_file: Path) -> List[Image.Image]:
        """Convert PDF pages to PIL Images"""
        try:
            self.log_step("Converting PDF to images", "INFO", f"DPI: {settings.PDF_DPI}")
            
            # Convert PDF to images using pdf2image
            images = convert_from_path(
                input_file,
                dpi=settings.PDF_DPI,
                first_page=1,
                last_page=None,  # All pages
                fmt='png',
                thread_count=1,  # Single thread for stability
                poppler_path=None  # Use system poppler
            )
            
            self.log_step(f"Converted PDF to {len(images)} images", "SUCCESS")
            return images
            
        except Exception as e:
            self.log_step("PDF to image conversion failed", "ERROR", str(e))
            raise
    
    def _process_page_image(self, pil_image: Image.Image, page_num: int, input_file: Path) -> Dict[str, Any]:
        """Process a single page image"""
        try:
            # Convert PIL to OpenCV
            cv_image = self._pil_to_cv2(pil_image)
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image_for_ocr(cv_image)
            
            # Perform OCR on the entire page
            ocr_text = self._perform_ocr(processed_image)
            
            # Detect and extract tables
            tables = self._extract_tables_from_image(processed_image, page_num, input_file)
            
            # Detect text regions for better organization
            text_regions = self._detect_text_regions(processed_image)
            
            # Save intermediate image if requested
            intermediate_path = None
            if settings.KEEP_INTERMEDIATE_FILES:
                intermediate_path = f"page_{page_num + 1}_processed.png"
                self._save_intermediate_image(processed_image, intermediate_path)
            
            page_data = {
                "page_number": page_num + 1,
                "text": ocr_text,
                "width": pil_image.width,
                "height": pil_image.height,
                "tables": tables,
                "text_regions": text_regions,
                "confidence": 0.8,  # OCR confidence
                "intermediate_file": intermediate_path
            }
            
            self.log_step(f"Processed page {page_num + 1}", "INFO", 
                         f"Text: {len(ocr_text)} chars, Tables: {len(tables)}")
            
            return page_data
            
        except Exception as e:
            self.log_step(f"Error processing page {page_num + 1}", "ERROR", str(e))
            return {
                "page_number": page_num + 1,
                "text": "",
                "width": pil_image.width,
                "height": pil_image.height,
                "tables": [],
                "text_regions": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
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
            
            # Resize image if too large
            gray = self._resize_image_if_needed(gray)
            
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
    
    def _resize_image_if_needed(self, image: np.ndarray, max_width: int = 2000, max_height: int = 2000) -> np.ndarray:
        """Resize image if it's too large"""
        try:
            height, width = image.shape[:2]
            
            # Calculate scaling factor
            scale_w = max_width / width
            scale_h = max_height / height
            scale = min(scale_w, scale_h, 1.0)  # Don't upscale
            
            if scale < 1.0:
                new_width = int(width * scale)
                new_height = int(height * scale)
                resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
                return resized
            
            return image
            
        except Exception as e:
            self.log_step("Error resizing image", "WARNING", str(e))
            return image
    
    def _perform_ocr(self, image: np.ndarray) -> str:
        """Perform OCR on the image"""
        try:
            # Convert back to PIL for pytesseract
            pil_image = Image.fromarray(image)
            
            # Perform OCR with different PSM modes for better results
            # PSM 6: Assume a single uniform block of text
            text = pytesseract.image_to_string(pil_image, config='--psm 6')
            
            # If no text found, try PSM 3 (Fully automatic page segmentation)
            if not text.strip():
                text = pytesseract.image_to_string(pil_image, config='--psm 3')
            
            return text.strip()
            
        except Exception as e:
            self.log_step("OCR failed", "WARNING", str(e))
            return ""
    
    def _extract_tables_from_image(self, image: np.ndarray, page_num: int, input_file: Path) -> List[Dict[str, Any]]:
        """Extract tables from the image using multiple methods"""
        tables = []
        
        try:
            # Method 1: Use Camelot for table detection
            camelot_tables = self._extract_tables_with_camelot(input_file, page_num + 1)
            tables.extend(camelot_tables)
            
            # Method 2: Use OpenCV for table detection
            cv_tables = self._detect_tables_with_opencv(image, page_num)
            tables.extend(cv_tables)
            
            # Method 3: Use OCR-based table detection
            ocr_tables = self._detect_tables_with_ocr(image, page_num)
            tables.extend(ocr_tables)
            
            # Method 4: Use simple text-based table detection as fallback
            if not tables:
                text_tables = self._extract_tables_from_text(image, page_num)
                tables.extend(text_tables)
            
            # Remove duplicates and merge similar tables
            tables = self._merge_similar_tables(tables)
            
            self.log_step(f"Found {len(tables)} tables on page {page_num + 1}", "INFO")
            
        except Exception as e:
            self.log_step(f"Error extracting tables from page {page_num + 1}", "WARNING", str(e))
        
        return tables
    
    def _extract_tables_with_camelot(self, input_file: Path, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables using Camelot"""
        try:
            # Use Camelot to extract tables from specific page
            tables = camelot.read_pdf(str(input_file), pages=str(page_num), flavor='lattice')
            
            camelot_tables = []
            for i, table in enumerate(tables):
                if not table.df.empty:
                    # Convert DataFrame to list of lists
                    table_data = table.df.values.tolist()
                    
                    # Clean up the data - remove empty rows and columns
                    cleaned_data = []
                    for row in table_data:
                        cleaned_row = [str(cell).strip() for cell in row if str(cell).strip()]
                        if cleaned_row:  # Only add non-empty rows
                            cleaned_data.append(cleaned_row)
                    
                    if cleaned_data:  # Only create table if we have data
                        camelot_tables.append({
                            "type": "camelot_table",
                            "data": cleaned_data,
                            "confidence": table.accuracy,
                            "method": "camelot_lattice",
                            "title": f"Camelot Table {i + 1}",
                            "bbox": [table._bbox[0], table._bbox[1], table._bbox[2], table._bbox[3]]
                        })
            
            return camelot_tables
            
        except Exception as e:
            self.log_step(f"Camelot table extraction failed for page {page_num}", "WARNING", str(e))
            return []
    
    def _detect_tables_with_opencv(self, image: np.ndarray, page_num: int) -> List[Dict[str, Any]]:
        """Detect tables using OpenCV morphological operations"""
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
                    "type": "opencv_table",
                    "cells": table_contours,
                    "confidence": 0.7,
                    "method": "morphological_analysis"
                })
            
            return tables
            
        except Exception as e:
            self.log_step(f"OpenCV table detection failed for page {page_num + 1}", "WARNING", str(e))
            return []
    
    def _detect_tables_with_ocr(self, image: np.ndarray, page_num: int) -> List[Dict[str, Any]]:
        """Detect tables using OCR text analysis"""
        try:
            tables = []
            
            # Convert image back to PIL for OCR
            pil_image = Image.fromarray(image)
            
            # Get simple text first for better structure detection
            simple_text = pytesseract.image_to_string(pil_image)
            
            if simple_text.strip():
                # Try to extract structured data from simple text
                structured_tables = self._extract_structured_tables_from_text(simple_text, page_num)
                tables.extend(structured_tables)
            
            # Also try detailed OCR for better accuracy
            ocr_data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            # Group words into potential table rows
            words = []
            for i in range(len(ocr_data['text'])):
                if int(ocr_data['conf'][i]) > 30:  # Confidence threshold
                    words.append({
                        'text': ocr_data['text'][i],
                        'x': ocr_data['left'][i],
                        'y': ocr_data['top'][i],
                        'w': ocr_data['width'][i],
                        'h': ocr_data['height'][i],
                        'conf': ocr_data['conf'][i]
                    })
            
            # Group words into rows based on y-coordinate
            rows = self._group_words_into_rows(words)
            
            # Convert rows to table data format with better organization
            table_data = []
            for row in rows:
                if len(row) >= 2:  # At least 2 columns for a table
                    # Extract text from each word in the row
                    row_text = []
                    for word in row:
                        if word['text'].strip():
                            row_text.append(word['text'].strip())
                    
                    if row_text and len(' '.join(row_text)) > 3:  # Only meaningful rows
                        table_data.append(row_text)
            
            # If we have table data, create a table
            if table_data:
                tables.append({
                    "type": "ocr_table",
                    "data": table_data,
                    "confidence": 0.7,
                    "method": "ocr_analysis",
                    "title": f"OCR Table {page_num + 1}"
                })
            
            return tables
            
        except Exception as e:
            self.log_step(f"OCR table detection failed for page {page_num + 1}", "WARNING", str(e))
            return []
    
    def _extract_tables_from_text(self, image: np.ndarray, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables using simple text analysis as fallback"""
        try:
            tables = []
            
            # Convert image back to PIL for OCR
            pil_image = Image.fromarray(image)
            
            # Get simple text from OCR
            text = pytesseract.image_to_string(pil_image)
            
            if not text.strip():
                return tables
            
            # Split text into lines
            lines = text.split('\n')
            
            # Look for table patterns in the text
            table_data = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line looks like table data (multiple values separated by spaces)
                words = line.split()
                if len(words) >= 2:
                    # Check if it looks like structured data
                    has_numbers = any(any(c.isdigit() for c in word) for word in words)
                    has_text = any(any(c.isalpha() for c in word) for word in words)
                    
                    if has_numbers or has_text:
                        table_data.append(words)
            
            # If we have table data, create a table
            if table_data:
                tables.append({
                    "type": "text_table",
                    "data": table_data,
                    "confidence": 0.5,
                    "method": "text_analysis",
                    "title": f"Text Table {page_num + 1}"
                })
            
            return tables
            
        except Exception as e:
            self.log_step(f"Text table extraction failed for page {page_num + 1}", "WARNING", str(e))
            return []
    
    def _extract_structured_tables_from_text(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Extract structured tables from OCR text using pattern matching"""
        try:
            tables = []
            
            if not text.strip():
                return tables
            
            # Split text into lines
            lines = text.split('\n')
            
            # Extract different types of structured data
            patient_info_table = self._extract_patient_info_table(lines)
            if patient_info_table:
                tables.append(patient_info_table)
            
            medical_history_table = self._extract_medical_history_table(lines)
            if medical_history_table:
                tables.append(medical_history_table)
            
            vital_signs_table = self._extract_vital_signs_table(lines)
            if vital_signs_table:
                tables.append(vital_signs_table)
            
            # Extract other structured data patterns
            other_tables = self._extract_other_structured_tables(lines)
            tables.extend(other_tables)
            
            return tables
            
        except Exception as e:
            self.log_step(f"Structured table extraction failed for page {page_num + 1}", "WARNING", str(e))
            return []
    
    def _is_structured_line(self, line: str) -> bool:
        """Check if a line looks like structured data"""
        import re
        
        # Look for patterns that suggest structured data
        patterns = [
            r'^[A-Za-z\s]+:\s*[A-Za-z0-9\s\-\.]+$',  # Key: Value pattern
            r'^[A-Za-z\s]+\s+[0-9]+',  # Text followed by numbers
            r'^[0-9]+\s+[A-Za-z\s]+',  # Numbers followed by text
            r'^[A-Za-z\s]+\s+[A-Za-z\s]+\s+[0-9]+',  # Multiple text fields with numbers
            r'^[A-Za-z\s]+\s+[0-9]+\s+[0-9]+',  # Text with multiple numbers
        ]
        
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        
        # Also check for lines with multiple meaningful parts
        parts = line.split()
        if len(parts) >= 2:
            has_text = any(any(c.isalpha() for c in part) for part in parts)
            has_numbers = any(any(c.isdigit() for c in part) for part in parts)
            return has_text and has_numbers
        
        return False
    
    def _parse_structured_line(self, line: str) -> List[str]:
        """Parse a structured line into columns"""
        import re
        
        # Try different parsing methods
        
        # Method 1: Key: Value pattern
        if ':' in line and len(line.split(':', 1)) == 2:
            key, value = line.split(':', 1)
            return [key.strip(), value.strip()]
        
        # Method 2: Multiple parts separated by spaces
        parts = line.split()
        if len(parts) >= 2:
            return [part.strip() for part in parts if part.strip()]
        
        # Method 3: Single value
        return [line.strip()]
    
    def _extract_patient_info_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Extract patient information table"""
        try:
            patient_data = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for patient information patterns
                if any(keyword in line.lower() for keyword in ['name:', 'uhid', 'age:', 'gender:', 'phone:', 'date:']):
                    # Parse the line
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            patient_data.append([key, value])
                    else:
                        # Try to extract structured data from the line
                        words = line.split()
                        if len(words) >= 2:
                            # Look for patterns like "Name: John Doe" or "UHID No: 12345"
                            if any(word.lower() in ['name', 'uhid', 'age', 'gender', 'phone', 'date'] for word in words):
                                patient_data.append(words)
            
            if patient_data:
                return {
                    "type": "patient_info_table",
                    "data": patient_data,
                    "confidence": 0.9,
                    "method": "patient_info_extraction",
                    "title": "Patient Information"
                }
            
            return None
            
        except Exception as e:
            self.log_step("Error extracting patient info table", "WARNING", str(e))
            return None
    
    def _extract_medical_history_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Extract medical history table"""
        try:
            history_data = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for medical history patterns
                if any(keyword in line.lower() for keyword in ['chief complaints', 'past history', 'personal history', 'family history', 'investigations']):
                    # Parse the line
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            history_data.append([key, value])
                    else:
                        # Try to extract structured data from the line
                        words = line.split()
                        if len(words) >= 2:
                            history_data.append(words)
            
            if history_data:
                return {
                    "type": "medical_history_table",
                    "data": history_data,
                    "confidence": 0.8,
                    "method": "medical_history_extraction",
                    "title": "Medical History"
                }
            
            return None
            
        except Exception as e:
            self.log_step("Error extracting medical history table", "WARNING", str(e))
            return None
    
    def _extract_vital_signs_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Extract vital signs table"""
        try:
            vital_data = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for vital signs patterns
                if any(keyword in line.lower() for keyword in ['bp:', 'pr:', 'hr:', 'weight:', 'temperature', 'pulse', 'blood pressure']):
                    # Parse the line
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            vital_data.append([key, value])
                    else:
                        # Try to extract structured data from the line
                        words = line.split()
                        if len(words) >= 2:
                            vital_data.append(words)
            
            if vital_data:
                return {
                    "type": "vital_signs_table",
                    "data": vital_data,
                    "confidence": 0.8,
                    "method": "vital_signs_extraction",
                    "title": "Vital Signs"
                }
            
            return None
            
        except Exception as e:
            self.log_step("Error extracting vital signs table", "WARNING", str(e))
            return None
    
    def _extract_other_structured_tables(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract other structured data patterns"""
        try:
            tables = []
            current_table = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line looks like structured data
                if self._is_structured_line(line):
                    current_table.append(self._parse_structured_line(line))
                else:
                    # If we have accumulated data and hit a non-structured line, save the table
                    if current_table and len(current_table) >= 2:
                        tables.append({
                            "type": "structured_table",
                            "data": current_table,
                            "confidence": 0.7,
                            "method": "text_pattern_matching",
                            "title": f"Structured Data {len(tables) + 1}"
                        })
                        current_table = []
            
            # Save the last table if exists
            if current_table and len(current_table) >= 2:
                tables.append({
                    "type": "structured_table",
                    "data": current_table,
                    "confidence": 0.7,
                    "method": "text_pattern_matching",
                    "title": f"Structured Data {len(tables) + 1}"
                })
            
            return tables
            
        except Exception as e:
            self.log_step("Error extracting other structured tables", "WARNING", str(e))
            return []
    
    def _group_words_into_rows(self, words: List[Dict]) -> List[List[Dict]]:
        """Group words into rows based on y-coordinate"""
        try:
            if not words:
                return []
            
            # Sort words by y-coordinate
            words.sort(key=lambda w: w['y'])
            
            rows = []
            current_row = [words[0]]
            y_threshold = 10  # Pixels
            
            for word in words[1:]:
                if abs(word['y'] - current_row[0]['y']) <= y_threshold:
                    current_row.append(word)
                else:
                    # Sort current row by x-coordinate
                    current_row.sort(key=lambda w: w['x'])
                    rows.append(current_row)
                    current_row = [word]
            
            # Add the last row
            if current_row:
                current_row.sort(key=lambda w: w['x'])
                rows.append(current_row)
            
            return rows
            
        except Exception as e:
            self.log_step("Error grouping words into rows", "WARNING", str(e))
            return []
    
    def _is_table_row(self, row: List[Dict]) -> bool:
        """Check if a row of words looks like a table row"""
        try:
            if len(row) < 2:
                return False
            
            # Check if words are roughly aligned in columns
            x_positions = [word['x'] for word in row]
            x_positions.sort()
            
            # Check for consistent spacing between columns
            if len(x_positions) > 1:
                gaps = [x_positions[i+1] - x_positions[i] for i in range(len(x_positions)-1)]
                avg_gap = sum(gaps) / len(gaps)
                
                # If gaps are relatively consistent, it might be a table
                if avg_gap > 20:  # Minimum gap between columns
                    return True
            
            return False
            
        except Exception as e:
            self.log_step("Error checking if row is table row", "WARNING", str(e))
            return False
    
    def _merge_similar_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge similar tables to avoid duplicates"""
        try:
            if len(tables) <= 1:
                return tables
            
            merged_tables = []
            used_indices = set()
            
            for i, table1 in enumerate(tables):
                if i in used_indices:
                    continue
                
                merged_table = table1.copy()
                used_indices.add(i)
                
                # Look for similar tables to merge
                for j, table2 in enumerate(tables[i+1:], i+1):
                    if j in used_indices:
                        continue
                    
                    if self._are_tables_similar(table1, table2):
                        # Merge table2 into merged_table
                        if 'data' in merged_table and 'data' in table2:
                            merged_table['data'].extend(table2['data'])
                        elif 'cells' in merged_table and 'cells' in table2:
                            merged_table['cells'].extend(table2['cells'])
                        
                        # Update confidence (average)
                        merged_table['confidence'] = (merged_table['confidence'] + table2['confidence']) / 2
                        used_indices.add(j)
                
                merged_tables.append(merged_table)
            
            return merged_tables
            
        except Exception as e:
            self.log_step("Error merging similar tables", "WARNING", str(e))
            return tables
    
    def _are_tables_similar(self, table1: Dict, table2: Dict) -> bool:
        """Check if two tables are similar enough to merge"""
        try:
            # Simple similarity check based on bbox overlap
            if 'bbox' in table1 and 'bbox' in table2:
                bbox1 = table1['bbox']
                bbox2 = table2['bbox']
                
                # Calculate overlap
                x1_overlap = max(bbox1[0], bbox2[0])
                y1_overlap = max(bbox1[1], bbox2[1])
                x2_overlap = min(bbox1[2], bbox2[2])
                y2_overlap = min(bbox1[3], bbox2[3])
                
                if x1_overlap < x2_overlap and y1_overlap < y2_overlap:
                    overlap_area = (x2_overlap - x1_overlap) * (y2_overlap - y1_overlap)
                    area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
                    area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
                    
                    # If overlap is significant, consider them similar
                    if overlap_area > 0.5 * min(area1, area2):
                        return True
            
            return False
            
        except Exception as e:
            self.log_step("Error checking table similarity", "WARNING", str(e))
            return False
    
    def _detect_text_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect text regions in the image"""
        try:
            # Find contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter out very small regions
                if w > 20 and h > 20:
                    text_regions.append({
                        "bbox": [x, y, x + w, y + h],
                        "area": w * h,
                        "aspect_ratio": w / h if h > 0 else 0
                    })
            
            return text_regions
            
        except Exception as e:
            self.log_step("Error detecting text regions", "WARNING", str(e))
            return []
    
    def _save_intermediate_image(self, image: np.ndarray, filename: str):
        """Save intermediate image file"""
        try:
            # This would be called from the main processing loop
            # The actual saving is handled by the base processor
            pass
        except Exception as e:
            self.log_step(f"Error saving intermediate image {filename}", "WARNING", str(e))
    
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
        total_tables = sum(len(page.get("tables", [])) for page in pages)
        total_text_regions = sum(len(page.get("text_regions", [])) for page in pages)
        
        return {
            "total_characters": total_chars,
            "total_words": total_words,
            "total_lines": total_lines,
            "total_tables": total_tables,
            "total_text_regions": total_text_regions,
            "average_chars_per_page": total_chars / len(pages) if pages else 0,
            "average_words_per_page": total_words / len(pages) if pages else 0,
            "average_tables_per_page": total_tables / len(pages) if pages else 0,
            "average_text_regions_per_page": total_text_regions / len(pages) if pages else 0
        }
