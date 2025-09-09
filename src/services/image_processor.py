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
            # Method 1: Try white background removal (assuming white background)
            extracted = self._white_background_extraction(image)
            if extracted is not None:
                logger.info("Character extracted using white background removal")
                return extracted
            
            # Method 2: Try automatic background removal using GrabCut
            extracted = self._grabcut_extraction(image)
            if extracted is not None:
                logger.info("Character extracted using GrabCut")
                return extracted
            
            # Method 3: Try edge-based extraction
            extracted = self._edge_based_extraction(image)
            if extracted is not None:
                logger.info("Character extracted using edge detection")
                return extracted
            
            # Method 4: Fallback to simple thresholding
            extracted = self._threshold_extraction(image)
            logger.info("Character extracted using threshold method")
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting character: {e}")
            return None
    
    def _white_background_extraction(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract character assuming white background using advanced color analysis"""
        try:
            height, width = image.shape[:2]
            
            # Convert to different color spaces for better analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            
            # Create multiple masks using different approaches
            masks = []
            
            # Method 1: RGB distance from white with adaptive threshold
            # Calculate distance from white (255, 255, 255)
            white_dist = np.sqrt(np.sum((image.astype(float) - 255) ** 2, axis=2))
            # Use Otsu's method to find optimal threshold
            _, white_mask1 = cv2.threshold(white_dist.astype(np.uint8), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            masks.append(white_mask1)
            
            # Method 2: HSV-based detection (low saturation = whitish)
            # White has very low saturation, so high saturation = foreground
            saturation = hsv[:, :, 1]
            _, white_mask2 = cv2.threshold(saturation, 20, 255, cv2.THRESH_BINARY)  # High saturation = foreground
            masks.append(white_mask2)
            
            # Method 3: LAB color space - detect non-white areas
            L, a, b = cv2.split(lab)
            # Non-white has lower L value or a,b far from neutral (128)
            lab_dist = np.sqrt((a.astype(float) - 128) ** 2 + (b.astype(float) - 128) ** 2)
            non_white_condition = (L < 220) | (lab_dist > 15)
            white_mask3 = non_white_condition.astype(np.uint8) * 255
            masks.append(white_mask3)
            
            # Method 4: Edge-enhanced mask to preserve fine details
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            # Dilate edges to ensure they're included
            kernel = np.ones((3, 3), np.uint8)
            edges_dilated = cv2.dilate(edges, kernel, iterations=1)
            
            # Combine all masks using voting
            combined_mask = np.zeros_like(masks[0])
            for mask in masks:
                combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Add edge information to preserve details
            combined_mask = cv2.bitwise_or(combined_mask, edges_dilated)
            
            # Clean up the mask with morphological operations
            kernel_small = np.ones((3, 3), np.uint8)
            kernel_medium = np.ones((5, 5), np.uint8)
            
            # Remove noise (small white spots)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel_small)
            # Fill holes in characters
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel_medium)
            # Remove small noise
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel_small)
            
            # Quality check
            foreground_ratio = np.sum(combined_mask > 0) / combined_mask.size
            logger.info(f"White background extraction foreground ratio: {foreground_ratio:.3f}")
            
            # First, check if most of the image perimeter is white-ish (good sign for white background)
            perimeter_white_ratio = self._check_perimeter_whiteness(image)
            logger.info(f"Perimeter whiteness ratio: {perimeter_white_ratio:.3f}")
            
            # Adjust thresholds based on perimeter whiteness
            if perimeter_white_ratio > 0.7:  # Likely white background
                # Allow higher foreground ratio for white background images
                if foreground_ratio < 0.03:
                    logger.warning("White background extraction: too little foreground detected")
                    return None
                if foreground_ratio > 0.95:
                    logger.warning("White background extraction: almost entire image is foreground")
                    return None
            else:
                # Stricter limits for non-white background
                if foreground_ratio < 0.05:
                    logger.warning("White background extraction: too little foreground detected")
                    return None
                if foreground_ratio > 0.75:
                    logger.warning("White background extraction: too much foreground detected (might not be white background)")
                    return None
            
            # Find the largest connected component to remove small artifacts
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(combined_mask, 8, cv2.CV_32S)
            if num_labels > 1:  # 0 is background
                # Find largest component (excluding background)
                largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
                combined_mask = (labels == largest_label).astype(np.uint8) * 255
            
            # Create RGBA result
            result_rgba = np.zeros((height, width, 4), dtype=np.uint8)
            result_rgba[:, :, :3] = image
            result_rgba[:, :, 3] = combined_mask
            
            logger.info("White background extraction successful")
            return result_rgba
            
        except Exception as e:
            logger.error(f"Error in white background extraction: {e}")
            return None
    
    def _check_perimeter_whiteness(self, image: np.ndarray) -> float:
        """Check how white the perimeter of the image is"""
        try:
            height, width = image.shape[:2]
            perimeter_pixels = []
            
            # Top and bottom edges
            perimeter_pixels.extend(image[0, :].reshape(-1, 3))  # top row
            perimeter_pixels.extend(image[-1, :].reshape(-1, 3))  # bottom row
            
            # Left and right edges (excluding corners already included)
            perimeter_pixels.extend(image[1:-1, 0].reshape(-1, 3))  # left column
            perimeter_pixels.extend(image[1:-1, -1].reshape(-1, 3))  # right column
            
            perimeter_pixels = np.array(perimeter_pixels)
            
            # Calculate distance from white for each perimeter pixel
            white_distances = np.sqrt(np.sum((perimeter_pixels.astype(float) - 255) ** 2, axis=1))
            
            # Count pixels that are close to white (distance < 30)
            white_count = np.sum(white_distances < 30)
            total_count = len(perimeter_pixels)
            
            return white_count / total_count if total_count > 0 else 0
            
        except Exception as e:
            logger.error(f"Error checking perimeter whiteness: {e}")
            return 0
    
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
            
            # Quality check: ensure enough foreground pixels
            foreground_ratio = np.sum(mask2) / (height * width)
            if foreground_ratio < 0.05 or foreground_ratio > 0.95:
                logger.warning(f"GrabCut extraction quality poor: foreground ratio {foreground_ratio:.3f}")
                return None
            
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
            
            # Quality check: ensure contour is reasonable size
            contour_area = cv2.contourArea(largest_contour)
            total_area = gray.shape[0] * gray.shape[1]
            area_ratio = contour_area / total_area
            
            if area_ratio < 0.05 or area_ratio > 0.95:
                logger.warning(f"Edge-based extraction quality poor: area ratio {area_ratio:.3f}")
                return None
            
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
        """Adaptive threshold-based extraction (fallback method)"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Try multiple threshold values to find the best one
        best_mask = None
        best_score = 0
        
        for threshold in [200, 220, 240, 260]:
            _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
            
            # Morphological operations to clean up mask
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Score based on foreground area (prefer 10-80% coverage)
            foreground_ratio = np.sum(mask > 0) / mask.size
            if 0.1 <= foreground_ratio <= 0.8:
                score = min(foreground_ratio, 1 - foreground_ratio)  # Prefer balanced ratios
                if score > best_score:
                    best_score = score
                    best_mask = mask
        
        # Fallback to simple threshold if no good mask found
        if best_mask is None:
            _, best_mask = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
            kernel = np.ones((3, 3), np.uint8)
            best_mask = cv2.morphologyEx(best_mask, cv2.MORPH_CLOSE, kernel)
            best_mask = cv2.morphologyEx(best_mask, cv2.MORPH_OPEN, kernel)
        
        # Apply mask
        result = image.copy()
        result_rgba = cv2.cvtColor(result, cv2.COLOR_RGB2RGBA)
        result_rgba[:, :, 3] = best_mask
        
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