"""
Audio manager for BGM and sound effects
"""

import pygame
import logging
from pathlib import Path
from typing import Dict, Optional
from config.settings import Settings

logger = logging.getLogger(__name__)

class AudioManager:
    """Manages background music and sound effects"""
    
    def __init__(self):
        self.enabled = Settings.ENABLE_SOUND
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_initialized = False
        self.current_bgm = None
        
        if self.enabled:
            try:
                # Initialize pygame mixer
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                self.music_initialized = True
                logger.info("Audio system initialized")
                
                # Set initial volumes
                pygame.mixer.music.set_volume(Settings.BGM_VOLUME * Settings.MASTER_VOLUME)
                
            except pygame.error as e:
                logger.warning(f"Failed to initialize audio system: {e}")
                self.enabled = False
    
    def load_sound(self, name: str, filename: str) -> bool:
        """Load a sound effect"""
        if not self.enabled:
            return False
            
        try:
            sound_path = Settings.SOUNDS_DIR / filename
            if sound_path.exists():
                sound = pygame.mixer.Sound(str(sound_path))
                sound.set_volume(Settings.SFX_VOLUME * Settings.MASTER_VOLUME)
                self.sounds[name] = sound
                logger.debug(f"Loaded sound: {name}")
                return True
            else:
                logger.warning(f"Sound file not found: {sound_path}")
                return False
                
        except pygame.error as e:
            logger.warning(f"Failed to load sound {name}: {e}")
            return False
    
    def play_sound(self, name: str, volume: float = 1.0) -> bool:
        """Play a sound effect"""
        if not self.enabled or name not in self.sounds:
            return False
            
        try:
            sound = self.sounds[name]
            sound.set_volume(min(1.0, volume * Settings.SFX_VOLUME * Settings.MASTER_VOLUME))
            sound.play()
            return True
        except pygame.error as e:
            logger.warning(f"Failed to play sound {name}: {e}")
            return False
    
    def load_bgm(self, filename: str) -> bool:
        """Load background music"""
        if not self.enabled or not self.music_initialized:
            return False
            
        try:
            music_path = Settings.MUSIC_DIR / filename
            if music_path.exists():
                pygame.mixer.music.load(str(music_path))
                self.current_bgm = filename
                logger.debug(f"Loaded BGM: {filename}")
                return True
            else:
                logger.warning(f"BGM file not found: {music_path}")
                return False
                
        except pygame.error as e:
            logger.warning(f"Failed to load BGM {filename}: {e}")
            return False
    
    def play_bgm(self, loops: int = -1, fade_in: int = 0) -> bool:
        """Play background music"""
        if not self.enabled or not self.music_initialized or not self.current_bgm:
            return False
            
        try:
            if fade_in > 0:
                pygame.mixer.music.play(loops, fade_ms=fade_in)
            else:
                pygame.mixer.music.play(loops)
            logger.debug(f"Started BGM: {self.current_bgm}")
            return True
        except pygame.error as e:
            logger.warning(f"Failed to play BGM: {e}")
            return False
    
    def stop_bgm(self, fade_out: int = 0) -> bool:
        """Stop background music"""
        if not self.enabled or not self.music_initialized:
            return False
            
        try:
            if fade_out > 0:
                pygame.mixer.music.fadeout(fade_out)
            else:
                pygame.mixer.music.stop()
            logger.debug("Stopped BGM")
            return True
        except pygame.error as e:
            logger.warning(f"Failed to stop BGM: {e}")
            return False
    
    def pause_bgm(self) -> bool:
        """Pause background music"""
        if not self.enabled or not self.music_initialized:
            return False
            
        try:
            pygame.mixer.music.pause()
            return True
        except pygame.error as e:
            logger.warning(f"Failed to pause BGM: {e}")
            return False
    
    def resume_bgm(self) -> bool:
        """Resume background music"""
        if not self.enabled or not self.music_initialized:
            return False
            
        try:
            pygame.mixer.music.unpause()
            return True
        except pygame.error as e:
            logger.warning(f"Failed to resume BGM: {e}")
            return False
    
    def set_master_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        if not self.enabled:
            return
            
        Settings.MASTER_VOLUME = max(0.0, min(1.0, volume))
        
        # Update BGM volume
        if self.music_initialized:
            pygame.mixer.music.set_volume(Settings.BGM_VOLUME * Settings.MASTER_VOLUME)
        
        # Update SFX volumes
        for sound in self.sounds.values():
            sound.set_volume(Settings.SFX_VOLUME * Settings.MASTER_VOLUME)
    
    def set_bgm_volume(self, volume: float):
        """Set BGM volume (0.0 to 1.0)"""
        if not self.enabled or not self.music_initialized:
            return
            
        Settings.BGM_VOLUME = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(Settings.BGM_VOLUME * Settings.MASTER_VOLUME)
    
    def set_sfx_volume(self, volume: float):
        """Set SFX volume (0.0 to 1.0)"""
        if not self.enabled:
            return
            
        Settings.SFX_VOLUME = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(Settings.SFX_VOLUME * Settings.MASTER_VOLUME)
    
    def is_bgm_playing(self) -> bool:
        """Check if BGM is currently playing"""
        if not self.enabled or not self.music_initialized:
            return False
            
        return pygame.mixer.music.get_busy()
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.enabled:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.stop()
                self.sounds.clear()
                logger.debug("Audio system cleaned up")
            except:
                pass
    
    def create_default_sounds(self):
        """Load or create default sound effects"""
        if not self.enabled:
            return

        # Define sound definitions with possible file names
        sound_defs = {
            "attack": {
                "files": ["attack.wav", "attack.ogg", "attack.mp3"],
                "frequency": 800,
                "duration": 0.1
            },
            "critical": {
                "files": ["critical.wav", "critical.ogg", "critical.mp3"],
                "frequency": 1200,
                "duration": 0.15
            },
            "magic": {
                "files": ["magic.wav", "magic.ogg", "magic.mp3"],
                "frequency": 600,
                "duration": 0.2,
                "warble": True
            },
            "miss": {
                "files": ["miss.wav", "miss.ogg", "miss.mp3"],
                "frequency": 400,
                "duration": 0.1,
                "descending": True
            },
            "victory": {
                "files": ["victory.wav", "victory.ogg", "victory.mp3"],
                "frequency": 800,
                "duration": 0.5,
                "melody": True
            }
        }

        try:
            for name, config in sound_defs.items():
                # Try to load from file first
                loaded = False
                for filename in config["files"]:
                    if self.load_sound(name, filename):
                        loaded = True
                        logger.info(f"Loaded sound '{name}' from file: {filename}")
                        break

                # If no file found, create programmatically
                if not loaded:
                    logger.debug(f"No file found for '{name}', creating programmatically")
                    self._create_simple_sound(
                        name,
                        frequency=config["frequency"],
                        duration=config["duration"],
                        warble=config.get("warble", False),
                        descending=config.get("descending", False),
                        melody=config.get("melody", False)
                    )

            logger.info("Sound effects initialized")

        except Exception as e:
            logger.warning(f"Failed to create default sounds: {e}")
    
    def _create_simple_sound(self, name: str, frequency: int, duration: float, 
                           warble: bool = False, descending: bool = False, melody: bool = False):
        """Create a simple programmatic sound effect"""
        try:
            sample_rate = 22050
            samples = int(sample_rate * duration)
            
            # Create sound data
            import numpy as np
            
            if melody:
                # Create a simple ascending melody
                freqs = [frequency, frequency * 1.25, frequency * 1.5, frequency * 2.0]
                sound_data = np.array([])
                for freq in freqs:
                    t = np.linspace(0, duration/4, samples//4, False)
                    wave = np.sin(freq * 2 * np.pi * t) * 0.3
                    sound_data = np.concatenate([sound_data, wave])
            elif warble:
                # Create warbling effect
                t = np.linspace(0, duration, samples, False)
                modulation = np.sin(10 * 2 * np.pi * t) * 0.2 + 1
                wave = np.sin(frequency * 2 * np.pi * t * modulation) * 0.3
                sound_data = wave
            elif descending:
                # Create descending tone
                t = np.linspace(0, duration, samples, False)
                freq_sweep = frequency * (1 - t / duration * 0.5)
                wave = np.sin(freq_sweep * 2 * np.pi * t) * 0.3
                sound_data = wave
            else:
                # Simple tone
                t = np.linspace(0, duration, samples, False)
                wave = np.sin(frequency * 2 * np.pi * t) * 0.3
                sound_data = wave
            
            # Apply fade out to prevent clicks
            fade_samples = min(1000, samples // 10)
            if len(sound_data) > fade_samples:
                sound_data[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Convert to 16-bit integers
            sound_data = (sound_data * 32767).astype(np.int16)
            
            # Create stereo sound
            stereo_data = np.zeros((len(sound_data), 2), dtype=np.int16)
            stereo_data[:, 0] = sound_data  # Left channel
            stereo_data[:, 1] = sound_data  # Right channel
            
            # Create pygame sound
            sound = pygame.sndarray.make_sound(stereo_data)
            sound.set_volume(Settings.SFX_VOLUME * Settings.MASTER_VOLUME)
            self.sounds[name] = sound
            
        except ImportError:
            # numpy not available, skip programmatic sound creation
            logger.warning("numpy not available for programmatic sound creation")
        except Exception as e:
            logger.warning(f"Failed to create sound {name}: {e}")

# Global audio manager instance
audio_manager = AudioManager()