"""Image extraction from PDF documents using PyMuPDF"""
import logging
import os
from typing import List, Dict, Any
import fitz  # PyMuPDF

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageExtractor:
    """Extract images from PDF documents"""
    
    def extract(self, pdf_path: str, output_dir: str) -> List[Dict[str, Any]]:
        """
        Extract images from PDF and save them to disk
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted images
            
        Returns:
            List of dictionaries with image metadata
            Format: [{"page": int, "image_id": int, "image_path": str}, ...]
        """
        extracted_data = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get PDF filename without extension for naming images
        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        
        try:
            # Open the PDF document
            doc = fitz.open(pdf_path)
            logger.info(f"Extracting images from PDF: {pdf_path} with {len(doc)} pages")
            
            # Extract images from each page
            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    image_list = page.get_images()
                    
                    if not image_list:
                        logger.info(f"No images found on page {page_num + 1}")
                        continue
                    
                    # Process each image on the page
                    for img_index, img in enumerate(image_list):
                        try:
                            xref = img[0]  # Image reference number
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]
                            
                            # Generate image filename
                            image_id = img_index + 1
                            image_filename = f"{pdf_filename}_page{page_num + 1}_img{image_id}.{image_ext}"
                            image_path = os.path.join(output_dir, image_filename)
                            
                            # Save image to disk
                            with open(image_path, "wb") as img_file:
                                img_file.write(image_bytes)
                            
                            extracted_data.append({
                                "page": page_num + 1,
                                "image_id": image_id,
                                "image_path": image_path
                            })
                            
                            logger.info(f"Saved image {image_id} from page {page_num + 1} to {image_path}")
                            
                        except Exception as e:
                            logger.error(f"Error extracting image {img_index + 1} from page {page_num + 1}: {str(e)}")
                            continue
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                    continue
            
            doc.close()
            logger.info(f"Image extraction complete: {len(extracted_data)} images extracted")
            
        except Exception as e:
            logger.error(f"Error opening PDF file {pdf_path}: {str(e)}")
            return []
        
        return extracted_data
