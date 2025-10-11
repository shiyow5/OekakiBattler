"""
Image utility functions
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def auto_rotate_image(image: np.ndarray) -> np.ndarray:
    """Automatically rotate image based on content orientation"""
    try:
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Find the angle of rotation needed
        coords = np.column_stack(np.where(gray > 0))
        if len(coords) == 0:
            return image
            
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        # Only rotate if angle is significant
        if abs(angle) > 5:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            return rotated
            
        return image
    except:
        return image

def remove_noise(image: np.ndarray) -> np.ndarray:
    """Remove noise from image using various filters"""
    try:
        # Bilateral filter to preserve edges while removing noise
        filtered = cv2.bilateralFilter(image, 9, 75, 75)
        return filtered
    except:
        return image

def crop_to_content(image: np.ndarray, padding: int = 10) -> np.ndarray:
    """Crop image to content bounds with optional padding"""
    try:
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Find content bounds
        coords = cv2.findNonZero(gray)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            
            # Add padding
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            
            # Crop image
            cropped = image[y:y+h, x:x+w]
            return cropped
            
        return image
    except:
        return image

def normalize_size_aspect_ratio(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """Normalize image size while maintaining aspect ratio"""
    try:
        h, w = image.shape[:2]
        target_w, target_h = target_size
        
        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        
        # Calculate new dimensions
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Create canvas with target size
        if len(image.shape) == 3:
            canvas = np.ones((target_h, target_w, image.shape[2]), dtype=image.dtype) * 255
        else:
            canvas = np.ones((target_h, target_w), dtype=image.dtype) * 255
        
        # Center the resized image on canvas
        start_y = (target_h - new_h) // 2
        start_x = (target_w - new_w) // 2
        
        if len(image.shape) == 3:
            canvas[start_y:start_y+new_h, start_x:start_x+new_w, :] = resized
        else:
            canvas[start_y:start_y+new_h, start_x:start_x+new_w] = resized
            
        return canvas
    except:
        return cv2.resize(image, target_size)

def enhance_drawing_features(image: np.ndarray) -> np.ndarray:
    """Enhance hand-drawn features for better AI analysis"""
    try:
        # Convert to grayscale for processing
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Adaptive thresholding to enhance line art
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Morphological operations to clean up lines
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to color if original was color
        if len(image.shape) == 3:
            enhanced = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2RGB)
            # Blend with original
            enhanced = cv2.addWeighted(image, 0.7, enhanced, 0.3, 0)
            return enhanced
        else:
            return cleaned

    except:
        return image

def download_image(url: str, cache_dir: str) -> Optional[str]:
    """
    Download an image from URL and cache it locally

    Args:
        url: URL of the image (Google Drive or any HTTP URL)
        cache_dir: Directory to cache the downloaded image

    Returns:
        Local path to the cached image, or None if download failed
    """
    try:
        import requests
        import hashlib

        # Create cache directory if it doesn't exist
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)

        # Generate cache filename from URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()
        # Extract extension from URL if possible
        extension = '.png'
        if url.lower().endswith(('.jpg', '.jpeg')):
            extension = '.jpg'
        elif url.lower().endswith('.png'):
            extension = '.png'

        cache_file = cache_path / f"{url_hash}{extension}"

        # Return cached file if it exists
        if cache_file.exists():
            logger.debug(f"Using cached image: {cache_file}")
            return str(cache_file)

        # Convert Google Drive view URLs to direct download URLs
        download_url = url
        if 'drive.google.com' in url:
            if '/file/d/' in url:
                # Extract file ID from share URL
                file_id = url.split('/file/d/')[1].split('/')[0]
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            elif 'id=' in url:
                # Already in direct download format
                pass

        # Download file
        logger.info(f"Downloading image from {url}")
        response = requests.get(download_url, stream=True, timeout=10)
        response.raise_for_status()

        # Save to cache
        with open(cache_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"✓ Image cached: {cache_file}")
        return str(cache_file)

    except Exception as e:
        logger.error(f"Failed to download image from {url}: {e}")
        return None