"""
Story mode battle engine
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
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

    def get_player_progress(self, character_id: str) -> StoryProgress:
        """Get player's story mode progress"""
        try:
            progress = self.db_manager.get_story_progress(character_id)
            if not progress:
                # Create new progress
                progress = StoryProgress(character_id=character_id)
                self.db_manager.save_story_progress(progress)
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
            boss_character = Character(
                id=f"boss_lv{boss_level}",
                name=boss.name,
                hp=boss.hp,
                attack=boss.attack,
                defense=boss.defense,
                speed=boss.speed,
                magic=boss.magic,
                description=boss.description,
                image_path=boss.image_path or "",
                sprite_path=boss.sprite_path or ""
            )

            # Create battle engine
            self.battle_engine = BattleEngine()
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
            progress = self.get_player_progress(character_id)
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

            return self.db_manager.save_story_progress(progress)

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
