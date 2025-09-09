"""
Unit tests for database operations
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.models import Character, Battle, BattleTurn
from src.services.database_manager import DatabaseManager


class TestDatabaseManager:
    """Test DatabaseManager functionality"""
    
    def test_save_and_get_character(self, db_manager, sample_character):
        """Test saving and retrieving a character"""
        # Save character
        success = db_manager.save_character(sample_character)
        assert success
        
        # Retrieve character
        retrieved = db_manager.get_character(sample_character.id)
        assert retrieved is not None
        assert retrieved.name == sample_character.name
        assert retrieved.hp == sample_character.hp
        assert retrieved.attack == sample_character.attack
        assert retrieved.defense == sample_character.defense
        assert retrieved.speed == sample_character.speed
        assert retrieved.magic == sample_character.magic
        assert retrieved.description == sample_character.description
        assert retrieved.image_path == sample_character.image_path
    
    def test_get_nonexistent_character(self, db_manager):
        """Test retrieving a character that doesn't exist"""
        retrieved = db_manager.get_character("nonexistent_id")
        assert retrieved is None
    
    def test_get_character_by_name(self, db_manager, sample_character):
        """Test retrieving character by name"""
        # Use a unique name for this test
        unique_name = f"UniqueTestChar_{sample_character.id[:8]}"
        sample_character.name = unique_name
        
        # Save character
        db_manager.save_character(sample_character)
        
        # Retrieve by name
        retrieved = db_manager.get_character_by_name(unique_name)
        assert retrieved is not None
        assert retrieved.name == unique_name
    
    def test_get_all_characters(self, db_manager, battle_participants):
        """Test retrieving all characters"""
        char1, char2 = battle_participants
        
        # Initially empty
        characters = db_manager.get_all_characters()
        initial_count = len(characters)
        
        # Save characters
        db_manager.save_character(char1)
        db_manager.save_character(char2)
        
        # Retrieve all
        characters = db_manager.get_all_characters()
        assert len(characters) == initial_count + 2
        
        # Check if our characters are in the list
        names = [char.name for char in characters]
        assert char1.name in names
        assert char2.name in names
    
    def test_search_characters(self, db_manager, battle_participants):
        """Test searching characters with filters"""
        char1, char2 = battle_participants
        
        # Save characters
        db_manager.save_character(char1)
        db_manager.save_character(char2)
        
        # Search by name pattern
        results = db_manager.search_characters(name_pattern="War")
        assert len(results) >= 1
        assert any(char.name == "Warrior" for char in results)
        
        # Search by total stats range
        char1_total = char1.total_stats
        results = db_manager.search_characters(
            min_total_stats=char1_total - 10,
            max_total_stats=char1_total + 10
        )
        assert len(results) >= 1
        assert any(char.name == "Warrior" for char in results)
    
    def test_update_character_stats(self, db_manager, sample_character):
        """Test updating character battle statistics"""
        # Save character
        db_manager.save_character(sample_character)
        
        # Update stats (win)
        success = db_manager.update_character_stats(sample_character.id, True)
        assert success
        
        # Retrieve and check
        updated = db_manager.get_character(sample_character.id)
        assert updated.battle_count == 1
        assert updated.win_count == 1
        assert updated.win_rate == 100.0
        
        # Update stats (loss)
        db_manager.update_character_stats(sample_character.id, False)
        
        # Retrieve and check
        updated = db_manager.get_character(sample_character.id)
        assert updated.battle_count == 2
        assert updated.win_count == 1
        assert updated.win_rate == 50.0
    
    def test_delete_character(self, db_manager, sample_character):
        """Test deleting a character"""
        # Save character
        db_manager.save_character(sample_character)
        
        # Verify it exists
        retrieved = db_manager.get_character(sample_character.id)
        assert retrieved is not None
        
        # Delete character
        success = db_manager.delete_character(sample_character.id)
        assert success
        
        # Verify it's gone
        retrieved = db_manager.get_character(sample_character.id)
        assert retrieved is None
    
    def test_delete_character_with_battles(self, db_manager, battle_participants):
        """Test that characters with battle history cannot be deleted"""
        char1, char2 = battle_participants
        
        # Save characters
        db_manager.save_character(char1)
        db_manager.save_character(char2)
        
        # Create and save a battle
        battle = Battle(
            character1_id=char1.id,
            character2_id=char2.id,
            winner_id=char1.id
        )
        db_manager.save_battle(battle)
        
        # Try to delete character with battle history
        success = db_manager.delete_character(char1.id)
        assert not success  # Should fail
        
        # Character should still exist
        retrieved = db_manager.get_character(char1.id)
        assert retrieved is not None


