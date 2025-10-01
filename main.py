#!/usr/bin/env python3
"""
お絵描きバトラー - Oekaki Battler
Main application entry point
"""

import os
import sys
import tkinter as tk
import logging
from pathlib import Path

# macOS 15+ fix: Force SDL2 video driver initialization on main thread
os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '1'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from config.database import initialize_database
from config.settings import Settings
from src.ui.main_menu import MainMenuWindow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oekaki_battler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        print("=" * 60)
        print("🎨 お絵描きバトラー (Oekaki Battler) 🎮")
        print("Hand-drawn Character Battle System")
        print("=" * 60)
        
        # Initialize database
        print("Initializing database...")
        logger.info("Starting application initialization")
        initialize_database()
        logger.info("Database initialized successfully")
        
        # Initialize settings manager
        print("Loading settings...")
        from src.services.settings_manager import settings_manager
        from src.services.audio_manager import audio_manager
        settings_manager.update_settings_class()
        settings_manager.apply_to_audio_manager(audio_manager)
        logger.info("Settings loaded and applied")

        # Initialize Pygame on main thread (macOS 15+ requirement)
        print("Initializing graphics system...")
        import pygame
        if not pygame.get_init():
            pygame.init()
            logger.info("Pygame initialized on main thread")
        
        # Check if API key is configured
        if not Settings.GOOGLE_API_KEY:
            print("⚠️  Warning: Google API key not found in .env file")
            print("   Some AI features may not work properly.")
            logger.warning("Google API key not configured")
        
        # Create and run main application
        print("Starting GUI application...")
        logger.info("Launching main GUI")
        
        root = tk.Tk()
        app = MainMenuWindow(root)
        
        # Center window on screen
        root.geometry("800x600")
        root.eval('tk::PlaceWindow . center')
        
        # Set up proper cleanup on window close
        def on_closing():
            try:
                app.cleanup()
                audio_manager.cleanup()
            except:
                pass
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Run application
        logger.info("Application started successfully")
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        logger.info("Application interrupted by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)
    finally:
        logger.info("Application shutdown")

if __name__ == "__main__":
    main()