"""
Unit tests for AI analyzer functionality
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
import tempfile
from pathlib import Path

from src.services.ai_analyzer import AIAnalyzer
from src.models import Character


class TestAIAnalyzer:
    """Test AIAnalyzer functionality"""
    
    def test_init_with_api_key(self):
        """Test AIAnalyzer initialization with API key"""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            analyzer = AIAnalyzer()
            assert analyzer is not None
    
    def test_init_without_api_key(self):
        """Test AIAnalyzer initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            analyzer = AIAnalyzer()
            assert analyzer is not None
            # Should work in fallback mode
    
    def test_is_available_with_api_key(self):
        """Test availability check with API key"""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            with patch('src.services.ai_analyzer.genai') as mock_genai:
                analyzer = AIAnalyzer()
                assert analyzer.is_available()
    
    def test_is_available_without_api_key(self):
        """Test availability check without API key"""
        analyzer = AIAnalyzer()
        analyzer.genai = None
        assert not analyzer.is_available()
    
    @patch('src.services.ai_analyzer.genai')
    def test_analyze_character_success(self, mock_genai, test_image_path):
        """Test successful character analysis"""
        # Setup mock AI response
        mock_response = MagicMock()
        mock_response.text = json.dumps([{
            "hp": 95,
            "attack": 80,
            "defense": 65,
            "speed": 90,
            "magic": 60,
            "description": "Strong warrior character"
        }])
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            analyzer = AIAnalyzer()
            result = analyzer.analyze_character(test_image_path)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['hp'] == 95
        assert result[0]['attack'] == 80
        assert 'description' in result[0]
    
    @patch('src.services.ai_analyzer.genai')
    def test_analyze_character_api_error(self, mock_genai, test_image_path):
        """Test character analysis with API error"""
        # Setup mock to raise exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            analyzer = AIAnalyzer()
            result = analyzer.analyze_character(test_image_path)
        
        # Should fall back to default stats
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert 'hp' in result[0]
        assert 'attack' in result[0]
    
    def test_analyze_character_fallback_mode(self, test_image_path):
        """Test character analysis in fallback mode"""
        analyzer = AIAnalyzer()
        analyzer.genai = None  # Force fallback mode
        
        result = analyzer.analyze_character(test_image_path, fallback_stats=True)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        
        stats = result[0]
        assert 50 <= stats['hp'] <= 150
        assert 30 <= stats['attack'] <= 120
        assert 20 <= stats['defense'] <= 100
        assert 40 <= stats['speed'] <= 130
        assert 10 <= stats['magic'] <= 100
        assert isinstance(stats['description'], str)
    
    def test_analyze_character_no_fallback(self, test_image_path):
        """Test character analysis without fallback when AI unavailable"""
        analyzer = AIAnalyzer()
        analyzer.genai = None  # Force unavailable
        
        result = analyzer.analyze_character(test_image_path, fallback_stats=False)
        
        assert result is None
    
    def test_analyze_character_invalid_file(self):
        """Test character analysis with invalid file"""
        analyzer = AIAnalyzer()
        result = analyzer.analyze_character("/nonexistent/file.png")
        
        assert result is None
    
    @patch('src.services.ai_analyzer.genai')
    def test_analyze_character_invalid_json_response(self, mock_genai, test_image_path):
        """Test handling of invalid JSON response from AI"""
        # Setup mock with invalid JSON
        mock_response = MagicMock()
        mock_response.text = "This is not JSON"
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            analyzer = AIAnalyzer()
            result = analyzer.analyze_character(test_image_path)
        
        # Should fall back to default stats
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
    
    @patch('src.services.ai_analyzer.genai')
    def test_analyze_character_empty_response(self, mock_genai, test_image_path):
        """Test handling of empty response from AI"""
        # Setup mock with empty response
        mock_response = MagicMock()
        mock_response.text = "[]"
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            analyzer = AIAnalyzer()
            result = analyzer.analyze_character(test_image_path)
        
        # Should fall back to default stats
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
    
    def test_generate_fallback_stats(self):
        """Test fallback stats generation"""
        analyzer = AIAnalyzer()
        stats = analyzer._generate_fallback_stats()
        
        assert isinstance(stats, dict)
        assert 'hp' in stats
        assert 'attack' in stats
        assert 'defense' in stats
        assert 'speed' in stats
        assert 'magic' in stats
        assert 'description' in stats
        
        # Check value ranges
        assert 50 <= stats['hp'] <= 150
        assert 30 <= stats['attack'] <= 120
        assert 20 <= stats['defense'] <= 100
        assert 40 <= stats['speed'] <= 130
        assert 10 <= stats['magic'] <= 100
    
    def test_validate_stats_valid(self):
        """Test validation of valid stats"""
        analyzer = AIAnalyzer()
        
        valid_stats = {
            "hp": 100,
            "attack": 75,
            "defense": 60,
            "speed": 85,
            "magic": 55,
            "description": "Test character"
        }
        
        result = analyzer._validate_stats(valid_stats)
        assert result == valid_stats
    
    def test_validate_stats_invalid_ranges(self):
        """Test validation of stats with invalid ranges"""
        analyzer = AIAnalyzer()
        
        invalid_stats = {
            "hp": 200,  # Too high
            "attack": 10,  # Too low
            "defense": 60,
            "speed": 85,
            "magic": 55,
            "description": "Test character"
        }
        
        result = analyzer._validate_stats(invalid_stats)
        
        # Should clamp values to valid ranges
        assert 50 <= result['hp'] <= 150
        assert 30 <= result['attack'] <= 120
    
    def test_validate_stats_missing_fields(self):
        """Test validation of stats with missing fields"""
        analyzer = AIAnalyzer()
        
        incomplete_stats = {
            "hp": 100,
            "attack": 75
            # Missing other fields
        }
        
        result = analyzer._validate_stats(incomplete_stats)
        
        # Should fill in missing fields with defaults
        assert 'defense' in result
        assert 'speed' in result
        assert 'magic' in result
        assert 'description' in result
    
    def test_validate_stats_non_numeric(self):
        """Test validation of stats with non-numeric values"""
        analyzer = AIAnalyzer()
        
        invalid_stats = {
            "hp": "one hundred",
            "attack": None,
            "defense": 60,
            "speed": 85,
            "magic": 55,
            "description": "Test character"
        }
        
        result = analyzer._validate_stats(invalid_stats)
        
        # Should replace invalid values with defaults
        assert isinstance(result['hp'], int)
        assert isinstance(result['attack'], int)
        assert 50 <= result['hp'] <= 150
        assert 30 <= result['attack'] <= 120


