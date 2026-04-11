"""
PDF Handwritten Content Processor
Handles PDFs with plain text + handwritten content using PyMuPDF + handwriting OCR
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any, List
import logging
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

from .base_processor import BaseProcessor
from config import settings

logger = logging.getLogger(__name__)

class PDFHandwrittenProcessor(BaseProcessor):
    """Processor for PDFs with plain text + handwritten content"""
    
    def __init__(self):
        super().__init__()
        self.processor_name = "PDFHandwrittenProcessor"
    
    def process(self, input_file: Path) -> Dict[str, Any]:
        """
        Process PDF file with handwritten content
        
        Args:
            input_file: Path to the PDF file
            
        Returns:
            Dictionary containing extracted data
        """
        self.log_step("Starting PDF handwritten content processing", "INFO", f"File: {input_file.name}")
        
        try:
            # First, try to extract plain text using PyMuPDF
            plain_text_data = self._extract_plain_text(input_file)
            
            # Convert PDF to images for handwritten content analysis
            images = self._convert_pdf_to_images(input_file)
            
            # Process each page for handwritten content
            handwritten_data = []
            for page_num, pil_image in enumerate(images):
                page_handwritten = self._process_handwritten_page(pil_image, page_num)
                handwritten_data.append(page_handwritten)
            
            # Combine plain text and handwritten content
            combined_data = self._combine_text_and_handwritten(plain_text_data, handwritten_data)
            
            # Post-process the extracted data
            combined_data = self._post_process_data(combined_data)
            
            self.log_step("PDF handwritten content processing completed", "SUCCESS", 
                         f"Extracted {len(combined_data.get('pages', []))} pages")
            
            return combined_data
            
        except Exception as e:
            self.log_step("PDF handwritten content processing failed", "ERROR", str(e))
            raise
    
    def _extract_plain_text(self, input_file: Path) -> Dict[str, Any]:
        """Extract plain text using PyMuPDF"""
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
                    "confidence": 1.0  # Plain text extraction is highly reliable
                }
                
                pages.append(page_data)
                self.log_step(f"Extracted plain text from page {page_num + 1}", "INFO", 
                             f"Text length: {len(text)}")
            
            doc.close()
            
            return {
                "pages": pages,
                "metadata": {
                    "processor": "PyMuPDF",
                    "total_pages": len(pages)
                }
            }
            
        except Exception as e:
            self.log_step("Plain text extraction failed", "WARNING", str(e))
            return {"pages": [], "metadata": {}}
    
    def _convert_pdf_to_images(self, input_file: Path) -> List[Image.Image]:
        """Convert PDF pages to PIL Images"""
        try:
            self.log_step("Converting PDF to images for handwritten analysis", "INFO", f"DPI: {settings.PDF_DPI}")
            
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
    
    def _process_handwritten_page(self, pil_image: Image.Image, page_num: int) -> Dict[str, Any]:
        """Process a single page for handwritten content"""
        try:
            # Convert PIL to OpenCV
            cv_image = self._pil_to_cv2(pil_image)
            
            # Detect handwritten regions
            handwritten_regions = self._detect_handwritten_regions(cv_image)
            
            # Extract handwritten text using specialized OCR
            handwritten_text = self._extract_handwritten_text(cv_image, handwritten_regions)
            
            # Detect annotations and comments
            annotations = self._detect_annotations(cv_image, handwritten_regions)
            
            page_data = {
                "page_number": page_num + 1,
                "handwritten_text": handwritten_text,
                "handwritten_regions": handwritten_regions,
                "annotations": annotations,
                "width": pil_image.width,
                "height": pil_image.height,
                "confidence": 0.7,  # Handwritten OCR has lower confidence
            }
            
            self.log_step(f"Processed handwritten content on page {page_num + 1}", "INFO", 
                         f"Handwritten regions: {len(handwritten_regions)}, Text: {len(handwritten_text)} chars")
            
            return page_data
            
        except Exception as e:
            self.log_step(f"Error processing handwritten content on page {page_num + 1}", "ERROR", str(e))
            return {
                "page_number": page_num + 1,
                "handwritten_text": "",
                "handwritten_regions": [],
                "annotations": [],
                "width": pil_image.width,
                "height": pil_image.height,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _detect_handwritten_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect handwritten regions using image processing techniques"""
        try:
            handwritten_regions = []
            
            # Convert to grayscale
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
    
    def _detect_annotations(self, image: np.ndarray, handwritten_regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect annotations and comments in the document"""
        try:
            annotations = []
            
            # Look for common annotation patterns
            # 1. Highlighted regions (yellow, pink, etc.)
            highlighted_regions = self._detect_highlighted_regions(image)
            annotations.extend(highlighted_regions)
            
            # 2. Underlined text
            underlined_regions = self._detect_underlined_text(image)
            annotations.extend(underlined_regions)
            
            # 3. Margin notes
            margin_notes = self._detect_margin_notes(image, handwritten_regions)
            annotations.extend(margin_notes)
            
            return annotations
            
        except Exception as e:
            self.log_step("Error detecting annotations", "WARNING", str(e))
            return []
    
    def _detect_highlighted_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect highlighted regions in the document"""
        try:
            annotations = []
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for common highlighters
            highlight_colors = [
                # Yellow highlighter
                (np.array([20, 100, 100]), np.array([30, 255, 255])),
                # Pink highlighter
                (np.array([160, 100, 100]), np.array([180, 255, 255])),
                # Green highlighter
                (np.array([40, 100, 100]), np.array([80, 255, 255]))
            ]
            
            for color_range in highlight_colors:
                mask = cv2.inRange(hsv, color_range[0], color_range[1])
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 500:  # Minimum area for highlight
                        x, y, w, h = cv2.boundingRect(contour)
                        annotations.append({
                            "type": "highlight",
                            "bbox": [x, y, x + w, y + h],
                            "area": area,
                            "confidence": min(area / 2000, 1.0)
                        })
            
            return annotations
            
        except Exception as e:
            self.log_step("Error detecting highlighted regions", "WARNING", str(e))
            return []
    
    def _detect_underlined_text(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect underlined text"""
        try:
            annotations = []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Detect horizontal lines (underlines)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                x, y, w, h = cv2.boundingRect(contour)
                
                # Underlines are typically long and thin
                if area > 100 and w > h * 3:
                    annotations.append({
                        "type": "underline",
                        "bbox": [x, y, x + w, y + h],
                        "area": area,
                        "confidence": min(area / 1000, 1.0)
                    })
            
            return annotations
            
        except Exception as e:
            self.log_step("Error detecting underlined text", "WARNING", str(e))
            return []
    
    def _detect_margin_notes(self, image: np.ndarray, handwritten_regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect margin notes and comments"""
        try:
            annotations = []
            height, width = image.shape[:2]
            
            # Define margin regions (left and right sides)
            left_margin = width * 0.1  # 10% from left
            right_margin = width * 0.9  # 90% from left
            
            for region in handwritten_regions:
                bbox = region["bbox"]
                x1, y1, x2, y2 = bbox
                
                # Check if region is in margin
                if x1 < left_margin or x2 > right_margin:
                    annotations.append({
                        "type": "margin_note",
                        "bbox": bbox,
                        "area": region.get("area", 0),
                        "confidence": region.get("confidence", 0.5)
                    })
            
            return annotations
            
        except Exception as e:
            self.log_step("Error detecting margin notes", "WARNING", str(e))
            return []
    
    def _combine_text_and_handwritten(self, plain_text_data: Dict[str, Any], handwritten_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine plain text and handwritten content"""
        try:
            pages = []
            
            # Get plain text pages
            plain_pages = plain_text_data.get("pages", [])
            
            # Combine with handwritten data
            for i, handwritten_page in enumerate(handwritten_data):
                plain_page = plain_pages[i] if i < len(plain_pages) else {
                    "page_number": i + 1,
                    "text": "",
                    "width": handwritten_page.get("width", 0),
                    "height": handwritten_page.get("height", 0),
                    "blocks": [],
                    "confidence": 0.0
                }
                
                # Combine the data
                combined_page = {
                    "page_number": i + 1,
                    "plain_text": plain_page.get("text", ""),
                    "handwritten_text": handwritten_page.get("handwritten_text", ""),
                    "combined_text": f"{plain_page.get('text', '')}\n\n[Handwritten]\n{handwritten_page.get('handwritten_text', '')}",
                    "width": plain_page.get("width", handwritten_page.get("width", 0)),
                    "height": plain_page.get("height", handwritten_page.get("height", 0)),
                    "plain_blocks": plain_page.get("blocks", []),
                    "handwritten_regions": handwritten_page.get("handwritten_regions", []),
                    "annotations": handwritten_page.get("annotations", []),
                    "confidence": max(plain_page.get("confidence", 0), handwritten_page.get("confidence", 0))
                }
                
                pages.append(combined_page)
            
            return {
                "pages": pages,
                "metadata": {
                    "processor": "PyMuPDF + Handwritten OCR",
                    "total_pages": len(pages),
                    "file_info": plain_text_data.get("metadata", {}).get("file_info", {})
                }
            }
            
        except Exception as e:
            self.log_step("Error combining text and handwritten content", "WARNING", str(e))
            return {"pages": [], "metadata": {}}
    
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
    
    def _post_process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process extracted data"""
        try:
            # Clean up text in each page
            for page in data.get("pages", []):
                # Clean and normalize plain text
                plain_text = page.get("plain_text", "")
                cleaned_plain_text = self._clean_text(plain_text)
                page["plain_text"] = cleaned_plain_text
                
                # Clean and normalize handwritten text
                handwritten_text = page.get("handwritten_text", "")
                cleaned_handwritten_text = self._clean_text(handwritten_text)
                page["handwritten_text"] = cleaned_handwritten_text
                
                # Update combined text
                page["combined_text"] = f"{cleaned_plain_text}\n\n[Handwritten]\n{cleaned_handwritten_text}"
                
                # Calculate text statistics
                page["text_stats"] = {
                    "plain_text_chars": len(cleaned_plain_text),
                    "handwritten_text_chars": len(cleaned_handwritten_text),
                    "total_chars": len(cleaned_plain_text) + len(cleaned_handwritten_text),
                    "plain_text_words": len(cleaned_plain_text.split()),
                    "handwritten_text_words": len(cleaned_handwritten_text.split()),
                    "total_words": len(cleaned_plain_text.split()) + len(cleaned_handwritten_text.split())
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
        
        total_plain_chars = sum(page.get("text_stats", {}).get("plain_text_chars", 0) for page in pages)
        total_handwritten_chars = sum(page.get("text_stats", {}).get("handwritten_text_chars", 0) for page in pages)
        total_chars = sum(page.get("text_stats", {}).get("total_chars", 0) for page in pages)
        total_plain_words = sum(page.get("text_stats", {}).get("plain_text_words", 0) for page in pages)
        total_handwritten_words = sum(page.get("text_stats", {}).get("handwritten_text_words", 0) for page in pages)
        total_words = sum(page.get("text_stats", {}).get("total_words", 0) for page in pages)
        total_annotations = sum(len(page.get("annotations", [])) for page in pages)
        total_handwritten_regions = sum(len(page.get("handwritten_regions", [])) for page in pages)
        
        return {
            "total_plain_text_characters": total_plain_chars,
            "total_handwritten_text_characters": total_handwritten_chars,
            "total_characters": total_chars,
            "total_plain_text_words": total_plain_words,
            "total_handwritten_text_words": total_handwritten_words,
            "total_words": total_words,
            "total_annotations": total_annotations,
            "total_handwritten_regions": total_handwritten_regions,
            "average_chars_per_page": total_chars / len(pages) if pages else 0,
            "average_words_per_page": total_words / len(pages) if pages else 0,
            "average_annotations_per_page": total_annotations / len(pages) if pages else 0,
            "average_handwritten_regions_per_page": total_handwritten_regions / len(pages) if pages else 0
        }
