"""
Settings manager for persistent configuration storage
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import Settings

logger = logging.getLogger(__name__)

class SettingsManager:
    """Manage persistent settings storage and retrieval"""
    
    def __init__(self):
        self.settings_file = Settings.DATA_DIR / "user_settings.json"
        self.default_settings = self._get_default_settings()
        self.current_settings = self.default_settings.copy()
        self.load_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings values"""
        return {
            # Battle Settings
            'battle_speed': 0.5,
            'max_turns': 50,
            'critical_chance': 0.05,
            
            # Display Settings
            'screen_width': 1024,
            'screen_height': 768,
            'fps': 60,
            
            # Audio Settings
            'master_volume': 0.7,
            'bgm_volume': 0.5,
            'sfx_volume': 0.8,
            'enable_sound': True,
            
            # General Settings
            'auto_save_battles': True,
            'show_battle_animations': True,
            'japanese_ui': True,
            'auto_load_characters': True,
        }
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    stored_settings = json.load(f)
                    
                # Merge with defaults (in case new settings were added)
                self.current_settings.update(stored_settings)
                logger.info("Settings loaded successfully")
            else:
                logger.info("No settings file found, using defaults")
                
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            logger.info("Using default settings")
            
        return self.current_settings.copy()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to file"""
        try:
            # Validate and sanitize settings
            validated_settings = self._validate_settings(settings)
            
            # Update current settings
            self.current_settings.update(validated_settings)
            
            # Ensure data directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2, ensure_ascii=False)
            
            logger.info("Settings saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize settings values"""
        validated = {}
        
        # Battle settings validation
        if 'battle_speed' in settings:
            validated['battle_speed'] = max(0.01, min(3.0, float(settings['battle_speed'])))
            
        if 'max_turns' in settings:
            validated['max_turns'] = max(10, min(200, int(settings['max_turns'])))
            
        if 'critical_chance' in settings:
            validated['critical_chance'] = max(0.0, min(1.0, float(settings['critical_chance'])))
        
        # Display settings validation
        if 'screen_width' in settings:
            validated['screen_width'] = max(800, min(3840, int(settings['screen_width'])))
            
        if 'screen_height' in settings:
            validated['screen_height'] = max(600, min(2160, int(settings['screen_height'])))
            
        if 'fps' in settings:
            validated['fps'] = max(30, min(144, int(settings['fps'])))
        
        # Audio settings validation
        if 'master_volume' in settings:
            validated['master_volume'] = max(0.0, min(1.0, float(settings['master_volume'])))
            
        if 'bgm_volume' in settings:
            validated['bgm_volume'] = max(0.0, min(1.0, float(settings['bgm_volume'])))
            
        if 'sfx_volume' in settings:
            validated['sfx_volume'] = max(0.0, min(1.0, float(settings['sfx_volume'])))
        
        # Boolean settings
        for key in ['enable_sound', 'auto_save_battles', 'show_battle_animations', 
                   'japanese_ui', 'auto_load_characters']:
            if key in settings:
                validated[key] = bool(settings[key])
        
        return validated
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        return self.current_settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a specific setting value and save immediately"""
        try:
            temp_settings = {key: value}
            validated = self._validate_settings(temp_settings)
            
            if key in validated:
                self.current_settings[key] = validated[key]
                return self.save_settings({})  # Save current settings
            else:
                logger.warning(f"Invalid setting key or value: {key}={value}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
            return False
    
    def apply_to_battle_engine(self, battle_engine):
        """Apply current settings to battle engine"""
        try:
            if hasattr(battle_engine, 'battle_speed'):
                battle_engine.battle_speed = self.get_setting('battle_speed', 2.0)
            if hasattr(battle_engine, 'max_turns'):
                battle_engine.max_turns = self.get_setting('max_turns', 50)
            if hasattr(battle_engine, 'critical_chance'):
                battle_engine.critical_chance = self.get_setting('critical_chance', 0.05)
                
            logger.debug("Settings applied to battle engine")
            
        except Exception as e:
            logger.error(f"Error applying settings to battle engine: {e}")
    
    def apply_to_audio_manager(self, audio_manager):
        """Apply current settings to audio manager"""
        try:
            audio_manager.set_master_volume(self.get_setting('master_volume', 0.7))
            audio_manager.set_bgm_volume(self.get_setting('bgm_volume', 0.5))
            audio_manager.set_sfx_volume(self.get_setting('sfx_volume', 0.8))
            
            # Update Settings class for audio manager
            Settings.ENABLE_SOUND = self.get_setting('enable_sound', True)
            Settings.MASTER_VOLUME = self.get_setting('master_volume', 0.7)
            Settings.BGM_VOLUME = self.get_setting('bgm_volume', 0.5)
            Settings.SFX_VOLUME = self.get_setting('sfx_volume', 0.8)
            
            logger.debug("Settings applied to audio manager")
            
        except Exception as e:
            logger.error(f"Error applying settings to audio manager: {e}")
    
    def update_settings_class(self):
        """Update the Settings class with current values"""
        try:
            # Update battle settings
            Settings.BATTLE_SPEED = self.get_setting('battle_speed', 2.0)
            Settings.MAX_TURNS = self.get_setting('max_turns', 50)
            Settings.CRITICAL_CHANCE = self.get_setting('critical_chance', 0.05)
            
            # Update display settings
            Settings.SCREEN_WIDTH = self.get_setting('screen_width', 1024)
            Settings.SCREEN_HEIGHT = self.get_setting('screen_height', 768)
            Settings.FPS = self.get_setting('fps', 60)
            
            # Update audio settings
            Settings.ENABLE_SOUND = self.get_setting('enable_sound', True)
            Settings.MASTER_VOLUME = self.get_setting('master_volume', 0.7)
            Settings.BGM_VOLUME = self.get_setting('bgm_volume', 0.5)
            Settings.SFX_VOLUME = self.get_setting('sfx_volume', 0.8)
            
            logger.debug("Settings class updated")
            
        except Exception as e:
            logger.error(f"Error updating Settings class: {e}")
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to default values"""
        try:
            self.current_settings = self.default_settings.copy()
            success = self.save_settings({})
            if success:
                self.update_settings_class()
            return success
            
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            return False

# Global settings manager instance
settings_manager = SettingsManager()