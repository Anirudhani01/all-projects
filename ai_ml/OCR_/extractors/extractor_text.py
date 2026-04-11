"""Text extraction from PDF documents using PyMuPDF"""
import logging
import os
from typing import List, Dict, Any
import fitz  # PyMuPDF

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextExtractor:
    """Extract textual content from PDF documents"""
    
    def extract(self, pdf_path: str, output_dir: str = None) -> List[Dict[str, Any]]:
        """
        Extract text from all pages of a PDF document
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted text files (optional)
            
        Returns:
            List of dictionaries with page numbers, text content, and file paths
            Format: [{"page": int, "text": str, "text_path": str}, ...]
        """
        extracted_data = []
        
        # Get PDF filename without extension for naming text files
        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Open the PDF document
            doc = fitz.open(pdf_path)
            logger.info(f"Opened PDF: {pdf_path} with {len(doc)} pages")
            
            # Extract text from each page
            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    text = page.get_text()
                    
                    # Only add pages with actual text content
                    if text.strip():
                        page_data = {
                            "page": page_num + 1,  # 1-indexed for user-friendliness
                            "text": text
                        }
                        
                        # Save text to file if output directory specified
                        if output_dir:
                            text_filename = f"{pdf_filename}_page{page_num + 1}.txt"
                            text_path = os.path.join(output_dir, text_filename)
                            
                            with open(text_path, 'w', encoding='utf-8') as f:
                                f.write(text)
                            
                            page_data["text_path"] = text_path
                            logger.info(f"Saved text from page {page_num + 1} to {text_path}")
                        else:
                            logger.info(f"Extracted text from page {page_num + 1}")
                        
                        extracted_data.append(page_data)
                    else:
                        logger.warning(f"Page {page_num + 1} contains no text")
                        
                except Exception as e:
                    logger.error(f"Error extracting text from page {page_num + 1}: {str(e)}")
                    continue
            
            doc.close()
            
            # Return metadata summary
            logger.info(f"Text extraction complete: {len(extracted_data)} pages with text")
            
        except Exception as e:
            logger.error(f"Error opening PDF file {pdf_path}: {str(e)}")
            raise
        
        return extracted_data
