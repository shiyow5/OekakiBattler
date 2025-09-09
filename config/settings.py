import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv(), override=True)

class Settings:
    # AI Settings
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite-preview-06-17")
    
    # Image Processing
    TARGET_IMAGE_SIZE = (300, 300)
    SUPPORTED_FORMATS = [".png", ".jpg", ".jpeg", ".bmp"]
    MIN_RESOLUTION = (100, 100)
    
    # Battle Settings
    MAX_TURNS = 50
    CRITICAL_CHANCE = 0.05
    CRITICAL_MULTIPLIER = 2.0
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    CHARACTERS_DIR = DATA_DIR / "characters"
    SPRITES_DIR = DATA_DIR / "sprites"
    ASSETS_DIR = PROJECT_ROOT / "assets"
    
    # Database
    DATABASE_PATH = DATA_DIR / "database.db"
    
    # Display Settings
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    FPS = 60
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.DATA_DIR, cls.CHARACTERS_DIR, cls.SPRITES_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

# Initialize directories on import
Settings.ensure_directories()