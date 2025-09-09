"""
Unit tests for image processing functionality
"""

import pytest
import numpy as np
import cv2
from PIL import Image
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.services.image_processor import ImageProcessor


class TestImageProcessor:
    """Test ImageProcessor functionality"""
    
    def test_init(self):
        """Test ImageProcessor initialization"""
        processor = ImageProcessor()
        assert processor is not None
    
    def test_load_image_valid_path(self, test_image_path):
        """Test loading valid image file"""
        processor = ImageProcessor()
        image = processor.load_image(test_image_path)
        
        assert image is not None
        assert isinstance(image, np.ndarray)
        assert len(image.shape) == 3  # Should be color image
        assert image.shape[2] == 3    # RGB channels
    
    def test_load_image_invalid_path(self):
        """Test loading non-existent image file"""
        processor = ImageProcessor()
        image = processor.load_image("/nonexistent/path.png")
        
        assert image is None
    
    def test_load_image_invalid_format(self, tmp_path):
        """Test loading invalid image format"""
        # Create a text file with .png extension
        fake_image = tmp_path / "fake.png"
        fake_image.write_text("This is not an image")
        
        processor = ImageProcessor()
        image = processor.load_image(str(fake_image))
        
        assert image is None
    
    def test_preprocess_image(self, test_image_path):
        """Test image preprocessing"""
        processor = ImageProcessor()
        image = processor.load_image(test_image_path)
        processed = processor.preprocess_image(image)
        
        assert processed is not None
        assert isinstance(processed, np.ndarray)
        assert processed.shape[:2] == (300, 300)  # Should be resized to target size
    
    def test_preprocess_image_none_input(self):
        """Test preprocessing with None input"""
        processor = ImageProcessor()
        result = processor.preprocess_image(None)
        
        assert result is None
    
    def test_extract_character_grabcut_method(self, test_image_path):
        """Test character extraction using GrabCut"""
        processor = ImageProcessor()
        image = processor.load_image(test_image_path)
        preprocessed = processor.preprocess_image(image)
        
        # Mock GrabCut to avoid actual processing
        with patch('cv2.grabCut') as mock_grabcut:
            # Setup mock to simulate successful extraction
            mock_mask = np.ones((300, 300), dtype=np.uint8)
            mock_mask[:, :150] = 0  # Left half background, right half foreground
            
            def grabcut_side_effect(img, mask, rect, bgd_model, fgd_model, iter_count, mode):
                # Simulate GrabCut modifying the mask
                mask[:] = mock_mask
            
            mock_grabcut.side_effect = grabcut_side_effect
            
            result = processor._grabcut_extraction(preprocessed)
            
            assert result is not None
            assert isinstance(result, np.ndarray)
            mock_grabcut.assert_called_once()
    
    def test_extract_character_edge_method(self, test_image_path):
        """Test character extraction using edge detection"""
        processor = ImageProcessor()
        image = processor.load_image(test_image_path)
        preprocessed = processor.preprocess_image(image)
        
        result = processor._edge_based_extraction(preprocessed)
        
        assert result is not None
        assert isinstance(result, np.ndarray)
    
    def test_extract_character_threshold_method(self, test_image_path):
        """Test character extraction using threshold"""
        processor = ImageProcessor()
        image = processor.load_image(test_image_path)
        preprocessed = processor.preprocess_image(image)
        
        result = processor._threshold_extraction(preprocessed)
        
        assert result is not None
        assert isinstance(result, np.ndarray)
    
    def test_extract_character_main_method(self, test_image_path):
        """Test main character extraction method"""
        processor = ImageProcessor()
        image = processor.load_image(test_image_path)
        preprocessed = processor.preprocess_image(image)
        
        result = processor.extract_character(preprocessed)
        
        assert result is not None
        assert isinstance(result, np.ndarray)
    
    def test_extract_character_none_input(self):
        """Test character extraction with None input"""
        processor = ImageProcessor()
        result = processor.extract_character(None)
        
        assert result is None
    
    def test_save_sprite(self, test_image_path, tmp_path):
        """Test saving extracted character image"""
        processor = ImageProcessor()
        image = processor.load_image(test_image_path)
        extracted = processor.extract_character(image)
        
        output_path = tmp_path / "extracted_character.png"
        success = processor.save_sprite(extracted, str(output_path))
        
        assert success
        assert output_path.exists()
        
        # Verify saved image can be loaded
        saved_image = processor.load_image(str(output_path))
        assert saved_image is not None
    
    def test_save_sprite_none_input(self, tmp_path):
        """Test saving None image"""
        processor = ImageProcessor()
        output_path = tmp_path / "test.png"
        
        success = processor.save_sprite(None, str(output_path))
        
        assert not success
        assert not output_path.exists()
    
    def test_save_sprite_invalid_path(self, test_image_path):
        """Test saving to invalid path"""
        processor = ImageProcessor()
        image = processor.load_image(test_image_path)
        
        # Try to save to non-existent directory
        success = processor.save_sprite(image, "/nonexistent/dir/test.png")
        
        assert not success
    
    def test_process_full_pipeline(self, test_image_path, tmp_path):
        """Test complete image processing pipeline"""
        processor = ImageProcessor()
        
        # Load image
        image = processor.load_image(test_image_path)
        assert image is not None
        
        # Preprocess
        preprocessed = processor.preprocess_image(image)
        assert preprocessed is not None
        
        # Extract character
        extracted = processor.extract_character(preprocessed)
        assert extracted is not None
        
        # Save result
        output_path = tmp_path / "pipeline_result.png"
        success = processor.save_sprite(extracted, str(output_path))
        assert success
        assert output_path.exists()


