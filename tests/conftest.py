"""
Pytest configuration and fixtures for Oekaki Battler tests
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
import sqlite3
import numpy as np
from PIL import Image

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.database import initialize_database
from src.models import Character, CharacterStats
from src.services.database_manager import DatabaseManager


@pytest.fixture(scope="session")
def test_database():
    """Create a temporary test database"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        test_db_path = f.name
    
    # Set test database path
    original_path = None
    try:
        from config import settings
        if hasattr(settings.Settings, 'DATABASE_PATH'):
            original_path = settings.Settings.DATABASE_PATH
            settings.Settings.DATABASE_PATH = Path(test_db_path)
        
        # Initialize test database
        initialize_database()
        
        yield test_db_path
        
    finally:
        # Restore original path
        if original_path:
            settings.Settings.DATABASE_PATH = original_path
        
        # Clean up
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


@pytest.fixture
def db_manager(test_database):
    """Create a database manager for testing"""
    return DatabaseManager()


@pytest.fixture
def sample_character():
    """Create a sample character for testing"""
    return Character(
        name="TestCharacter",
        hp=100,
        attack=75,
        defense=60,
        speed=85,
        magic=55,
        description="A test character for unit testing",
        image_path="/test/path/character.png"
    )


@pytest.fixture
def sample_character_stats():
    """Create sample character stats for testing"""
    return CharacterStats(
        hp=100,
        attack=75,
        defense=60,
        speed=85,
        magic=55,
        description="Test character stats"
    )


@pytest.fixture
def test_image():
    """Create a test image for image processing tests"""
    # Create a simple test image
    image = Image.new('RGB', (300, 300), color='white')
    
    # Draw a simple character shape
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    
    # Draw a simple stick figure
    # Head
    draw.ellipse([140, 50, 160, 70], fill='black')
    # Body
    draw.line([150, 70, 150, 150], fill='black', width=3)
    # Arms
    draw.line([130, 100, 170, 100], fill='black', width=3)
    # Legs
    draw.line([150, 150, 130, 200], fill='black', width=3)
    draw.line([150, 150, 170, 200], fill='black', width=3)
    
    return image


@pytest.fixture
def test_image_path(test_image, tmp_path):
    """Save test image to temporary file and return path"""
    image_path = tmp_path / "test_character.png"
    test_image.save(image_path)
    return str(image_path)


@pytest.fixture
def mock_ai_response():
    """Mock AI response data for testing"""
    return [
        {
            "hp": 95,
            "attack": 80,
            "defense": 65,
            "speed": 90,
            "magic": 60,
            "description": "AI分析による戦士キャラクター"
        }
    ]


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create temporary directory for test data"""
    return tmp_path_factory.mktemp("test_data")


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, tmp_path):
    """Setup test environment variables and paths"""
    # Set test environment variables
    monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key")
    monkeypatch.setenv("MODEL_NAME", "test_model")
    
    # Mock settings paths to use temporary directories
    from config import settings
    monkeypatch.setattr(settings.Settings, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(settings.Settings, "CHARACTERS_DIR", tmp_path / "data" / "characters")
    monkeypatch.setattr(settings.Settings, "SPRITES_DIR", tmp_path / "data" / "sprites")
    
    # Create directories
    (tmp_path / "data").mkdir(exist_ok=True)
    (tmp_path / "data" / "characters").mkdir(exist_ok=True)
    (tmp_path / "data" / "sprites").mkdir(exist_ok=True)


@pytest.fixture
def battle_participants():
    """Create two characters for battle testing"""
    char1 = Character(
        name="Warrior",
        hp=120,
        attack=90,
        defense=70,
        speed=60,
        magic=30,
        description="Strong warrior",
        image_path="/test/warrior.png"
    )
    
    char2 = Character(
        name="Mage",
        hp=80,
        attack=50,
        defense=40,
        speed=85,
        magic=95,
        description="Powerful mage",
        image_path="/test/mage.png"
    )
    
    return char1, char2