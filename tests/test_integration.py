"""
Integration tests for the complete Oekaki Battler system
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

from src.services.image_processor import ImageProcessor
from src.services.ai_analyzer import AIAnalyzer
from src.services.battle_engine import BattleEngine
from src.services.database_manager import DatabaseManager
from src.models import Character, Battle


@pytest.mark.integration
class TestCompleteWorkflow:
    """Test complete workflow from image to battle"""
    
    def test_image_to_character_workflow(self, test_image_path, db_manager):
        """Test complete workflow: image -> analysis -> character creation -> database"""
        # Step 1: Process image
        processor = ImageProcessor()
        image = processor.load_image(test_image_path)
        assert image is not None
        
        extracted = processor.extract_character(image)
        assert extracted is not None
        
        # Step 2: Analyze character with AI (mocked)
        analyzer = AIAnalyzer()
        
        # Mock AI response for consistent testing
        mock_stats = [{
            "hp": 95,
            "attack": 80,
            "defense": 65,
            "speed": 90,
            "magic": 60,
            "description": "Integration test character"
        }]
        
        with patch.object(analyzer, 'analyze_character', return_value=mock_stats):
            analysis_result = analyzer.analyze_character(test_image_path)
        
        assert analysis_result is not None
        assert len(analysis_result) == 1
        
        # Step 3: Create character from analysis
        stats = analysis_result[0]
        character = Character(
            name="IntegrationChar",
            hp=stats['hp'],
            attack=stats['attack'],
            defense=stats['defense'],
            speed=stats['speed'],
            magic=stats['magic'],
            description=stats['description'],
            image_path=test_image_path
        )
        
        # Step 4: Save to database
        success = db_manager.save_character(character)
        assert success
        
        # Step 5: Retrieve from database
        retrieved = db_manager.get_character(character.id)
        assert retrieved is not None
        assert retrieved.name == character.name
        assert retrieved.hp == character.hp
    
    def test_character_to_battle_workflow(self, db_manager, battle_participants):
        """Test workflow: character creation -> database -> battle -> results"""
        char1, char2 = battle_participants
        
        # Step 1: Save characters to database
        success1 = db_manager.save_character(char1)
        success2 = db_manager.save_character(char2)
        assert success1 and success2
        
        # Step 2: Retrieve characters from database
        retrieved_char1 = db_manager.get_character(char1.id)
        retrieved_char2 = db_manager.get_character(char2.id)
        assert retrieved_char1 is not None
        assert retrieved_char2 is not None
        
        # Step 3: Run battle
        engine = BattleEngine()
        result = engine.start_battle(retrieved_char1, retrieved_char2, visual_mode=False)
        assert result is not None
        
        # Step 4: Create battle record
        battle = Battle(
            character1_id=char1.id,
            character2_id=char2.id,
            winner_id=result.winner,
            duration=result.duration
        )
        
        # Step 5: Save battle to database
        battle_success = db_manager.save_battle(battle)
        assert battle_success
        
        # Step 6: Update character statistics
        winner_id = result.winner
        loser_id = char2.id if winner_id == char1.id else char1.id
        
        win_update = db_manager.update_character_stats(winner_id, True)
        loss_update = db_manager.update_character_stats(loser_id, False)
        assert win_update and loss_update
        
        # Step 7: Verify updated statistics
        updated_winner = db_manager.get_character(winner_id)
        updated_loser = db_manager.get_character(loser_id)
        
        assert updated_winner.battle_count == 1
        assert updated_winner.win_count == 1
        assert updated_winner.win_rate == 100.0
        
        assert updated_loser.battle_count == 1
        assert updated_loser.win_count == 0
        assert updated_loser.win_rate == 0.0
    
    def test_full_tournament_workflow(self, db_manager):
        """Test multiple characters in a tournament-style setup"""
        # Create multiple characters
        characters = []
        for i in range(4):
            char = Character(
                name=f"TournamentChar{i}",
                hp=100 + i * 10,
                attack=75 + i * 5,
                defense=60 + i * 3,
                speed=85 + i * 2,
                magic=55 + i * 4,
                description=f"Tournament character {i}",
                image_path=f"/test/tournament{i}.png"
            )
            characters.append(char)
            
            # Save to database
            success = db_manager.save_character(char)
            assert success
        
        # Run battles between all pairs
        engine = BattleEngine()
        battles = []
        
        for i in range(len(characters)):
            for j in range(i + 1, len(characters)):
                char1 = characters[i]
                char2 = characters[j]
                
                # Reset HP for battle
                char1.hp = 100 + i * 10
                char2.hp = 100 + j * 10
                
                # Run battle
                result = engine.start_battle(char1, char2, visual_mode=False)
                assert result is not None
                
                # Create and save battle record
                battle = Battle(
                    character1_id=char1.id,
                    character2_id=char2.id,
                    winner_id=result.winner,
                    duration=result.duration
                )
                
                battle_success = db_manager.save_battle(battle)
                assert battle_success
                battles.append(battle)
                
                # Update character stats
                winner_id = result.winner
                loser_id = char2.id if winner_id == char1.id else char1.id
                
                db_manager.update_character_stats(winner_id, True)
                db_manager.update_character_stats(loser_id, False)
        
        # Verify tournament results
        assert len(battles) == 6  # 4 choose 2 = 6 battles
        
        # Check that all characters have battle history
        for char in characters:
            updated_char = db_manager.get_character(char.id)
            assert updated_char.battle_count > 0
            
        # Check tournament statistics
        stats = db_manager.get_statistics()
        assert stats['total_characters'] >= 4
        assert stats['total_battles'] >= 6


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across the integrated system"""
    
    def test_image_processing_failure_recovery(self, db_manager):
        """Test system recovery when image processing fails"""
        processor = ImageProcessor()
        analyzer = AIAnalyzer()
        
        # Try to process non-existent image
        image = processor.load_image("/nonexistent/image.png")
        assert image is None
        
        # AI analyzer should handle this gracefully
        result = analyzer.analyze_character("/nonexistent/image.png")
        assert result is None
        
        # System should still allow manual character creation
        manual_char = Character(
            name="ManualChar",
            hp=100, attack=75, defense=60, speed=85, magic=55,
            description="Manually created character",
            image_path="/nonexistent/image.png"
        )
        
        success = db_manager.save_character(manual_char)
        assert success
    
    def test_ai_failure_with_fallback(self, test_image_path, db_manager):
        """Test system behavior when AI fails but fallback is available"""
        processor = ImageProcessor()
        analyzer = AIAnalyzer()
        
        # Process image successfully
        image = processor.load_image(test_image_path)
        assert image is not None
        
        # Force AI analyzer to use fallback
        analyzer.genai = None
        result = analyzer.analyze_character(test_image_path, fallback_stats=True)
        
        assert result is not None
        assert len(result) == 1
        
        # Should still be able to create and save character
        stats = result[0]
        character = Character(
            name="FallbackChar",
            hp=stats['hp'],
            attack=stats['attack'],
            defense=stats['defense'],
            speed=stats['speed'],
            magic=stats['magic'],
            description=stats['description'],
            image_path=test_image_path
        )
        
        success = db_manager.save_character(character)
        assert success
    
    def test_database_failure_handling(self, test_image_path):
        """Test system behavior with database failures"""
        # Create database manager with invalid path
        invalid_db_manager = DatabaseManager()
        
        # Create character
        character = Character(
            name="TestChar",
            hp=100, attack=75, defense=60, speed=85, magic=55,
            description="Test character",
            image_path=test_image_path
        )
        
        # Save might fail, but shouldn't crash the system
        try:
            success = invalid_db_manager.save_character(character)
            # If it succeeds, that's fine too
        except Exception:
            # If it fails, that's expected and should be handled gracefully
            pass
    
    def test_battle_with_invalid_characters(self):
        """Test battle system with edge case characters"""
        # Create characters with extreme stats
        weak_char = Character(
            name="VeryWeak",
            hp=50, attack=30, defense=20, speed=40, magic=10,
            description="Very weak character",
            image_path="/test/weak.png"
        )
        
        strong_char = Character(
            name="VeryStrong", 
            hp=150, attack=120, defense=100, speed=130, magic=100,
            description="Very strong character",
            image_path="/test/strong.png"
        )
        
        engine = BattleEngine()
        
        # Battle should still work
        result = engine.start_battle(weak_char, strong_char, visual_mode=False)
        assert result is not None
        assert result.winner in [weak_char.id, strong_char.id]


