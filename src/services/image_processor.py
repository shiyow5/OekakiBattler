"""
Image processing service for character extraction and preprocessing
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional
import logging
from config.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handle image processing for character extraction"""
    
    def __init__(self):
        self.target_size = Settings.TARGET_IMAGE_SIZE
        self.supported_formats = Settings.SUPPORTED_FORMATS
        self.min_resolution = Settings.MIN_RESOLUTION
        
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image from file path"""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.error(f"Image file not found: {image_path}")
                return None
                
            if path.suffix.lower() not in self.supported_formats:
                logger.error(f"Unsupported format: {path.suffix}")
                return None
            
            # Load with OpenCV
            image = cv2.imread(str(path))
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            logger.info(f"Successfully loaded image: {image.shape}")
            return image
            
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    def extract_character(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract character from background using various techniques"""
        try:
            # Method 1: Try automatic background removal using GrabCut
            extracted = self._grabcut_extraction(image)
            if extracted is not None:
                logger.info("Character extracted using GrabCut")
                return extracted
            
            # Method 2: Try edge-based extraction
            extracted = self._edge_based_extraction(image)
            if extracted is not None:
                logger.info("Character extracted using edge detection")
                return extracted
            
            # Method 3: Fallback to simple thresholding
            extracted = self._threshold_extraction(image)
            logger.info("Character extracted using threshold method")
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting character: {e}")
            return None
    
    def _grabcut_extraction(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract character using GrabCut algorithm"""
        try:
            height, width = image.shape[:2]
            
            # Create rectangle for probable foreground (center 60% of image)
            margin_x, margin_y = int(width * 0.2), int(height * 0.2)
            rect = (margin_x, margin_y, width - 2*margin_x, height - 2*margin_y)
            
            # Initialize masks
            mask = np.zeros((height, width), np.uint8)
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)
            
            # Apply GrabCut
            cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
            
            # Create final mask
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            
            # Apply mask
            result = image * mask2[:, :, np.newaxis]
            
            # Convert to RGBA with transparency
            result_rgba = cv2.cvtColor(result, cv2.COLOR_RGB2RGBA)
            result_rgba[:, :, 3] = mask2 * 255
            
            return result_rgba
            
        except Exception as e:
            logger.warning(f"GrabCut extraction failed: {e}")
            return None
    
    def _edge_based_extraction(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract character using edge detection"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # Find largest contour (assumed to be main character)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Create mask from contour
            mask = np.zeros(gray.shape, np.uint8)
            cv2.fillPoly(mask, [largest_contour], 255)
            
            # Apply mask
            result = image.copy()
            result_rgba = cv2.cvtColor(result, cv2.COLOR_RGB2RGBA)
            result_rgba[:, :, 3] = mask
            
            return result_rgba
            
        except Exception as e:
            logger.warning(f"Edge-based extraction failed: {e}")
            return None
    
    def _threshold_extraction(self, image: np.ndarray) -> np.ndarray:
        """Simple threshold-based extraction (fallback method)"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold to separate foreground from background
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Morphological operations to clean up mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Apply mask
        result = image.copy()
        result_rgba = cv2.cvtColor(result, cv2.COLOR_RGB2RGBA)
        result_rgba[:, :, 3] = mask
        
        return result_rgba
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for AI analysis"""
        try:
            # Handle RGBA images
            if image.shape[2] == 4:
                # Convert to RGB with white background
                rgb_image = np.ones((image.shape[0], image.shape[1], 3), dtype=np.uint8) * 255
                alpha = image[:, :, 3] / 255.0
                for c in range(3):
                    rgb_image[:, :, c] = (1 - alpha) * 255 + alpha * image[:, :, c]
                image = rgb_image
            
            # Resize to target size
            image_resized = cv2.resize(image, self.target_size, interpolation=cv2.INTER_AREA)
            
            # Enhance contrast
            image_enhanced = self._enhance_contrast(image_resized)
            
            # Enhance line art
            image_enhanced = self._enhance_line_art(image_enhanced)
            
            logger.info(f"Image preprocessed to shape: {image_enhanced.shape}")
            return image_enhanced
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE"""
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            
            # Convert back to RGB
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            return enhanced
        except:
            return image
    
    def _enhance_line_art(self, image: np.ndarray) -> np.ndarray:
        """Enhance line art features"""
        try:
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Detect edges
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 10)
            
            # Convert back to 3 channels
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            
            # Combine with original image
            enhanced = cv2.addWeighted(image, 0.8, edges_colored, 0.2, 0)
            return enhanced
        except:
            return image
    
    def save_sprite(self, sprite: np.ndarray, output_path: str) -> bool:
        """Save extracted sprite to file"""
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to PIL Image for saving
            if sprite.shape[2] == 4:  # RGBA
                pil_image = Image.fromarray(sprite, 'RGBA')
            else:  # RGB
                pil_image = Image.fromarray(sprite, 'RGB')
            
            # Save as PNG to preserve transparency
            output_path_png = str(path.with_suffix('.png'))
            pil_image.save(output_path_png, 'PNG')
            
            logger.info(f"Sprite saved to: {output_path_png}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving sprite: {e}")
            return False
    
    def validate_image(self, image_path: str) -> Tuple[bool, str]:
        """Validate if image meets requirements"""
        try:
            path = Path(image_path)
            
            if not path.exists():
                return False, "File does not exist"
            
            if path.suffix.lower() not in self.supported_formats:
                return False, f"Unsupported format. Supported: {', '.join(self.supported_formats)}"
            
            # Check image dimensions
            with Image.open(path) as img:
                width, height = img.size
                if width < self.min_resolution[0] or height < self.min_resolution[1]:
                    return False, f"Image too small. Minimum: {self.min_resolution[0]}x{self.min_resolution[1]}"
            
            return True, "Image is valid"
            
        except Exception as e:
            return False, f"Error validating image: {e}"
    
    def process_character_image(self, input_path: str, output_dir: str, character_name: str) -> Tuple[bool, str, Optional[str]]:
        """Complete pipeline: load, extract, preprocess, and save character sprite"""
        try:
            # Validate input
            is_valid, message = self.validate_image(input_path)
            if not is_valid:
                return False, message, None
            
            # Load image
            image = self.load_image(input_path)
            if image is None:
                return False, "Failed to load image", None
            
            # Extract character
            extracted = self.extract_character(image)
            if extracted is None:
                return False, "Failed to extract character", None
            
            # Preprocess
            processed = self.preprocess_image(extracted)
            
            # Save sprite
            output_path = Path(output_dir) / f"{character_name}_sprite.png"
            if not self.save_sprite(processed, str(output_path)):
                return False, "Failed to save sprite", None
            
            return True, "Character processing completed successfully", str(output_path)
            
        except Exception as e:
            logger.error(f"Error in character processing pipeline: {e}")
            return False, f"Processing error: {e}", None