class TestBattleDatabase:
    """Test battle-related database operations"""
    
    def test_save_and_get_battle(self, db_manager, battle_participants):
        """Test saving and retrieving a battle"""
        char1, char2 = battle_participants
        
        # Save characters first
        db_manager.save_character(char1)
        db_manager.save_character(char2)
        
        # Create battle with turns
        battle = Battle(
            character1_id=char1.id,
            character2_id=char2.id,
            winner_id=char1.id,
            duration=15.5
        )
        
        # Add some turns
        turn1 = BattleTurn(
            turn_number=1,
            attacker_id=char1.id,
            defender_id=char2.id,
            action_type="attack",
            damage=25,
            is_critical=False,
            is_miss=False,
            attacker_hp_after=120,
            defender_hp_after=55
        )
        
        turn2 = BattleTurn(
            turn_number=2,
            attacker_id=char2.id,
            defender_id=char1.id,
            action_type="magic",
            damage=30,
            is_critical=True,
            is_miss=False,
            attacker_hp_after=55,
            defender_hp_after=90
        )
        
        battle.add_turn(turn1)
        battle.add_turn(turn2)
        battle.add_log_entry("Battle started!")
        battle.add_log_entry("Warrior attacks Mage for 25 damage")
        battle.add_log_entry("Mage critical magic attack for 30 damage!")
        
        # Save battle
        success = db_manager.save_battle(battle)
        assert success
        
        # Retrieve battle
        retrieved = db_manager.get_battle(battle.id)
        assert retrieved is not None
        assert retrieved.character1_id == battle.character1_id
        assert retrieved.character2_id == battle.character2_id
        assert retrieved.winner_id == battle.winner_id
        assert retrieved.duration == battle.duration
        assert len(retrieved.turns) == 2
        assert len(retrieved.battle_log) == 3
        
        # Check turn details
        retrieved_turn1 = retrieved.turns[0]
        assert retrieved_turn1.turn_number == 1
        assert retrieved_turn1.damage == 25
        assert not retrieved_turn1.is_critical
        
        retrieved_turn2 = retrieved.turns[1]
        assert retrieved_turn2.turn_number == 2
        assert retrieved_turn2.damage == 30
        assert retrieved_turn2.is_critical
        assert retrieved_turn2.action_type == "magic"
    
    def test_get_recent_battles(self, db_manager, battle_participants):
        """Test retrieving recent battles"""
        char1, char2 = battle_participants
        
        # Save characters
        db_manager.save_character(char1)
        db_manager.save_character(char2)
        
        # Save multiple battles
        for i in range(3):
            battle = Battle(
                character1_id=char1.id,
                character2_id=char2.id,
                winner_id=char1.id if i % 2 == 0 else char2.id
            )
            db_manager.save_battle(battle)
        
        # Get recent battles
        recent = db_manager.get_recent_battles(limit=2)
        assert len(recent) == 2
        
        # Should be ordered by creation time (most recent first)
        assert all(isinstance(battle, Battle) for battle in recent)
    
    def test_get_character_battles(self, db_manager, battle_participants):
        """Test retrieving battles for a specific character"""
        char1, char2 = battle_participants
        
        # Create a third character
        char3 = Character(
            name="Archer",
            hp=100, attack=85, defense=55, speed=95, magic=40,
            description="Swift archer", image_path="/test/archer.png"
        )
        
        # Save all characters
        db_manager.save_character(char1)
        db_manager.save_character(char2)
        db_manager.save_character(char3)
        
        # Create battles: char1 vs char2, char1 vs char3
        battle1 = Battle(character1_id=char1.id, character2_id=char2.id, winner_id=char1.id)
        battle2 = Battle(character1_id=char1.id, character2_id=char3.id, winner_id=char3.id)
        battle3 = Battle(character1_id=char2.id, character2_id=char3.id, winner_id=char2.id)
        
        db_manager.save_battle(battle1)
        db_manager.save_battle(battle2)
        db_manager.save_battle(battle3)
        
        # Get char1's battles
        char1_battles = db_manager.get_character_battles(char1.id)
        assert len(char1_battles) == 2  # char1 participated in 2 battles
        
        # Get char2's battles  
        char2_battles = db_manager.get_character_battles(char2.id)
        assert len(char2_battles) == 2  # char2 participated in 2 battles
        
        # Get char3's battles
        char3_battles = db_manager.get_character_battles(char3.id)
        assert len(char3_battles) == 2  # char3 participated in 2 battles


