"""
Endless Battle Engine - Tournament-style endless battle system
"""

import logging
import time
import random
from typing import List, Optional, Dict, Any
from src.models import Character, Battle
from src.services.battle_engine import BattleEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EndlessBattleEngine:
    """Manages endless tournament-style battles"""

    def __init__(self, db_manager, battle_engine: BattleEngine):
        self.db_manager = db_manager
        self.battle_engine = battle_engine
        self.is_running = False
        self.current_champion: Optional[Character] = None
        self.participants: List[Character] = []
        self.battle_count = 0
        self.champion_wins = 0
        self.known_character_ids = set()

    def start_endless_battle(self, visual_mode: bool = False):
        """
        Start endless battle mode

        Args:
            visual_mode: Whether to show visual battle display
        """
        logger.info("Starting endless battle mode")
        self.is_running = True
        self.battle_count = 0

        # Load initial characters
        self._load_characters()

        if not self.participants:
            logger.error("No characters available for endless battle")
            return None

        # Select random first champion
        self.current_champion = random.choice(self.participants)
        self.participants.remove(self.current_champion)
        self.champion_wins = 0

        logger.info(f"Initial champion: {self.current_champion.name}")

        return {
            'status': 'started',
            'champion': self.current_champion,
            'remaining_count': len(self.participants)
        }

    def run_next_battle(self, visual_mode: bool = False) -> Optional[Dict[str, Any]]:
        """
        Run the next battle in the endless tournament

        Args:
            visual_mode: Whether to show visual battle display

        Returns:
            Battle result dictionary or None if waiting for new characters
        """
        if not self.is_running:
            logger.warning("Endless battle not running")
            return None

        # Check for new characters
        self._check_for_new_characters()

        # If no participants, wait for new characters
        if not self.participants:
            logger.info("No challengers available. Waiting for new characters...")
            return {
                'status': 'waiting',
                'champion': self.current_champion,
                'champion_wins': self.champion_wins,
                'message': 'チャンピオンが新たな挑戦者を待っています...'
            }

        # Select random challenger
        challenger = random.choice(self.participants)
        self.participants.remove(challenger)

        logger.info(f"Battle {self.battle_count + 1}: {self.current_champion.name} vs {challenger.name}")

        # Execute battle
        battle = self.battle_engine.start_battle(
            self.current_champion,
            challenger,
            visual_mode=visual_mode
        )

        self.battle_count += 1

        # Determine new champion
        if battle.winner_id == self.current_champion.id:
            # Champion wins
            self.champion_wins += 1
            # Add challenger back to pool (optional: could be eliminated)
            # self.participants.append(challenger)
            winner = self.current_champion
            loser = challenger
        elif battle.winner_id == challenger.id:
            # Challenger wins, becomes new champion
            # Old champion goes back to pool (optional: could be eliminated)
            # self.participants.append(self.current_champion)
            self.current_champion = challenger
            self.champion_wins = 1
            winner = challenger
            loser = self.current_champion
        else:
            # Draw - both return to pool
            self.participants.append(challenger)
            winner = None
            loser = None

        return {
            'status': 'battle_complete',
            'battle': battle,
            'champion': self.current_champion,
            'champion_wins': self.champion_wins,
            'remaining_count': len(self.participants),
            'battle_count': self.battle_count,
            'winner': winner,
            'loser': loser
        }

    def _load_characters(self):
        """Load all characters from database"""
        try:
            all_characters = self.db_manager.get_all_characters()
            self.participants = [c for c in all_characters if c.hp > 0]
            self.known_character_ids = {c.id for c in all_characters}
            logger.info(f"Loaded {len(self.participants)} characters")
        except Exception as e:
            logger.error(f"Error loading characters: {e}")
            self.participants = []

    def _check_for_new_characters(self):
        """Check for newly added characters and add them to participants"""
        try:
            all_characters = self.db_manager.get_all_characters()
            new_characters = [
                c for c in all_characters
                if c.id not in self.known_character_ids and c.hp > 0
            ]

            if new_characters:
                logger.info(f"Found {len(new_characters)} new character(s)")
                self.participants.extend(new_characters)
                self.known_character_ids.update(c.id for c in new_characters)

                for char in new_characters:
                    logger.info(f"New challenger joins: {char.name}")

        except Exception as e:
            logger.error(f"Error checking for new characters: {e}")

    def stop(self):
        """Stop endless battle mode"""
        logger.info("Stopping endless battle mode")
        self.is_running = False

        return {
            'status': 'stopped',
            'total_battles': self.battle_count,
            'final_champion': self.current_champion,
            'champion_wins': self.champion_wins
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current status of endless battle"""
        return {
            'is_running': self.is_running,
            'champion': self.current_champion.name if self.current_champion else None,
            'champion_wins': self.champion_wins,
            'remaining_challengers': len(self.participants),
            'total_battles': self.battle_count
        }