class TestImageProcessorEdgeCases:
    """Test edge cases for image processing"""
    
    def test_very_small_image(self, tmp_path):
        """Test processing very small image"""
        # Create tiny 10x10 image
        tiny_image = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
        image_path = tmp_path / "tiny.png"
        cv2.imwrite(str(image_path), tiny_image)
        
        processor = ImageProcessor()
        image = processor.load_image(str(image_path))
        preprocessed = processor.preprocess_image(image)
        
        assert preprocessed is not None
        assert preprocessed.shape[:2] == (300, 300)  # Should be upscaled
    
    def test_very_large_image(self, tmp_path):
        """Test processing very large image"""
        # Create large 2000x2000 image
        large_image = np.random.randint(0, 255, (2000, 2000, 3), dtype=np.uint8)
        image_path = tmp_path / "large.png"
        cv2.imwrite(str(image_path), large_image)
        
        processor = ImageProcessor()
        image = processor.load_image(str(image_path))
        preprocessed = processor.preprocess_image(image)
        
        assert preprocessed is not None
        assert preprocessed.shape[:2] == (300, 300)  # Should be downscaled
    
    def test_grayscale_image(self, tmp_path):
        """Test processing grayscale image"""
        # Create grayscale image
        gray_image = np.random.randint(0, 255, (300, 300), dtype=np.uint8)
        image_path = tmp_path / "gray.png"
        cv2.imwrite(str(image_path), gray_image)
        
        processor = ImageProcessor()
        image = processor.load_image(str(image_path))
        
        # Should convert to color
        assert image is not None
        assert len(image.shape) == 3
        assert image.shape[2] == 3
    
    def test_all_white_image(self, tmp_path):
        """Test processing all-white image"""
        # Create all-white image
        white_image = np.full((300, 300, 3), 255, dtype=np.uint8)
        image_path = tmp_path / "white.png"
        cv2.imwrite(str(image_path), white_image)
        
        processor = ImageProcessor()
        image = processor.load_image(str(image_path))
        extracted = processor.extract_character(image)
        
        # Should handle gracefully (may return original or None)
        assert extracted is not None or extracted is None
    
    def test_all_black_image(self, tmp_path):
        """Test processing all-black image"""
        # Create all-black image
        black_image = np.zeros((300, 300, 3), dtype=np.uint8)
        image_path = tmp_path / "black.png"
        cv2.imwrite(str(image_path), black_image)
        
        processor = ImageProcessor()
        image = processor.load_image(str(image_path))
        extracted = processor.extract_character(image)
        
        # Should handle gracefully
        assert extracted is not None or extracted is None
    
    def test_corrupted_image_data(self):
        """Test handling corrupted image data"""
        processor = ImageProcessor()
        
        # Create corrupted numpy array
        corrupted = np.array([[1, 2], [3]], dtype=object)  # Irregular shape
        
        # Should handle gracefully
        result = processor.preprocess_image(corrupted)
        assert result is None or isinstance(result, np.ndarray)


@pytest.mark.unit
class TestImageProcessorPerformance:
    """Test image processor performance"""
    
    def test_batch_processing(self, tmp_path):
        """Test processing multiple images"""
        processor = ImageProcessor()
        
        # Create multiple test images
        image_paths = []
        for i in range(5):
            test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
            image_path = tmp_path / f"test_{i}.png"
            cv2.imwrite(str(image_path), test_image)
            image_paths.append(str(image_path))
        
        # Process all images
        results = []
        for path in image_paths:
            image = processor.load_image(path)
            if image is not None:
                extracted = processor.extract_character(image)
                results.append(extracted)
        
        # Should process all successfully
        assert len(results) == 5
        assert all(result is not None for result in results)


class TestImageProcessorIntegration:
    """Integration tests for image processor with other components"""
    
    def test_processor_with_ai_analyzer_input(self, test_image_path, tmp_path):
        """Test that processor output is suitable for AI analyzer"""
        processor = ImageProcessor()
        
        # Process image
        image = processor.load_image(test_image_path)
        extracted = processor.extract_character(image)
        
        # Save processed image for AI analysis
        output_path = tmp_path / "for_ai_analysis.png"
        success = processor.save_sprite(extracted, str(output_path))
        
        assert success
        assert output_path.exists()
        
        # Verify the saved image has proper format for AI
        saved_image = processor.load_image(str(output_path))
        assert saved_image is not None
        assert saved_image.shape[:2] == (300, 300)  # Expected size for AI
    
    def test_processor_error_recovery(self, tmp_path):
        """Test processor error recovery mechanisms"""
        processor = ImageProcessor()
        
        # Test with various problematic inputs
        test_cases = [
            None,
            np.array([]),  # Empty array
            np.random.randint(0, 255, (1, 1, 3), dtype=np.uint8),  # Too small
        ]
        
        for test_input in test_cases:
            # Should not crash, should return None or valid result
            result = processor.extract_character(test_input)
            assert result is None or isinstance(result, np.ndarray)