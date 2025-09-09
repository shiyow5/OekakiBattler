"""
Unit tests for data models
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models import Character, CharacterStats, Battle, BattleTurn, BattleResult


class TestCharacterStats:
    """Test CharacterStats model"""
    
    def test_valid_character_stats(self, sample_character_stats):
        """Test creating valid character stats"""
        stats = sample_character_stats
        assert stats.hp == 100
        assert stats.attack == 75
        assert stats.defense == 60
        assert stats.speed == 85
        assert stats.magic == 55
        assert stats.description == "Test character stats"
    
    def test_character_stats_validation(self):
        """Test character stats validation"""
        # Test HP validation
        with pytest.raises(ValidationError):
            CharacterStats(hp=49, attack=75, defense=60, speed=85, magic=55, description="Test")
        
        with pytest.raises(ValidationError):
            CharacterStats(hp=151, attack=75, defense=60, speed=85, magic=55, description="Test")
        
        # Test attack validation
        with pytest.raises(ValidationError):
            CharacterStats(hp=100, attack=29, defense=60, speed=85, magic=55, description="Test")
        
        with pytest.raises(ValidationError):
            CharacterStats(hp=100, attack=121, defense=60, speed=85, magic=55, description="Test")
        
        # Test defense validation
        with pytest.raises(ValidationError):
            CharacterStats(hp=100, attack=75, defense=19, speed=85, magic=55, description="Test")
        
        with pytest.raises(ValidationError):
            CharacterStats(hp=100, attack=75, defense=101, speed=85, magic=55, description="Test")
        
        # Test speed validation
        with pytest.raises(ValidationError):
            CharacterStats(hp=100, attack=75, defense=60, speed=39, magic=55, description="Test")
        
        with pytest.raises(ValidationError):
            CharacterStats(hp=100, attack=75, defense=60, speed=131, magic=55, description="Test")
        
        # Test magic validation
        with pytest.raises(ValidationError):
            CharacterStats(hp=100, attack=75, defense=60, speed=85, magic=9, description="Test")
        
        with pytest.raises(ValidationError):
            CharacterStats(hp=100, attack=75, defense=60, speed=85, magic=101, description="Test")


class TestCharacter:
    """Test Character model"""
    
    def test_valid_character(self, sample_character):
        """Test creating valid character"""
        char = sample_character
        assert char.name == "TestCharacter"
        assert char.hp == 100
        assert char.attack == 75
        assert char.defense == 60
        assert char.speed == 85
        assert char.magic == 55
        assert char.description == "A test character for unit testing"
        assert char.image_path == "/test/path/character.png"
        assert char.battle_count == 0
        assert char.win_count == 0
        assert char.id is not None
        assert isinstance(char.created_at, datetime)
    
    def test_character_properties(self, sample_character):
        """Test character calculated properties"""
        char = sample_character
        
        # Test win rate with no battles
        assert char.win_rate == 0.0
        
        # Test win rate with battles
        char.battle_count = 10
        char.win_count = 7
        assert char.win_rate == 70.0
        
        # Test total stats
        expected_total = char.hp + char.attack + char.defense + char.speed + char.magic
        assert char.total_stats == expected_total
    
    def test_character_serialization(self, sample_character):
        """Test character to_dict and from_dict"""
        char = sample_character
        
        # Test to_dict
        char_dict = char.to_dict()
        assert isinstance(char_dict, dict)
        assert char_dict['name'] == char.name
        assert char_dict['hp'] == char.hp
        assert char_dict['id'] == char.id
        
        # Test from_dict
        restored_char = Character.from_dict(char_dict)
        assert restored_char.name == char.name
        assert restored_char.hp == char.hp
        assert restored_char.id == char.id
        assert restored_char.created_at == char.created_at
    
    def test_character_validation(self):
        """Test character validation"""
        # Test invalid HP
        with pytest.raises(ValidationError):
            Character(
                name="Test", hp=49, attack=75, defense=60, 
                speed=85, magic=55, description="Test", image_path="test.png"
            )
        
        # Test missing required fields
        with pytest.raises(ValidationError):
            Character(hp=100, attack=75, defense=60, speed=85, magic=55)


class TestBattleTurn:
    """Test BattleTurn model"""
    
    def test_valid_battle_turn(self):
        """Test creating valid battle turn"""
        turn = BattleTurn(
            turn_number=1,
            attacker_id="char1",
            defender_id="char2",
            action_type="attack",
            damage=25,
            is_critical=False,
            is_miss=False,
            attacker_hp_after=100,
            defender_hp_after=75
        )
        
        assert turn.turn_number == 1
        assert turn.attacker_id == "char1"
        assert turn.defender_id == "char2"
        assert turn.action_type == "attack"
        assert turn.damage == 25
        assert not turn.is_critical
        assert not turn.is_miss
        assert turn.attacker_hp_after == 100
        assert turn.defender_hp_after == 75
    
    def test_critical_hit_turn(self):
        """Test critical hit battle turn"""
        turn = BattleTurn(
            turn_number=2,
            attacker_id="char2",
            defender_id="char1",
            action_type="attack",
            damage=50,
            is_critical=True,
            is_miss=False,
            attacker_hp_after=75,
            defender_hp_after=50
        )
        
        assert turn.is_critical
        assert turn.damage == 50
    
    def test_miss_turn(self):
        """Test miss battle turn"""
        turn = BattleTurn(
            turn_number=3,
            attacker_id="char1",
            defender_id="char2",
            action_type="attack",
            damage=0,
            is_critical=False,
            is_miss=True,
            attacker_hp_after=50,
            defender_hp_after=75
        )
        
        assert turn.is_miss
        assert turn.damage == 0


class TestBattle:
    """Test Battle model"""
    
    def test_valid_battle(self):
        """Test creating valid battle"""
        battle = Battle(
            character1_id="char1",
            character2_id="char2"
        )
        
        assert battle.character1_id == "char1"
        assert battle.character2_id == "char2"
        assert battle.winner_id is None
        assert battle.battle_log == []
        assert battle.turns == []
        assert battle.duration == 0.0
        assert battle.id is not None
        assert isinstance(battle.created_at, datetime)
    
    def test_battle_properties(self):
        """Test battle calculated properties"""
        battle = Battle(
            character1_id="char1",
            character2_id="char2"
        )
        
        # Test initial state
        assert not battle.is_finished
        assert battle.turn_count == 0
        
        # Add turns
        turn1 = BattleTurn(
            turn_number=1, attacker_id="char1", defender_id="char2",
            action_type="attack", damage=25, is_critical=False, is_miss=False,
            attacker_hp_after=100, defender_hp_after=75
        )
        battle.add_turn(turn1)
        
        assert battle.turn_count == 1
        assert not battle.is_finished
        
        # Set winner
        battle.winner_id = "char1"
        assert battle.is_finished
    
    def test_battle_log(self):
        """Test battle log functionality"""
        battle = Battle(
            character1_id="char1",
            character2_id="char2"
        )
        
        # Add log entries
        battle.add_log_entry("Battle started!")
        battle.add_log_entry("Character 1 attacks!")
        
        assert len(battle.battle_log) == 2
        assert battle.battle_log[0] == "Battle started!"
        assert battle.battle_log[1] == "Character 1 attacks!"
    
    def test_battle_serialization(self):
        """Test battle to_dict and from_dict"""
        battle = Battle(
            character1_id="char1",
            character2_id="char2",
            winner_id="char1"
        )
        battle.add_log_entry("Test log entry")
        battle.duration = 15.5
        
        # Test to_dict
        battle_dict = battle.to_dict()
        assert isinstance(battle_dict, dict)
        assert battle_dict['character1_id'] == "char1"
        assert battle_dict['character2_id'] == "char2"
        assert battle_dict['winner_id'] == "char1"
        assert battle_dict['duration'] == 15.5
        assert "Test log entry" in battle_dict['battle_log']
        
        # Test from_dict
        restored_battle = Battle.from_dict(battle_dict)
        assert restored_battle.character1_id == battle.character1_id
        assert restored_battle.character2_id == battle.character2_id
        assert restored_battle.winner_id == battle.winner_id
        assert restored_battle.duration == battle.duration
        assert restored_battle.battle_log == battle.battle_log


class TestBattleResult:
    """Test BattleResult model"""
    
    def test_valid_battle_result(self):
        """Test creating valid battle result"""
        result = BattleResult(
            winner="char1",
            total_turns=15,
            duration=25.5,
            damage_dealt={"char1": 120, "char2": 85},
            critical_hits={"char1": 2, "char2": 1},
            magic_used={"char1": 0, "char2": 3}
        )
        
        assert result.winner == "char1"
        assert result.total_turns == 15
        assert result.duration == 25.5
        assert result.damage_dealt["char1"] == 120
        assert result.damage_dealt["char2"] == 85
        assert result.critical_hits["char1"] == 2
        assert result.magic_used["char2"] == 3
    
    def test_empty_battle_result(self):
        """Test creating empty battle result"""
        result = BattleResult()
        
        assert result.winner is None
        assert result.total_turns == 0
        assert result.duration == 0.0
        assert result.damage_dealt == {}
        assert result.critical_hits == {}
        assert result.magic_used == {}


@pytest.mark.unit
class TestModelEdgeCases:
    """Test edge cases for models"""
    
    def test_character_extreme_values(self):
        """Test character with extreme but valid values"""
        char = Character(
            name="ExtremeChar",
            hp=150,  # Max HP
            attack=120,  # Max attack
            defense=100,  # Max defense
            speed=130,  # Max speed
            magic=100,  # Max magic
            description="Extreme character",
            image_path="extreme.png"
        )
        
        assert char.total_stats == 600
        assert char.win_rate == 0.0
    
    def test_character_minimum_values(self):
        """Test character with minimum valid values"""
        char = Character(
            name="MinChar",
            hp=50,   # Min HP
            attack=30,   # Min attack
            defense=20,  # Min defense
            speed=40,    # Min speed
            magic=10,    # Min magic
            description="Minimum character",
            image_path="min.png"
        )
        
        assert char.total_stats == 150
    
    def test_long_character_name(self):
        """Test character with very long name"""
        long_name = "A" * 100
        char = Character(
            name=long_name,
            hp=100, attack=75, defense=60, speed=85, magic=55,
            description="Test", image_path="test.png"
        )
        
        assert len(char.name) == 100
        assert char.name == long_name
    
    def test_unicode_character_name(self):
        """Test character with unicode name"""
        unicode_name = "テストキャラクター🗡️"
        char = Character(
            name=unicode_name,
            hp=100, attack=75, defense=60, speed=85, magic=55,
            description="Unicode test", image_path="test.png"
        )
        
        assert char.name == unicode_name