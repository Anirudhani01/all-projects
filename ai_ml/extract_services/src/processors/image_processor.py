"""
Image Processor
Handles image files with text/tables using OpenCV + OCR
"""
from pathlib import Path
from typing import Dict, Any, List
import logging
import cv2
import numpy as np
from PIL import Image
import pytesseract
import camelot
import pandas as pd

from .base_processor import BaseProcessor
from config import settings

logger = logging.getLogger(__name__)

class ImageProcessor(BaseProcessor):
    """Processor for image files with text/tables"""
    
    def __init__(self):
        super().__init__()
        self.processor_name = "ImageProcessor"
    
    def process(self, input_file: Path) -> Dict[str, Any]:
        """
        Process image file with text/tables
        
        Args:
            input_file: Path to the image file
            
        Returns:
            Dictionary containing extracted data
        """
        self.log_step("Starting image processing", "INFO", f"File: {input_file.name}")
        
        try:
            # Load and preprocess the image
            image = self._load_image(input_file)
            
            # Process the image
            page_data = self._process_image(image, input_file)
            
            # Post-process the extracted data
            extracted_data = {
                "pages": [page_data],
                "metadata": {
                    "processor": "OpenCV + OCR + Table Detection",
                    "total_pages": 1,
                    "file_info": {
                        "filename": input_file.name,
                        "file_size": input_file.stat().st_size
                    }
                }
            }
            
            extracted_data = self._post_process_data(extracted_data)
            
            self.log_step("Image processing completed", "SUCCESS", 
                         f"Text: {len(page_data.get('text', ''))} chars, Tables: {len(page_data.get('tables', []))}")
            
            return extracted_data
            
        except Exception as e:
            self.log_step("Image processing failed", "ERROR", str(e))
            raise
    
    def _load_image(self, input_file: Path) -> np.ndarray:
        """Load image from file"""
        try:
            # Load image using OpenCV
            image = cv2.imread(str(input_file))
            
            if image is None:
                raise ValueError(f"Could not load image: {input_file}")
            
            self.log_step(f"Loaded image: {image.shape[1]}x{image.shape[0]} pixels", "INFO")
            return image
            
        except Exception as e:
            self.log_step("Error loading image", "ERROR", str(e))
            raise
    
    def _process_image(self, image: np.ndarray, input_file: Path) -> Dict[str, Any]:
        """Process a single image for text and tables"""
        try:
            # Preprocess image for better OCR
            processed_image = self._preprocess_image_for_ocr(image)
            
            # Perform OCR on the entire image
            ocr_text = self._perform_ocr(processed_image)
            
            # Detect and extract tables
            tables = self._extract_tables_from_image(processed_image, input_file)
            
            # Detect text regions for better organization
            text_regions = self._detect_text_regions(processed_image)
            
            # Detect handwritten regions (if any)
            handwritten_regions = self._detect_handwritten_regions(processed_image)
            
            # Extract handwritten text if regions found
            handwritten_text = ""
            if handwritten_regions:
                handwritten_text = self._extract_handwritten_text(processed_image, handwritten_regions)
            
            # Save intermediate image if requested
            intermediate_path = None
            if settings.KEEP_INTERMEDIATE_FILES:
                intermediate_path = f"processed_{input_file.stem}.png"
                self._save_intermediate_image(processed_image, intermediate_path)
            
            page_data = {
                "page_number": 1,
                "text": ocr_text,
                "handwritten_text": handwritten_text,
                "width": image.shape[1],
                "height": image.shape[0],
                "tables": tables,
                "text_regions": text_regions,
                "handwritten_regions": handwritten_regions,
                "confidence": 0.8,  # OCR confidence
                "intermediate_file": intermediate_path
            }
            
            self.log_step("Processed image", "INFO", 
                         f"Text: {len(ocr_text)} chars, Tables: {len(tables)}, Handwritten: {len(handwritten_text)} chars")
            
            return page_data
            
        except Exception as e:
            self.log_step(f"Error processing image", "ERROR", str(e))
            return {
                "page_number": 1,
                "text": "",
                "handwritten_text": "",
                "width": image.shape[1] if image is not None else 0,
                "height": image.shape[0] if image is not None else 0,
                "tables": [],
                "text_regions": [],
                "handwritten_regions": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
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
    
    def _extract_tables_from_image(self, image: np.ndarray, input_file: Path) -> List[Dict[str, Any]]:
        """Extract tables from the image using multiple methods"""
        tables = []
        
        try:
            # Method 1: Use OpenCV for table detection
            cv_tables = self._detect_tables_with_opencv(image)
            tables.extend(cv_tables)
            
            # Method 2: Use OCR-based table detection
            ocr_tables = self._detect_tables_with_ocr(image)
            tables.extend(ocr_tables)
            
            # Method 3: Try Camelot if it's a PDF (convert image to PDF first)
            # This is a fallback method
            try:
                camelot_tables = self._extract_tables_with_camelot(input_file)
                tables.extend(camelot_tables)
            except:
                pass  # Camelot might not work with image files
            
            # Remove duplicates and merge similar tables
            tables = self._merge_similar_tables(tables)
            
            self.log_step(f"Found {len(tables)} tables", "INFO")
            
        except Exception as e:
            self.log_step(f"Error extracting tables", "WARNING", str(e))
        
        return tables
    
    def _detect_tables_with_opencv(self, image: np.ndarray) -> List[Dict[str, Any]]:
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
            self.log_step(f"OpenCV table detection failed", "WARNING", str(e))
            return []
    
    def _detect_tables_with_ocr(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect tables using OCR text analysis"""
        try:
            tables = []
            
            # Convert image back to PIL for OCR
            pil_image = Image.fromarray(image)
            
            # Get detailed OCR data with bounding boxes
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
            
            # Detect table patterns
            table_rows = []
            for row in rows:
                if len(row) >= 3:  # At least 3 columns for a table
                    # Check if words are aligned in columns
                    if self._is_table_row(row):
                        table_rows.append(row)
            
            # Group consecutive table rows
            if table_rows:
                tables.append({
                    "type": "ocr_table",
                    "data": table_rows,
                    "confidence": 0.6,
                    "method": "ocr_analysis"
                })
            
            return tables
            
        except Exception as e:
            self.log_step(f"OCR table detection failed", "WARNING", str(e))
            return []
    
    def _extract_tables_with_camelot(self, input_file: Path) -> List[Dict[str, Any]]:
        """Extract tables using Camelot (fallback method)"""
        try:
            # This method might not work with image files directly
            # It's included as a fallback for potential PDF conversion
            return []
            
        except Exception as e:
            self.log_step(f"Camelot table extraction failed", "WARNING", str(e))
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
    
    def _detect_handwritten_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect handwritten regions using image processing techniques"""
        try:
            handwritten_regions = []
            
            # Convert to grayscale if needed
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Apply edge detection to find handwritten strokes
            edges = cv2.Canny(gray, 50, 150)
            
            # Apply morphological operations to connect handwritten strokes
            kernel = np.ones((3, 3), np.uint8)
            closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter based on area and aspect ratio (handwritten text characteristics)
                if area > 100 and w > 20 and h > 20:
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Handwritten text typically has irregular shapes
                    if 0.1 < aspect_ratio < 10:
                        handwritten_regions.append({
                            "bbox": [x, y, x + w, y + h],
                            "area": area,
                            "aspect_ratio": aspect_ratio,
                            "confidence": min(area / 1000, 1.0)  # Confidence based on size
                        })
            
            return handwritten_regions
            
        except Exception as e:
            self.log_step("Error detecting handwritten regions", "WARNING", str(e))
            return []
    
    def _extract_handwritten_text(self, image: np.ndarray, handwritten_regions: List[Dict[str, Any]]) -> str:
        """Extract text from handwritten regions using specialized OCR"""
        try:
            all_text = []
            
            for region in handwritten_regions:
                bbox = region["bbox"]
                x1, y1, x2, y2 = bbox
                
                # Extract region from image
                region_image = image[y1:y2, x1:x2]
                
                if region_image.size == 0:
                    continue
                
                # Preprocess region for handwritten OCR
                processed_region = self._preprocess_handwritten_region(region_image)
                
                # Perform OCR with handwriting-optimized settings
                text = self._perform_handwritten_ocr(processed_region)
                
                if text.strip():
                    all_text.append(text.strip())
            
            return "\n".join(all_text)
            
        except Exception as e:
            self.log_step("Error extracting handwritten text", "WARNING", str(e))
            return ""
    
    def _preprocess_handwritten_region(self, region_image: np.ndarray) -> np.ndarray:
        """Preprocess handwritten region for better OCR"""
        try:
            # Convert to grayscale if needed
            if len(region_image.shape) == 3:
                gray = cv2.cvtColor(region_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = region_image
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up handwritten strokes
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            self.log_step("Error preprocessing handwritten region", "WARNING", str(e))
            return region_image
    
    def _perform_handwritten_ocr(self, image: np.ndarray) -> str:
        """Perform OCR optimized for handwritten text"""
        try:
            # Convert to PIL for pytesseract
            pil_image = Image.fromarray(image)
            
            # Use PSM 8 (Single word) for handwritten text
            text = pytesseract.image_to_string(pil_image, config='--psm 8')
            
            # If no text found, try PSM 7 (Single text line)
            if not text.strip():
                text = pytesseract.image_to_string(pil_image, config='--psm 7')
            
            # If still no text, try PSM 13 (Raw line. Treat the image as a single text line)
            if not text.strip():
                text = pytesseract.image_to_string(pil_image, config='--psm 13')
            
            return text.strip()
            
        except Exception as e:
            self.log_step("Handwritten OCR failed", "WARNING", str(e))
            return ""
    
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
                
                # Clean and normalize handwritten text
                handwritten_text = page.get("handwritten_text", "")
                cleaned_handwritten_text = self._clean_text(handwritten_text)
                page["handwritten_text"] = cleaned_handwritten_text
                
                # Calculate text statistics
                page["text_stats"] = {
                    "char_count": len(cleaned_text),
                    "word_count": len(cleaned_text.split()),
                    "line_count": len(cleaned_text.split('\n')),
                    "paragraph_count": len([p for p in cleaned_text.split('\n\n') if p.strip()]),
                    "handwritten_char_count": len(cleaned_handwritten_text),
                    "handwritten_word_count": len(cleaned_handwritten_text.split())
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
        total_handwritten_chars = sum(page.get("text_stats", {}).get("handwritten_char_count", 0) for page in pages)
        total_handwritten_regions = sum(len(page.get("handwritten_regions", [])) for page in pages)
        
        return {
            "total_characters": total_chars,
            "total_words": total_words,
            "total_lines": total_lines,
            "total_tables": total_tables,
            "total_text_regions": total_text_regions,
            "total_handwritten_characters": total_handwritten_chars,
            "total_handwritten_regions": total_handwritten_regions,
            "average_chars_per_page": total_chars / len(pages) if pages else 0,
            "average_words_per_page": total_words / len(pages) if pages else 0,
            "average_tables_per_page": total_tables / len(pages) if pages else 0,
            "average_text_regions_per_page": total_text_regions / len(pages) if pages else 0
        }
