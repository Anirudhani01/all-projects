"""
Image processing utilities
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

class ImageUtils:
    """Utility class for image processing operations"""
    
    @staticmethod
    def preprocess_image(image_path: Path) -> Optional[np.ndarray]:
        """Preprocess image for better OCR results"""
        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            return thresh
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            return None
    
    @staticmethod
    def enhance_image(image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better OCR"""
        try:
            # Apply morphological operations to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(cleaned, (1, 1), 0)
            
            return blurred
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image
    
    @staticmethod
    def detect_text_regions(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect text regions in image using contour detection"""
        try:
            # Find contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter out very small regions
                if w > 20 and h > 20:
                    text_regions.append((x, y, w, h))
            
            return text_regions
            
        except Exception as e:
            logger.error(f"Error detecting text regions: {e}")
            return []
    
    @staticmethod
    def resize_image(image: np.ndarray, max_width: int = 2000, max_height: int = 2000) -> np.ndarray:
        """Resize image while maintaining aspect ratio"""
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
            logger.error(f"Error resizing image: {e}")
            return image
    
    @staticmethod
    def convert_pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
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
            logger.error(f"Error converting PIL to OpenCV: {e}")
            return np.array(pil_image)
    
    @staticmethod
    def convert_cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
        """Convert OpenCV image to PIL format"""
        try:
            # Convert BGR to RGB for PIL
            if len(cv2_image.shape) == 3:
                rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = cv2_image
            
            return Image.fromarray(rgb_image)
            
        except Exception as e:
            logger.error(f"Error converting OpenCV to PIL: {e}")
            return Image.fromarray(cv2_image)
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: Path, quality: int = 95) -> bool:
        """Save image with specified quality"""
        try:
            # Convert to PIL for better quality control
            pil_image = ImageUtils.convert_cv2_to_pil(image)
            pil_image.save(output_path, quality=quality, optimize=True)
            return True
            
        except Exception as e:
            logger.error(f"Error saving image to {output_path}: {e}")
            return False
