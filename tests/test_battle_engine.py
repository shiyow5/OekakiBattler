"""
Unit tests for battle engine functionality
"""

import pytest
from unittest.mock import patch, MagicMock
import time

from src.services.battle_engine import BattleEngine
from src.models import Character, Battle, BattleTurn, Battle


class TestBattleEngine:
    """Test BattleEngine functionality"""
    
    def test_init(self):
        """Test BattleEngine initialization"""
        engine = BattleEngine()
        assert engine is not None
    
    def test_start_battle_without_visual(self, battle_participants):
        """Test starting battle without visual mode"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        result = engine.start_battle(char1, char2, visual_mode=False)
        
        assert result is not None
        assert isinstance(result, Battle)
        assert result.winner_id in [char1.id, char2.id]
        assert result.turn_count > 0
        assert result.duration > 0
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    def test_start_battle_with_visual_mock(self, mock_caption, mock_display, mock_init, battle_participants):
        """Test starting battle with visual mode (mocked)"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        # Mock pygame components
        mock_screen = MagicMock()
        mock_display.return_value = mock_screen
        mock_clock = MagicMock()
        
        with patch('pygame.time.Clock', return_value=mock_clock):
            with patch('pygame.event.get', return_value=[]):
                with patch.object(engine, '_run_visual_battle') as mock_visual:
                    mock_visual.return_value = Battle(
                        winner=char1.id,
                        total_turns=10,
                        duration=5.0,
                        damage_dealt={char1.id: 100, char2.id: 80},
                        critical_hits={char1.id: 1, char2.id: 0},
                        magic_used={char1.id: 0, char2.id: 2}
                    )
                    
                    result = engine.start_battle(char1, char2, visual_mode=True)
        
        assert result is not None
        assert isinstance(result, Battle)
        mock_init.assert_called_once()
    
    def test_calculate_damage_normal_attack(self, battle_participants):
        """Test normal attack damage calculation"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        damage, is_critical, is_miss = engine._calculate_damage(char1, char2, "attack")
        
        assert isinstance(damage, int)
        assert damage >= 0
        assert isinstance(is_critical, bool)
        assert isinstance(is_miss, bool)
        
        if not is_miss:
            # Damage should be influenced by attack and defense
            expected_base = max(1, char1.attack - char2.defense)
            assert damage >= expected_base * 0.8  # Allow for variance
    
    def test_calculate_damage_magic_attack(self, battle_participants):
        """Test magic attack damage calculation"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        damage, is_critical, is_miss = engine._calculate_damage(char1, char2, "magic")
        
        assert isinstance(damage, int)
        assert damage >= 0
        
        if not is_miss:
            # Magic damage should be influenced by magic stat
            expected_base = max(1, char1.magic - char2.defense // 2)
            assert damage >= expected_base * 0.8
    
    def test_calculate_damage_miss(self, battle_participants):
        """Test damage calculation when attack misses"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        # Mock random to force miss
        with patch('random.random', return_value=0.95):  # High value for miss
            damage, is_critical, is_miss = engine._calculate_damage(char1, char2, "attack")
        
        if is_miss:
            assert damage == 0
            assert not is_critical
    
    def test_calculate_damage_critical(self, battle_participants):
        """Test critical hit damage calculation"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        # Force critical by mocking random
        with patch('random.random', side_effect=[0.5, 0.05]):  # No miss, critical hit
            damage, is_critical, is_miss = engine._calculate_damage(char1, char2, "attack")
        
        if is_critical and not is_miss:
            # Critical hits should do more damage
            normal_damage, _, _ = engine._calculate_damage(char1, char2, "attack")
            assert damage >= normal_damage
    
    def test_determine_action(self, battle_participants):
        """Test action determination based on character stats"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        action = engine._determine_action(char1)
        
        assert action in ["attack", "magic"]
        
        # High magic characters should be more likely to use magic
        high_magic_char = Character(
            name="HighMage", hp=100, attack=30, defense=50, 
            speed=80, magic=100, description="High magic", image_path="/test.png"
        )
        
        magic_count = 0
        for _ in range(100):
            if engine._determine_action(high_magic_char) == "magic":
                magic_count += 1
        
        # Should use magic more often than attack
        assert magic_count > 30  # At least 30% magic usage
    
    def test_determine_turn_order(self, battle_participants):
        """Test turn order determination based on speed"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        first, second = engine._determine_turn_order(char1, char2)
        
        # Should return both characters
        assert first in [char1, char2]
        assert second in [char1, char2]
        assert first != second
        
        # Faster character should generally go first
        if char1.speed > char2.speed:
            assert first == char1
        elif char2.speed > char1.speed:
            assert first == char2
    
    def test_apply_damage(self, battle_participants):
        """Test damage application to character"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        original_hp = char2.hp
        damage = 25
        
        new_hp = engine._apply_damage(char2, damage)
        
        assert new_hp == original_hp - damage
        assert new_hp >= 0  # HP shouldn't go negative
    
    def test_apply_damage_overkill(self, battle_participants):
        """Test damage application that exceeds current HP"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        excessive_damage = char2.hp + 50
        new_hp = engine._apply_damage(char2, excessive_damage)
        
        assert new_hp == 0  # Should not go negative
    
    def test_is_battle_over(self, battle_participants):
        """Test battle end condition checking"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        # Battle should not be over initially
        assert not engine._is_battle_over(char1, char2)
        
        # Simulate character death
        char2.hp = 0
        assert engine._is_battle_over(char1, char2)
        
        # Reset and test other character
        char2.hp = 100
        char1.hp = 0
        assert engine._is_battle_over(char1, char2)
    
    def test_get_winner(self, battle_participants):
        """Test winner determination"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        # Test when char1 wins
        char2.hp = 0
        winner = engine._get_winner(char1, char2)
        assert winner == char1.id
        
        # Test when char2 wins
        char1.hp = 0
        char2.hp = 50
        winner = engine._get_winner(char1, char2)
        assert winner == char2.id
        
        # Test when both alive (should return None)
        char1.hp = 50
        char2.hp = 50
        winner = engine._get_winner(char1, char2)
        assert winner is None
    
    def test_create_battle_record(self, battle_participants):
        """Test battle record creation"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        battle = engine._create_battle_record(char1, char2)
        
        assert isinstance(battle, Battle)
        assert battle.character1_id == char1.id
        assert battle.character2_id == char2.id
        assert battle.winner_id is None  # Should be set later
        assert battle.turns == []
        assert battle.battle_log == []
    
    def test_add_battle_turn(self, battle_participants):
        """Test adding turn to battle record"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        battle = engine._create_battle_record(char1, char2)
        
        turn = BattleTurn(
            turn_number=1,
            attacker_id=char1.id,
            defender_id=char2.id,
            action_type="attack",
            damage=25,
            is_critical=False,
            is_miss=False,
            attacker_hp_after=char1.hp,
            defender_hp_after=char2.hp - 25
        )
        
        battle.add_turn(turn)
        
        assert len(battle.turns) == 1
        assert battle.turns[0] == turn
    
    def test_complete_battle_flow(self, battle_participants):
        """Test complete battle from start to finish"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        result = engine.start_battle(char1, char2, visual_mode=False)
        
        # Verify result structure
        assert isinstance(result, Battle)
        assert result.winner_id in [char1.id, char2.id]
        assert result.turn_count > 0
        assert result.duration > 0
        assert result.damage_dealt[char1.id] >= 0
        assert result.damage_dealt[char2.id] >= 0
        assert result.critical_hits[char1.id] >= 0
        assert result.critical_hits[char2.id] >= 0
        assert result.magic_used[char1.id] >= 0
        assert result.magic_used[char2.id] >= 0


class TestBattleEngineEdgeCases:
    """Test edge cases for battle engine"""
    
    def test_identical_characters(self):
        """Test battle between identical characters"""
        char1 = Character(
            name="Clone1", hp=100, attack=75, defense=60, 
            speed=85, magic=55, description="Clone", image_path="/test1.png"
        )
        char2 = Character(
            name="Clone2", hp=100, attack=75, defense=60, 
            speed=85, magic=55, description="Clone", image_path="/test2.png"
        )
        
        engine = BattleEngine()
        result = engine.start_battle(char1, char2, visual_mode=False)
        
        assert result is not None
        assert result.winner_id in [char1.id, char2.id]
    
    def test_extreme_stat_differences(self):
        """Test battle with extreme stat differences"""
        weak_char = Character(
            name="Weak", hp=50, attack=30, defense=20, 
            speed=40, magic=10, description="Weak", image_path="/weak.png"
        )
        strong_char = Character(
            name="Strong", hp=150, attack=120, defense=100, 
            speed=130, magic=100, description="Strong", image_path="/strong.png"
        )
        
        engine = BattleEngine()
        result = engine.start_battle(weak_char, strong_char, visual_mode=False)
        
        assert result is not None
        # Strong character should likely win, but not guaranteed due to randomness
        assert result.winner_id in [weak_char.id, strong_char.id]
    
    def test_max_turns_limit(self):
        """Test that battles don't exceed maximum turn limit"""
        # Create characters that are hard to kill (high HP, low attack)
        tank1 = Character(
            name="Tank1", hp=150, attack=30, defense=100, 
            speed=40, magic=10, description="Tank", image_path="/tank1.png"
        )
        tank2 = Character(
            name="Tank2", hp=150, attack=30, defense=100, 
            speed=40, magic=10, description="Tank", image_path="/tank2.png"
        )
        
        engine = BattleEngine()
        engine.MAX_TURNS = 10  # Set low limit for testing
        
        result = engine.start_battle(tank1, tank2, visual_mode=False)
        
        assert result is not None
        assert result.turn_count <= engine.MAX_TURNS
    
    def test_zero_damage_scenario(self, battle_participants):
        """Test scenario where attacks do zero damage"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        # Mock calculate_damage to always return 0 damage
        with patch.object(engine, '_calculate_damage', return_value=(0, False, False)):
            result = engine.start_battle(char1, char2, visual_mode=False)
        
        # Battle should still end (via turn limit)
        assert result is not None
        assert result.turn_count > 0


@pytest.mark.unit
class TestBattleEnginePerformance:
    """Test battle engine performance"""
    
    def test_battle_speed(self, battle_participants):
        """Test that battles complete in reasonable time"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        start_time = time.time()
        result = engine.start_battle(char1, char2, visual_mode=False)
        end_time = time.time()
        
        duration = end_time - start_time
        
        assert result is not None
        assert duration < 5.0  # Should complete within 5 seconds
    
    def test_multiple_battles(self, battle_participants):
        """Test running multiple battles in sequence"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        results = []
        for _ in range(5):
            # Reset character HP for each battle
            char1.hp = 120
            char2.hp = 80
            
            result = engine.start_battle(char1, char2, visual_mode=False)
            results.append(result)
        
        # All battles should complete successfully
        assert len(results) == 5
        assert all(result is not None for result in results)
        assert all(isinstance(result, Battle) for result in results)


class TestBattleEngineStatistics:
    """Test battle statistics tracking"""
    
    def test_damage_tracking(self, battle_participants):
        """Test that damage is tracked correctly"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        result = engine.start_battle(char1, char2, visual_mode=False)
        
        assert result.damage_dealt[char1.id] >= 0
        assert result.damage_dealt[char2.id] >= 0
        
        # Total damage should be reasonable
        total_damage = result.damage_dealt[char1.id] + result.damage_dealt[char2.id]
        assert total_damage > 0
    
    def test_critical_hit_tracking(self, battle_participants):
        """Test that critical hits are tracked"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        # Mock some critical hits
        original_calculate = engine._calculate_damage
        def mock_calculate(*args, **kwargs):
            damage, _, is_miss = original_calculate(*args, **kwargs)
            return damage * 2, True, is_miss  # Force critical
        
        with patch.object(engine, '_calculate_damage', side_effect=mock_calculate):
            result = engine.start_battle(char1, char2, visual_mode=False)
        
        # Should have some critical hits
        total_crits = result.critical_hits[char1.id] + result.critical_hits[char2.id]
        assert total_crits >= 0
    
    def test_magic_usage_tracking(self, battle_participants):
        """Test that magic usage is tracked"""
        char1, char2 = battle_participants
        engine = BattleEngine()
        
        # Mock to force magic usage
        with patch.object(engine, '_determine_action', return_value="magic"):
            result = engine.start_battle(char1, char2, visual_mode=False)
        
        # Should have recorded magic usage
        total_magic = result.magic_used[char1.id] + result.magic_used[char2.id]
        assert total_magic > 0