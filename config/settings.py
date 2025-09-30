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
    MAX_IMAGE_SIZE = 600  # Maximum width or height while preserving aspect ratio
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
    SOUNDS_DIR = ASSETS_DIR / "sounds"
    MUSIC_DIR = ASSETS_DIR / "music"
    
    # Database
    DATABASE_PATH = DATA_DIR / "database.db"
    
    # Display Settings
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    FPS = 60
    
    # Audio Settings
    ENABLE_SOUND = True
    MASTER_VOLUME = 0.7
    BGM_VOLUME = 0.5
    SFX_VOLUME = 0.8
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.DATA_DIR, cls.CHARACTERS_DIR, cls.SPRITES_DIR, 
                         cls.ASSETS_DIR, cls.SOUNDS_DIR, cls.MUSIC_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

# Initialize directories on import
Settings.ensure_directories()