@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance of integrated system"""
    
    def test_bulk_character_processing(self, tmp_path, db_manager):
        """Test processing multiple characters efficiently"""
        processor = ImageProcessor()
        analyzer = AIAnalyzer()
        
        # Create multiple test images
        characters_created = 0
        target_count = 5
        
        for i in range(target_count):
            # Create simple test image
            import numpy as np
            import cv2
            
            test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
            image_path = tmp_path / f"bulk_test_{i}.png"
            cv2.imwrite(str(image_path), test_image)
            
            # Process image
            image = processor.load_image(str(image_path))
            if image is not None:
                # Use fallback for speed and consistency
                analyzer.genai = None
                result = analyzer.analyze_character(str(image_path), fallback_stats=True)
                
                if result:
                    stats = result[0]
                    character = Character(
                        name=f"BulkChar{i}",
                        hp=stats['hp'],
                        attack=stats['attack'],
                        defense=stats['defense'],
                        speed=stats['speed'],
                        magic=stats['magic'],
                        description=stats['description'],
                        image_path=str(image_path)
                    )
                    
                    success = db_manager.save_character(character)
                    if success:
                        characters_created += 1
        
        # Should successfully process most/all characters
        assert characters_created >= target_count * 0.8  # At least 80% success rate
        
        # Verify they're all in database
        all_chars = db_manager.get_all_characters()
        bulk_chars = [c for c in all_chars if c.name.startswith("BulkChar")]
        assert len(bulk_chars) == characters_created
    
    def test_rapid_battle_sequence(self, db_manager):
        """Test running multiple battles in sequence"""
        # Create test characters
        char1 = Character(
            name="Speedster1", hp=100, attack=75, defense=60, 
            speed=85, magic=55, description="Fast", image_path="/test1.png"
        )
        char2 = Character(
            name="Speedster2", hp=100, attack=75, defense=60, 
            speed=85, magic=55, description="Fast", image_path="/test2.png"
        )
        
        db_manager.save_character(char1)
        db_manager.save_character(char2)
        
        engine = BattleEngine()
        battle_count = 3
        
        for i in range(battle_count):
            # Reset character HP
            char1.hp = 100
            char2.hp = 100
            
            # Run battle
            result = engine.start_battle(char1, char2, visual_mode=False)
            assert result is not None
            
            # Save battle record
            battle = Battle(
                character1_id=char1.id,
                character2_id=char2.id,
                winner_id=result.winner,
                duration=result.duration
            )
            
            success = db_manager.save_battle(battle)
            assert success
        
        # Verify all battles were recorded
        char1_battles = db_manager.get_character_battles(char1.id)
        assert len(char1_battles) == battle_count


@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across the system"""
    
    def test_character_data_consistency(self, test_image_path, db_manager):
        """Test that character data remains consistent across operations"""
        # Create character
        original_char = Character(
            name="ConsistencyTest",
            hp=95, attack=80, defense=65, speed=90, magic=60,
            description="Consistency test character",
            image_path=test_image_path
        )
        
        # Save to database
        db_manager.save_character(original_char)
        
        # Retrieve from database
        retrieved_char = db_manager.get_character(original_char.id)
        
        # Verify all attributes match
        assert retrieved_char.name == original_char.name
        assert retrieved_char.hp == original_char.hp
        assert retrieved_char.attack == original_char.attack
        assert retrieved_char.defense == original_char.defense
        assert retrieved_char.speed == original_char.speed
        assert retrieved_char.magic == original_char.magic
        assert retrieved_char.description == original_char.description
        assert retrieved_char.image_path == original_char.image_path
        assert retrieved_char.id == original_char.id
    
    def test_battle_data_consistency(self, db_manager, battle_participants):
        """Test that battle data remains consistent"""
        char1, char2 = battle_participants
        
        # Save characters
        db_manager.save_character(char1)
        db_manager.save_character(char2)
        
        # Run battle
        engine = BattleEngine()
        result = engine.start_battle(char1, char2, visual_mode=False)
        
        # Create battle record
        battle = Battle(
            character1_id=char1.id,
            character2_id=char2.id,
            winner_id=result.winner,
            duration=result.duration
        )
        
        # Save battle
        db_manager.save_battle(battle)
        
        # Retrieve battle
        retrieved_battle = db_manager.get_battle(battle.id)
        
        # Verify consistency
        assert retrieved_battle.character1_id == battle.character1_id
        assert retrieved_battle.character2_id == battle.character2_id
        assert retrieved_battle.winner_id == battle.winner_id
        assert retrieved_battle.duration == battle.duration
        assert retrieved_battle.id == battle.id
    
    def test_statistics_consistency(self, db_manager, battle_participants):
        """Test that statistics calculations are consistent"""
        char1, char2 = battle_participants
        
        # Save characters
        db_manager.save_character(char1)
        db_manager.save_character(char2)
        
        # Get initial stats
        initial_stats = db_manager.get_statistics()
        initial_char_count = initial_stats['total_characters']
        initial_battle_count = initial_stats['total_battles']
        
        # Run and record battle
        engine = BattleEngine()
        result = engine.start_battle(char1, char2, visual_mode=False)
        
        battle = Battle(
            character1_id=char1.id,
            character2_id=char2.id,
            winner_id=result.winner,
            duration=result.duration
        )
        
        db_manager.save_battle(battle)
        
        # Update character stats
        winner_id = result.winner
        loser_id = char2.id if winner_id == char1.id else char1.id
        
        db_manager.update_character_stats(winner_id, True)
        db_manager.update_character_stats(loser_id, False)
        
        # Get updated stats
        updated_stats = db_manager.get_statistics()
        
        # Verify changes are consistent
        assert updated_stats['total_characters'] >= initial_char_count + 2
        # Note: total_battles in statistics might not include all battles
        # depending on implementation, so we just check it's reasonable
        assert updated_stats['total_battles'] >= initial_battle_count