class TestDatabaseStatistics:
    """Test database statistics functionality"""
    
    def test_get_statistics_empty(self, db_manager):
        """Test statistics with empty database"""
        stats = db_manager.get_statistics()
        
        assert 'total_characters' in stats
        assert 'total_battles' in stats
        assert 'average_stats' in stats
        assert 'top_characters' in stats
        
        # With empty database, counts should be 0 or low
        assert isinstance(stats['total_characters'], int)
        assert isinstance(stats['total_battles'], int)
        assert isinstance(stats['average_stats'], dict)
        assert isinstance(stats['top_characters'], list)
    
    def test_get_statistics_with_data(self, db_manager, battle_participants):
        """Test statistics with actual data"""
        char1, char2 = battle_participants
        
        # Save characters
        db_manager.save_character(char1)
        db_manager.save_character(char2)
        
        # Update battle stats
        db_manager.update_character_stats(char1.id, True)  # char1 wins
        db_manager.update_character_stats(char2.id, False)  # char2 loses
        
        db_manager.update_character_stats(char1.id, False)  # char1 loses
        db_manager.update_character_stats(char2.id, True)   # char2 wins
        
        # Get statistics
        stats = db_manager.get_statistics()
        
        assert stats['total_characters'] >= 2
        assert 'hp' in stats['average_stats']
        assert 'attack' in stats['average_stats']
        
        # Should have some top characters
        if stats['total_characters'] > 0:
            assert len(stats['top_characters']) >= 0


class TestDatabaseEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_save_duplicate_character(self, db_manager, sample_character):
        """Test saving the same character twice (should update)"""
        # Save character
        success1 = db_manager.save_character(sample_character)
        assert success1
        
        # Modify and save again
        sample_character.description = "Updated description"
        success2 = db_manager.save_character(sample_character)
        assert success2
        
        # Retrieve and check it was updated
        retrieved = db_manager.get_character(sample_character.id)
        assert retrieved.description == "Updated description"
    
    def test_update_stats_nonexistent_character(self, db_manager):
        """Test updating stats for character that doesn't exist"""
        success = db_manager.update_character_stats("nonexistent_id", True)
        assert not success
    
    def test_delete_nonexistent_character(self, db_manager):
        """Test deleting character that doesn't exist"""
        success = db_manager.delete_character("nonexistent_id")
        assert not success
    
    def test_get_battle_nonexistent(self, db_manager):
        """Test retrieving battle that doesn't exist"""
        battle = db_manager.get_battle("nonexistent_id")
        assert battle is None
    
    def test_search_characters_no_matches(self, db_manager):
        """Test searching with criteria that match nothing"""
        results = db_manager.search_characters(
            name_pattern="NonExistentCharacter",
            min_total_stats=1000,
            max_total_stats=2000
        )
        assert len(results) == 0


@pytest.mark.unit
class TestDatabasePerformance:
    """Test database performance with larger datasets"""
    
    def test_bulk_character_operations(self, db_manager):
        """Test performance with multiple characters"""
        # Create multiple characters
        characters = []
        for i in range(10):
            char = Character(
                name=f"BulkChar{i}",
                hp=100 + i,
                attack=75 + i,
                defense=60 + i,
                speed=85 + i,
                magic=55 + i,
                description=f"Bulk character {i}",
                image_path=f"/test/bulk{i}.png"
            )
            characters.append(char)
        
        # Save all characters
        for char in characters:
            success = db_manager.save_character(char)
            assert success
        
        # Retrieve all characters
        all_chars = db_manager.get_all_characters()
        assert len(all_chars) >= 10
        
        # Search should still work efficiently
        results = db_manager.search_characters(name_pattern="Bulk")
        assert len(results) >= 10