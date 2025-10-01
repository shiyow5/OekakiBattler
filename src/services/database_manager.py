import logging
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models import Character, Battle, BattleTurn
from config.database import execute_query, get_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manage database operations for characters and battles"""
    
    def __init__(self):
        self.connection_cache = {}
    
    def save_character(self, character: Character) -> bool:
        """Save character to database"""
        try:
            query = """
                INSERT OR REPLACE INTO characters 
                (id, name, hp, attack, defense, speed, magic, description, 
                 image_path, sprite_path, created_at, battle_count, win_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                character.id,
                character.name,
                character.hp,
                character.attack,
                character.defense,
                character.speed,
                character.magic,
                character.description,
                character.image_path,
                character.sprite_path,
                character.created_at.isoformat(),
                character.battle_count,
                character.win_count
            )
            
            result = execute_query(query, params)
            
            if result > 0:
                logger.info(f"Character saved successfully: {character.name}")
                return True
            else:
                logger.warning(f"Failed to save character: {character.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving character: {e}")
            return False
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Get character by ID"""
        try:
            query = "SELECT * FROM characters WHERE id = ?"
            result = execute_query(query, (character_id,))
            
            if result and len(result) > 0:
                row = result[0]
                character_data = self._row_to_character_dict(row)
                return Character.from_dict(character_data)
            else:
                logger.warning(f"Character not found: {character_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving character: {e}")
            return None
    
    def get_character_by_name(self, name: str) -> Optional[Character]:
        """Get character by name"""
        try:
            query = "SELECT * FROM characters WHERE name = ?"
            result = execute_query(query, (name,))
            
            if result and len(result) > 0:
                row = result[0]
                character_data = self._row_to_character_dict(row)
                return Character.from_dict(character_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving character by name: {e}")
            return None
    
    def get_all_characters(self) -> List[Character]:
        """Get all characters"""
        try:
            query = "SELECT * FROM characters ORDER BY created_at DESC"
            result = execute_query(query)
            
            characters = []
            if result:
                for row in result:
                    try:
                        character_data = self._row_to_character_dict(row)
                        character = Character.from_dict(character_data)
                        characters.append(character)
                    except Exception as e:
                        logger.warning(f"Error parsing character row: {e}")
                        continue
            
            logger.info(f"Retrieved {len(characters)} characters from database")
            return characters
            
        except Exception as e:
            logger.error(f"Error retrieving characters: {e}")
            return []
    
    def search_characters(self, name_pattern: str = None, min_total_stats: int = None, max_total_stats: int = None) -> List[Character]:
        """Search characters with filters"""
        try:
            conditions = []
            params = []
            
            if name_pattern:
                conditions.append("name LIKE ?")
                params.append(f"%{name_pattern}%")
            
            if min_total_stats is not None:
                conditions.append("(hp + attack + defense + speed + magic) >= ?")
                params.append(min_total_stats)
            
            if max_total_stats is not None:
                conditions.append("(hp + attack + defense + speed + magic) <= ?")
                params.append(max_total_stats)
            
            query = "SELECT * FROM characters"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY created_at DESC"
            
            result = execute_query(query, params if params else None)
            
            characters = []
            if result:
                for row in result:
                    try:
                        character_data = self._row_to_character_dict(row)
                        character = Character.from_dict(character_data)
                        characters.append(character)
                    except Exception as e:
                        logger.warning(f"Error parsing character row: {e}")
                        continue
            
            return characters
            
        except Exception as e:
            logger.error(f"Error searching characters: {e}")
            return []
    
    def delete_character(self, character_id: str, force_delete: bool = False) -> bool:
        """Delete character from database
        
        Args:
            character_id: ID of character to delete
            force_delete: If True, delete character even if it has battle history
        """
        try:
            # Check if character exists in any battles
            battle_check = execute_query(
                "SELECT COUNT(*) FROM battles WHERE character1_id = ? OR character2_id = ?",
                (character_id, character_id)
            )
            
            battle_count = battle_check[0][0] if battle_check and battle_check[0] else 0
            
            if battle_count > 0 and not force_delete:
                logger.warning(f"Cannot delete character {character_id}: has {battle_count} battle(s) in history. Use force_delete=True to override.")
                return False
            
            # If force_delete is True and character has battles, delete related data first
            if force_delete and battle_count > 0:
                logger.info(f"Force deleting character {character_id} with {battle_count} battle(s)")
                
                # Delete battle turns for all battles involving this character
                execute_query(
                    """DELETE FROM battle_turns 
                       WHERE battle_id IN (
                           SELECT id FROM battles 
                           WHERE character1_id = ? OR character2_id = ?
                       )""",
                    (character_id, character_id)
                )
                
                # Delete battles involving this character
                execute_query(
                    "DELETE FROM battles WHERE character1_id = ? OR character2_id = ?",
                    (character_id, character_id)
                )
                
                logger.info(f"Deleted {battle_count} battle(s) and related data for character {character_id}")
            
            # Delete the character
            query = "DELETE FROM characters WHERE id = ?"
            result = execute_query(query, (character_id,))
            
            if result > 0:
                logger.info(f"Character deleted: {character_id}")
                return True
            else:
                logger.warning(f"Character not found for deletion: {character_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting character: {e}")
            return False
    
    def get_character_battle_count(self, character_id: str) -> int:
        """Get the number of battles a character has participated in"""
        try:
            battle_check = execute_query(
                "SELECT COUNT(*) FROM battles WHERE character1_id = ? OR character2_id = ?",
                (character_id, character_id)
            )
            return battle_check[0][0] if battle_check and battle_check[0] else 0
        except Exception as e:
            logger.error(f"Error getting battle count for character {character_id}: {e}")
            return 0
    
    def save_battle(self, battle: Battle) -> bool:
        """Save battle to database"""
        try:
            # Save main battle record
            battle_query = """
                INSERT OR REPLACE INTO battles 
                (id, character1_id, character2_id, winner_id, battle_log, duration, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            battle_params = (
                battle.id,
                battle.character1_id,
                battle.character2_id,
                battle.winner_id,
                '|'.join(battle.battle_log),
                battle.duration,
                battle.created_at.isoformat()
            )
            
            battle_result = execute_query(battle_query, battle_params)
            
            if battle_result <= 0:
                logger.error("Failed to save battle record")
                return False
            
            # Save battle turns
            for turn in battle.turns:
                turn_query = """
                    INSERT OR REPLACE INTO battle_turns
                    (battle_id, turn_number, attacker_id, defender_id, action_type,
                     damage, is_critical, is_miss, attacker_hp_after, defender_hp_after)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                turn_params = (
                    battle.id,
                    turn.turn_number,
                    turn.attacker_id,
                    turn.defender_id,
                    turn.action_type,
                    turn.damage,
                    turn.is_critical,
                    turn.is_miss,
                    turn.attacker_hp_after,
                    turn.defender_hp_after
                )
                
                turn_result = execute_query(turn_query, turn_params)
                if turn_result <= 0:
                    logger.warning(f"Failed to save battle turn {turn.turn_number}")
            
            # Update character battle statistics
            self.update_character_stats(battle.character1_id, battle.winner_id == battle.character1_id)
            self.update_character_stats(battle.character2_id, battle.winner_id == battle.character2_id)
            
            logger.info(f"Battle saved successfully: {battle.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving battle: {e}")
            return False
    
    def get_battle(self, battle_id: str) -> Optional[Battle]:
        """Get battle by ID with all turns"""
        try:
            # Get battle record
            battle_query = "SELECT * FROM battles WHERE id = ?"
            battle_result = execute_query(battle_query, (battle_id,))
            
            if not battle_result or len(battle_result) == 0:
                logger.warning(f"Battle not found: {battle_id}")
                return None
            
            battle_row = battle_result[0]
            battle_data = self._row_to_battle_dict(battle_row)
            battle = Battle.from_dict(battle_data)
            
            # Get battle turns
            turns_query = """
                SELECT * FROM battle_turns 
                WHERE battle_id = ? 
                ORDER BY turn_number
            """
            turns_result = execute_query(turns_query, (battle_id,))
            
            if turns_result:
                for turn_row in turns_result:
                    turn_data = self._row_to_turn_dict(turn_row)
                    battle_turn = BattleTurn(**turn_data)
                    battle.add_turn(battle_turn)
            
            return battle
            
        except Exception as e:
            logger.error(f"Error retrieving battle: {e}")
            return None
    
    def get_recent_battles(self, limit: int = 10) -> List[Battle]:
        """Get recent battles"""
        try:
            query = "SELECT * FROM battles ORDER BY created_at DESC LIMIT ?"
            result = execute_query(query, (limit,))
            
            battles = []
            if result:
                for row in result:
                    try:
                        battle_data = self._row_to_battle_dict(row)
                        battle = Battle.from_dict(battle_data)
                        
                        # Load battle turns
                        self._load_battle_turns(battle)
                        
                        battles.append(battle)
                    except Exception as e:
                        logger.warning(f"Error parsing battle row: {e}")
                        continue
            
            return battles
            
        except Exception as e:
            logger.error(f"Error retrieving recent battles: {e}")
            return []
    
    def get_character_battles(self, character_id: str) -> List[Battle]:
        """Get all battles for a specific character"""
        try:
            query = """
                SELECT * FROM battles 
                WHERE character1_id = ? OR character2_id = ? 
                ORDER BY created_at DESC
            """
            result = execute_query(query, (character_id, character_id))
            
            battles = []
            if result:
                for row in result:
                    try:
                        battle_data = self._row_to_battle_dict(row)
                        battle = Battle.from_dict(battle_data)
                        
                        # Load battle turns
                        self._load_battle_turns(battle)
                        
                        battles.append(battle)
                    except Exception as e:
                        logger.warning(f"Error parsing battle row: {e}")
                        continue
            
            return battles
            
        except Exception as e:
            logger.error(f"Error retrieving character battles: {e}")
            return []
    
    def update_character_stats(self, character_id: str, won: bool) -> bool:
        """Update character battle statistics"""
        try:
            if won:
                query = """
                    UPDATE characters 
                    SET battle_count = battle_count + 1, win_count = win_count + 1
                    WHERE id = ?
                """
            else:
                query = """
                    UPDATE characters 
                    SET battle_count = battle_count + 1
                    WHERE id = ?
                """
            
            result = execute_query(query, (character_id,))
            
            if result > 0:
                logger.debug(f"Updated stats for character {character_id}, won: {won}")
                return True
            else:
                logger.warning(f"Failed to update stats for character {character_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating character stats: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {}
            
            # Character statistics
            char_query = "SELECT COUNT(*) FROM characters"
            char_result = execute_query(char_query)
            stats['total_characters'] = char_result[0][0] if char_result else 0
            
            # Battle statistics
            battle_query = "SELECT COUNT(*) FROM battles"
            battle_result = execute_query(battle_query)
            stats['total_battles'] = battle_result[0][0] if battle_result else 0
            
            # Average character stats
            avg_query = """
                SELECT AVG(hp), AVG(attack), AVG(defense), AVG(speed), AVG(magic)
                FROM characters
            """
            avg_result = execute_query(avg_query)
            if avg_result and avg_result[0][0] is not None:
                stats['average_stats'] = {
                    'hp': round(avg_result[0][0], 1),
                    'attack': round(avg_result[0][1], 1),
                    'defense': round(avg_result[0][2], 1),
                    'speed': round(avg_result[0][3], 1),
                    'magic': round(avg_result[0][4], 1)
                }
            else:
                stats['average_stats'] = {'hp': 0, 'attack': 0, 'defense': 0, 'speed': 0, 'magic': 0}
            
            # Top performing characters
            top_query = """
                SELECT name, win_count, battle_count,
                       CASE WHEN battle_count > 0 THEN ROUND((win_count * 100.0 / battle_count), 1) ELSE 0 END as win_rate
                FROM characters
                WHERE battle_count > 0
                ORDER BY win_rate DESC, win_count DESC
                LIMIT 5
            """
            top_result = execute_query(top_query)
            
            stats['top_characters'] = []
            if top_result:
                for row in top_result:
                    stats['top_characters'].append({
                        'name': row[0],
                        'wins': row[1],
                        'battles': row[2],
                        'win_rate': row[3]
                    })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def _row_to_character_dict(self, row) -> Dict[str, Any]:
        """Convert database row to character dictionary"""
        return {
            'id': row[0],
            'name': row[1],
            'hp': row[2],
            'attack': row[3],
            'defense': row[4],
            'speed': row[5],
            'magic': row[6],
            'description': row[7] if row[7] else "",
            'image_path': row[8],
            'sprite_path': row[9],
            'created_at': row[10],
            'battle_count': row[11],
            'win_count': row[12]
        }
    
    def _row_to_battle_dict(self, row) -> Dict[str, Any]:
        """Convert database row to battle dictionary"""
        return {
            'id': row[0],
            'character1_id': row[1],
            'character2_id': row[2],
            'winner_id': row[3],
            'battle_log': row[4],  # Keep as string, let Battle.from_dict handle the split
            'duration': row[5],
            'created_at': row[6]
        }
    
    def _row_to_turn_dict(self, row) -> Dict[str, Any]:
        """Convert database row to battle turn dictionary"""
        return {
            'turn_number': row[2],
            'attacker_id': row[3],
            'defender_id': row[4],
            'action_type': row[5],
            'damage': row[6],
            'is_critical': bool(row[7]),
            'is_miss': bool(row[8]),
            'attacker_hp_after': row[9],
            'defender_hp_after': row[10]
        }
    
    def _load_battle_turns(self, battle: Battle):
        """Load battle turns for a battle"""
        try:
            turns_query = """
                SELECT * FROM battle_turns 
                WHERE battle_id = ? 
                ORDER BY turn_number
            """
            turns_result = execute_query(turns_query, (battle.id,))
            
            if turns_result:
                for turn_row in turns_result:
                    turn_data = self._row_to_turn_dict(turn_row)
                    battle_turn = BattleTurn(**turn_data)
                    battle.add_turn(battle_turn)
                    
        except Exception as e:
            logger.warning(f"Error loading battle turns for {battle.id}: {e}")