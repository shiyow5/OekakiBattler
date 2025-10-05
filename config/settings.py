import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv(), override=True)

class Settings:
    # AI Settings
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite-preview-06-17")

    # Google Sheets Settings
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    WORKSHEET_NAME = os.getenv("WORKSHEET_NAME", "Characters")
    BATTLE_HISTORY_SHEET = os.getenv("BATTLE_HISTORY_SHEET", "BattleHistory")
    RANKING_SHEET = os.getenv("RANKING_SHEET", "Rankings")
    GOOGLE_CREDENTIALS_PATH = Path(os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"))

    # Google Drive Settings (optional - for organizing uploads in a specific folder)
    DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")  # Optional: specify a folder ID to organize uploads

    # Google Apps Script Settings (for uploading via GAS to use user's storage quota)
    GAS_WEBHOOK_URL = os.getenv("GAS_WEBHOOK_URL")  # Google Apps Script Web App URL
    GAS_SHARED_SECRET = os.getenv("SHARED_SECRET", "oekaki_battler_line_to_gas_secret_shiyow5")  # Secret for GAS authentication

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
    # Battle display monitor index (0-based)
    # - 0 = Primary monitor (first display)
    # - 1 = Secondary monitor (second display) ← Default
    # - 2 = Tertiary monitor (third display)
    # Note: Display indices are 0-based. For 2 monitors, valid indices are 0 and 1.
    BATTLE_DISPLAY_INDEX = int(os.getenv("BATTLE_DISPLAY_INDEX", "1"))
    
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