class TestAIAnalyzerIntegration:
    """Integration tests for AI analyzer"""
    
    def test_create_character_from_analysis(self, test_image_path):
        """Test creating Character object from AI analysis"""
        analyzer = AIAnalyzer()
        analysis_result = analyzer.analyze_character(test_image_path)
        
        assert analysis_result is not None
        stats = analysis_result[0]
        
        # Create character from analysis
        character = Character(
            name="Test Character",
            hp=stats['hp'],
            attack=stats['attack'],
            defense=stats['defense'],
            speed=stats['speed'],
            magic=stats['magic'],
            description=stats['description'],
            image_path=test_image_path
        )
        
        assert character is not None
        assert character.hp == stats['hp']
        assert character.attack == stats['attack']
        assert character.description == stats['description']
    
    @patch('src.services.ai_analyzer.genai')
    def test_multiple_characters_analysis(self, mock_genai, test_image_path):
        """Test analyzing multiple characters"""
        # Setup mock to return multiple characters
        mock_response = MagicMock()
        mock_response.text = json.dumps([
            {
                "hp": 95,
                "attack": 80,
                "defense": 65,
                "speed": 90,
                "magic": 60,
                "description": "First character"
            },
            {
                "hp": 85,
                "attack": 70,
                "defense": 75,
                "speed": 95,
                "magic": 85,
                "description": "Second character"
            }
        ])
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            analyzer = AIAnalyzer()
            result = analyzer.analyze_character(test_image_path)
        
        assert result is not None
        assert len(result) == 2
        assert result[0]['description'] == "First character"
        assert result[1]['description'] == "Second character"


@pytest.mark.unit
class TestAIAnalyzerPerformance:
    """Test AI analyzer performance and reliability"""
    
    def test_repeated_analysis_consistency(self, test_image_path):
        """Test that repeated analysis produces consistent results"""
        analyzer = AIAnalyzer()
        analyzer.genai = None  # Use fallback for consistency
        
        results = []
        for _ in range(3):
            result = analyzer.analyze_character(test_image_path)
            results.append(result)
        
        # All results should be valid
        assert all(result is not None for result in results)
        assert all(len(result) == 1 for result in results)
        
        # Stats should be in valid ranges
        for result in results:
            stats = result[0]
            assert 50 <= stats['hp'] <= 150
            assert 30 <= stats['attack'] <= 120
    
    def test_error_handling_robustness(self):
        """Test robust error handling"""
        analyzer = AIAnalyzer()
        
        # Test various error conditions
        error_cases = [
            None,
            "",
            "/nonexistent/path.png",
            "/dev/null",
        ]
        
        for case in error_cases:
            # Should not crash
            result = analyzer.analyze_character(case)
            # Should either return valid stats or None
            assert result is None or (isinstance(result, list) and len(result) >= 1)


class TestAIAnalyzerEdgeCases:
    """Test edge cases for AI analyzer"""
    
    def test_very_long_description(self):
        """Test handling of very long AI-generated descriptions"""
        analyzer = AIAnalyzer()
        
        long_desc_stats = {
            "hp": 100,
            "attack": 75,
            "defense": 60,
            "speed": 85,
            "magic": 55,
            "description": "A" * 1000  # Very long description
        }
        
        result = analyzer._validate_stats(long_desc_stats)
        
        # Should handle long descriptions gracefully
        assert result is not None
        assert 'description' in result
        assert isinstance(result['description'], str)
    
    def test_unicode_description(self):
        """Test handling of unicode characters in descriptions"""
        analyzer = AIAnalyzer()
        
        unicode_stats = {
            "hp": 100,
            "attack": 75,
            "defense": 60,
            "speed": 85,
            "magic": 55,
            "description": "強い戦士キャラクター🗡️✨"
        }
        
        result = analyzer._validate_stats(unicode_stats)
        
        assert result is not None
        assert result['description'] == "強い戦士キャラクター🗡️✨"
    
    def test_extreme_stat_values(self):
        """Test handling of extreme stat values from AI"""
        analyzer = AIAnalyzer()
        
        extreme_stats = {
            "hp": -100,  # Negative
            "attack": 99999,  # Way too high
            "defense": 0,    # Zero
            "speed": 85.5,   # Float instead of int
            "magic": "fifty",  # String instead of number
            "description": None  # None instead of string
        }
        
        result = analyzer._validate_stats(extreme_stats)
        
        # Should normalize all values
        assert 50 <= result['hp'] <= 150
        assert 30 <= result['attack'] <= 120
        assert 20 <= result['defense'] <= 100
        assert isinstance(result['speed'], int)
        assert isinstance(result['magic'], int)
        assert isinstance(result['description'], str)