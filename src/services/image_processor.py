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
        self.max_size = Settings.MAX_IMAGE_SIZE
        self.supported_formats = Settings.SUPPORTED_FORMATS
        self.min_resolution = Settings.MIN_RESOLUTION
        
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image from file path"""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.error(f"Image file not found: {image_path}")
                return None

            # Check file size
            file_size = path.stat().st_size
            if file_size == 0:
                logger.error(f"Image file is empty: {image_path}")
                return None
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                logger.error(f"Image file too large ({file_size} bytes): {image_path}")
                return None

            if path.suffix.lower() not in self.supported_formats:
                logger.error(f"Unsupported format: {path.suffix}")
                return None

            # Load with OpenCV
            image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
            if image is None:
                logger.error(f"Failed to load image with OpenCV: {image_path}")
                # Try with PIL as fallback
                try:
                    from PIL import Image
                    pil_image = Image.open(path)
                    image = np.array(pil_image)
                    if len(image.shape) == 2:  # Grayscale
                        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                    elif image.shape[2] == 4:  # RGBA
                        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
                    logger.info(f"Loaded image with PIL fallback: {image.shape}")
                except Exception as pil_error:
                    logger.error(f"PIL fallback also failed: {pil_error}")
                    return None
            else:
                # Convert BGR to RGB if needed
                if len(image.shape) == 3 and image.shape[2] == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                elif len(image.shape) == 3 and image.shape[2] == 4:
                    image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)

            logger.info(f"Successfully loaded image: {image.shape}")
            return image

        except Exception as e:
            logger.error(f"Error loading image: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def extract_character(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract character from white background using simple threshold"""
        try:
            # Convert RGB to BGR for OpenCV processing
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Convert to grayscale
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

            # Threshold to create mask (assuming white background)
            _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

            # Apply mask to create result
            result = cv2.bitwise_and(image_bgr, image_bgr, mask=mask)

            # Split channels and add alpha channel for transparency
            b, g, r = cv2.split(result)
            alpha = mask
            rgba = cv2.merge([r, g, b, alpha])  # Convert back to RGB order

            logger.info("Character extracted using simple threshold method")
            return rgba

        except Exception as e:
            logger.error(f"Error extracting character: {e}")
            return None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for AI analysis while preserving aspect ratio"""
        try:
            # Check if image has alpha channel
            has_alpha = image.shape[2] == 4

            # Store alpha channel if present
            if has_alpha:
                alpha_channel = image[:, :, 3]
                rgb_image = image[:, :, :3]
            else:
                rgb_image = image

            # Calculate new size while preserving aspect ratio
            height, width = rgb_image.shape[:2]
            if width > height:
                if width > self.max_size:
                    new_width = self.max_size
                    new_height = int(height * (self.max_size / width))
                else:
                    new_width = width
                    new_height = height
            else:
                if height > self.max_size:
                    new_height = self.max_size
                    new_width = int(width * (self.max_size / height))
                else:
                    new_width = width
                    new_height = height

            # Resize to new size while preserving aspect ratio
            if new_width != width or new_height != height:
                image_resized = cv2.resize(rgb_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logger.info(f"Resized from {width}x{height} to {new_width}x{new_height} (aspect ratio preserved)")
            else:
                image_resized = rgb_image
                logger.info(f"Image size {width}x{height} is within limits, no resizing needed")

            # Resize alpha channel if present
            if has_alpha and (new_width != width or new_height != height):
                alpha_resized = cv2.resize(alpha_channel, (new_width, new_height), interpolation=cv2.INTER_AREA)
            elif has_alpha:
                alpha_resized = alpha_channel

            # Enhance contrast
            image_enhanced = self._enhance_contrast(image_resized)

            # Enhance line art
            image_enhanced = self._enhance_line_art(image_enhanced)

            # Restore alpha channel if present
            if has_alpha:
                # Merge RGB with alpha
                image_enhanced = np.dstack([image_enhanced, alpha_resized])

            logger.info(f"Image preprocessed to shape: {image_enhanced.shape}")
            return image_enhanced

        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image
    
    def save_image(self, image: np.ndarray, output_path: str) -> bool:
        """Save image to file"""
        try:
            # Handle different image formats
            if len(image.shape) == 3 and image.shape[2] == 4:
                # RGBA image
                from PIL import Image
                pil_image = Image.fromarray(image, 'RGBA')
                pil_image.save(output_path)
            else:
                # RGB image
                # Convert RGB to BGR for OpenCV
                if len(image.shape) == 3:
                    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                else:
                    image_bgr = image
                cv2.imwrite(output_path, image_bgr)
            
            logger.info(f"Image saved to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False
    
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
        """Save extracted sprite to file with transparency"""
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Ensure output is PNG format for transparency support
            output_path_png = str(path.with_suffix('.png'))

            # Convert to PIL Image for saving
            if len(sprite.shape) == 3 and sprite.shape[2] == 4:  # RGBA
                pil_image = Image.fromarray(sprite, 'RGBA')
                logger.info(f"Saving sprite with transparency (RGBA)")
            else:  # RGB
                pil_image = Image.fromarray(sprite, 'RGB')
                logger.info(f"Saving sprite without transparency (RGB)")

            # Save as PNG with optimization
            pil_image.save(output_path_png, 'PNG', optimize=True)

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

            # Save sprite with transparency
            output_path = Path(output_dir) / f"{character_name}_sprite.png"
            if not self.save_sprite(processed, str(output_path)):
                return False, "Failed to save sprite", None

            return True, "Character processing completed successfully", str(output_path)

        except Exception as e:
            logger.error(f"Error in character processing pipeline: {e}")
            return False, f"Processing error: {e}", None