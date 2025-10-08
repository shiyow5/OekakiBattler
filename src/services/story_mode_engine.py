"""
Story mode battle engine with auto-execution support
"""

import logging
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from src.models.character import Character
from src.models.story_boss import StoryBoss, StoryProgress
from src.services.battle_engine import BattleEngine
from src.models.battle import Battle

logger = logging.getLogger(__name__)


class StoryModeEngine:
    """Manages story mode progression and battles"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.bosses: Dict[int, StoryBoss] = {}
        self.battle_engine = None
        self.is_running = False
        self.character_queue: List[str] = []
        self.processed_character_ids = set()
        self.current_character: Optional[Character] = None
        self.current_boss_level: int = 1
        self.progress_cache: Dict[str, StoryProgress] = {}  # Cache to reduce API calls

    def load_bosses(self) -> bool:
        """Load all story mode bosses"""
        try:
            # Load bosses from database/storage
            for level in range(1, 6):
                boss = self.db_manager.get_story_boss(level)
                if boss:
                    self.bosses[level] = boss
                else:
                    logger.warning(f"Boss for level {level} not found")

            return len(self.bosses) > 0
        except Exception as e:
            logger.error(f"Error loading story bosses: {e}")
            return False

    def get_boss(self, level: int) -> Optional[StoryBoss]:
        """Get boss by level"""
        return self.bosses.get(level)

    def get_player_progress(self, character_id: str, use_cache: bool = True) -> StoryProgress:
        """Get player's story mode progress with caching"""
        try:
            # Check cache first
            if use_cache and character_id in self.progress_cache:
                return self.progress_cache[character_id]

            progress = self.db_manager.get_story_progress(character_id)
            if not progress:
                # Create new progress
                progress = StoryProgress(character_id=character_id)
                self.db_manager.save_story_progress(progress)

            # Update cache
            self.progress_cache[character_id] = progress
            return progress
        except Exception as e:
            logger.error(f"Error getting story progress: {e}")
            return StoryProgress(character_id=character_id)

    def start_battle(self, player: Character, boss_level: int) -> Optional[Battle]:
        """Start a story mode battle"""
        try:
            boss = self.get_boss(boss_level)
            if not boss:
                logger.error(f"Boss not found for level {boss_level}")
                return None

            # Convert StoryBoss to Character for battle
            # Use model_construct to bypass validation (bosses can have up to 500 total stats)
            boss_character = Character.model_construct(
                id=f"boss_lv{boss_level}",
                name=boss.name,
                hp=boss.hp,
                attack=boss.attack,
                defense=boss.defense,
                speed=boss.speed,
                magic=boss.magic,
                luck=boss.luck,
                description=boss.description,
                image_path=boss.image_path or "",
                sprite_path=boss.sprite_path or "",
                created_at=datetime.now(),
                battle_count=0,
                win_count=0
            )

            # Create battle engine
            self.battle_engine = BattleEngine()

            # Apply current settings to battle engine
            try:
                from src.services.settings_manager import settings_manager
                settings_manager.apply_to_battle_engine(self.battle_engine)
                logger.info("Applied settings to story mode battle engine")
            except Exception as e:
                logger.warning(f"Could not apply settings to story mode battle engine: {e}")

            self.battle_engine.character1 = player
            self.battle_engine.character2 = boss_character

            logger.info(f"Story battle started: {player.name} vs {boss.name} (Lv{boss_level})")
            return None  # Battle will be executed separately

        except Exception as e:
            logger.error(f"Error starting story battle: {e}")
            return None

    def execute_battle(self, visual_mode: bool = False) -> Optional[Dict[str, Any]]:
        """Execute the current battle"""
        if not self.battle_engine:
            logger.error("No active battle")
            return None

        try:
            char1 = self.battle_engine.character1
            char2 = self.battle_engine.character2

            battle = self.battle_engine.start_battle(char1, char2, visual_mode=visual_mode)

            return {
                'battle': battle,
                'winner': char1 if battle.winner_id == char1.id else char2,
                'loser': char2 if battle.winner_id == char1.id else char1
            }
        except Exception as e:
            logger.error(f"Error executing story battle: {e}")
            return None

    def update_progress(self, character_id: str, boss_level: int, victory: bool) -> bool:
        """Update player's story mode progress"""
        try:
            progress = self.get_player_progress(character_id, use_cache=False)  # Always fetch fresh for updates
            progress.attempts += 1

            if victory:
                if boss_level not in progress.victories:
                    progress.victories.append(boss_level)
                    progress.victories.sort()

                # Update current level
                if boss_level == progress.current_level and boss_level < 5:
                    progress.current_level = boss_level + 1
                elif boss_level == 5:
                    progress.completed = True

            result = self.db_manager.save_story_progress(progress)

            # Update cache
            if result:
                self.progress_cache[character_id] = progress

            return result

        except Exception as e:
            logger.error(f"Error updating story progress: {e}")
            return False

    def get_next_boss_level(self, character_id: str) -> int:
        """Get the next boss level for the player"""
        progress = self.get_player_progress(character_id)
        return progress.current_level

    def is_completed(self, character_id: str) -> bool:
        """Check if player has completed story mode"""
        progress = self.get_player_progress(character_id)
        return progress.completed

    def reset_progress(self, character_id: str) -> bool:
        """Reset player's story mode progress"""
        try:
            progress = StoryProgress(character_id=character_id)
            return self.db_manager.save_story_progress(progress)
        except Exception as e:
            logger.error(f"Error resetting story progress: {e}")
            return False

    def start_auto_story_mode(self, visual_mode: bool = False):
        """
        Start auto story mode - automatically runs story mode for all characters

        Args:
            visual_mode: Whether to show visual battle display
        """
        logger.info("Starting auto story mode")
        self.is_running = True

        # Load bosses
        if not self.load_bosses():
            logger.error("Failed to load story bosses")
            return None

        # Load initial characters
        self._check_for_new_characters()

        if not self.character_queue:
            logger.info("No characters available for auto story mode")
            return {
                'status': 'waiting',
                'message': '新しいキャラクターを待機中...'
            }

        # Select first character from queue
        self.current_character = self._get_next_character()
        if self.current_character:
            progress = self.get_player_progress(self.current_character.id)
            self.current_boss_level = progress.current_level

            return {
                'status': 'started',
                'character': self.current_character,
                'boss_level': self.current_boss_level
            }

        return None

    def run_next_story_battle(self, visual_mode: bool = False) -> Optional[Dict[str, Any]]:
        """
        Run the next story battle in auto mode

        Args:
            visual_mode: Whether to show visual battle display

        Returns:
            Battle result dictionary or None if waiting for new characters
        """
        if not self.is_running:
            logger.warning("Auto story mode not running")
            return None

        # Check for new characters
        self._check_for_new_characters()

        # If no current character, get next from queue
        if not self.current_character:
            self.current_character = self._get_next_character()

            if not self.current_character:
                logger.info("No characters in queue. Waiting for new characters...")
                return {
                    'status': 'waiting',
                    'message': '新しいキャラクターを待機中...'
                }

            # Get progress for new character
            progress = self.get_player_progress(self.current_character.id)
            self.current_boss_level = progress.current_level

        # Check if current character has completed story mode
        if self.is_completed(self.current_character.id):
            logger.info(f"Character {self.current_character.name} has completed story mode")

            # Grant endless access via StoryProgress
            progress = self.get_player_progress(self.current_character.id, use_cache=True)
            if not progress.endless_access:
                progress.endless_access = True
                result = self.db_manager.save_story_progress(progress)
                if result:
                    self.progress_cache[self.current_character.id] = progress

            # Move to next character
            completed_char = self.current_character
            self.current_character = None

            return {
                'status': 'completed',
                'character': completed_char,
                'message': f'{completed_char.name} がストーリーモードをクリアしました！エンドレスモードへのアクセスが許可されました。'
            }

        # Start battle with current boss
        logger.info(f"Battle: {self.current_character.name} vs Boss Lv{self.current_boss_level}")

        self.start_battle(self.current_character, self.current_boss_level)
        result = self.execute_battle(visual_mode=visual_mode)

        if not result:
            logger.error("Failed to execute battle")
            return None

        battle = result['battle']
        winner = result['winner']

        # Check if player won
        victory = (winner.id == self.current_character.id)

        # Update progress
        self.update_progress(self.current_character.id, self.current_boss_level, victory)

        if victory:
            logger.info(f"{self.current_character.name} defeated Boss Lv{self.current_boss_level}")

            # Move to next boss level
            self.current_boss_level += 1

            # Check if story completed (defeated Lv5)
            if self.current_boss_level > 5:
                # Grant endless access via StoryProgress
                progress = self.get_player_progress(self.current_character.id, use_cache=False)
                progress.endless_access = True
                result = self.db_manager.save_story_progress(progress)
                if result:
                    self.progress_cache[self.current_character.id] = progress

                completed_char = self.current_character
                self.current_character = None

                return {
                    'status': 'completed',
                    'battle': battle,
                    'character': completed_char,
                    'boss_level': 5,
                    'victory': True,
                    'message': f'{completed_char.name} がストーリーモードをクリアしました！エンドレスモードへのアクセスが許可されました。'
                }

            return {
                'status': 'victory',
                'battle': battle,
                'character': self.current_character,
                'boss_level': self.current_boss_level - 1,
                'next_boss_level': self.current_boss_level,
                'victory': True
            }
        else:
            logger.info(f"{self.current_character.name} was defeated by Boss Lv{self.current_boss_level}")

            # Grant endless access even on defeat (story mode participation grants access)
            progress = self.get_player_progress(self.current_character.id, use_cache=False)
            if not progress.endless_access:
                progress.endless_access = True
                result = self.db_manager.save_story_progress(progress)
                if result:
                    self.progress_cache[self.current_character.id] = progress
                logger.info(f"Granted endless access to {self.current_character.name} after story mode attempt")

            # Character failed - move to next character
            failed_char = self.current_character
            self.current_character = None

            return {
                'status': 'defeated',
                'battle': battle,
                'character': failed_char,
                'boss_level': self.current_boss_level,
                'victory': False,
                'message': f'{failed_char.name} はBoss Lv{self.current_boss_level}に敗北しました。エンドレスモードへのアクセスが許可されました。'
            }

    def _check_for_new_characters(self):
        """Check for new characters and add to queue"""
        try:
            all_characters = self.db_manager.get_all_characters()

            for char in all_characters:
                # Skip characters already in queue or processed
                if char.id in self.processed_character_ids:
                    continue

                # Skip characters with empty stats
                if char.hp == 0 or not char.name:
                    continue

                # Check if character has completed story mode or has endless access
                progress = self.get_player_progress(char.id)
                if progress.completed:
                    self.processed_character_ids.add(char.id)
                    # Grant endless access if not already granted
                    if not progress.endless_access:
                        progress.endless_access = True
                        self.db_manager.save_story_progress(progress)
                    continue

                # Add to queue
                if char.id not in self.character_queue:
                    self.character_queue.append(char.id)
                    logger.info(f"Added character to story queue: {char.name} (ID: {char.id})")

        except Exception as e:
            logger.error(f"Error checking for new characters: {e}")

    def _get_next_character(self) -> Optional[Character]:
        """Get next character from queue"""
        while self.character_queue:
            char_id = self.character_queue.pop(0)

            # Mark as processed
            self.processed_character_ids.add(char_id)

            # Load character
            char = self.db_manager.get_character(char_id)
            if char:
                return char

        return None

    def stop_auto_story_mode(self):
        """Stop auto story mode"""
        self.is_running = False
        self.current_character = None
        self.character_queue.clear()
        self.progress_cache.clear()  # Clear cache when stopping
        logger.info("Auto story mode stopped")
