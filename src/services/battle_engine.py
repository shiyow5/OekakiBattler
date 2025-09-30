"""
Battle engine service for automated character battles
"""

import random
import time
import logging
import pygame
import math
from pathlib import Path
from typing import Tuple, List, Optional
from src.models import Character, Battle, BattleTurn, BattleResult
from src.services.audio_manager import audio_manager
from src.services.battle_effects import BattleEffects, CharacterAnimator
from config.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BattleEngine:
    """Handle automated battles between characters"""
    
    def __init__(self):
        self.max_turns = Settings.MAX_TURNS
        self.critical_chance = Settings.CRITICAL_CHANCE
        self.critical_multiplier = Settings.CRITICAL_MULTIPLIER

        # Battle state
        self.current_battle = None
        self.battle_speed = 0.5  # Battle animation delay in seconds (lower = faster)

        # Pygame state - initialize only when needed
        self.pygame_initialized = False
        self.screen = None
        self.clock = None
        self.font = None
        self.small_font = None
        self.japanese_font_path = None  # Store the path to the Japanese font
        self.battle_sprites = {}

        # Effect systems
        self.effects = None
        self.animator = None
        
    def initialize_display(self) -> bool:
        """Initialize Pygame display for battle visualization"""
        try:
            # Clean up any existing display first
            if self.screen is not None:
                try:
                    pygame.display.quit()
                    self.screen = None
                except:
                    pass
            
            # Initialize Pygame if not already done
            if not pygame.get_init():
                pygame.init()
                self.pygame_initialized = True
                logger.info("Pygame initialized")
            
            # Initialize audio and load default sounds
            audio_manager.create_default_sounds()
            
            # Create new display
            self.screen = pygame.display.set_mode((Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT))
            logger.info("New battle display created")
            
            pygame.display.set_caption("お絵描きバトラー - Battle Arena")
            
            # Initialize clock if needed
            if self.clock is None:
                self.clock = pygame.time.Clock()
            
            # Load fonts with Japanese support
            if self.font is None:
                try:
                    # Try to load a Japanese font
                    japanese_fonts = [
                        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",  # Linux system font
                        "/usr/share/fonts/truetype/fonts-japanese-mincho.ttf",  # Linux system font
                        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",  # macOS
                        "/usr/share/fonts/truetype/noto-cjk/NotoSansCJK-Regular.ttc",  # Linux
                        "C:/Windows/Fonts/msgothic.ttc",  # Windows
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux fallback
                    ]

                    font_loaded = False
                    for font_path in japanese_fonts:
                        try:
                            if Path(font_path).exists():
                                self.font = pygame.font.Font(font_path, 28)
                                self.japanese_font_path = font_path  # Store the font path
                                font_loaded = True
                                logger.info(f"Loaded Japanese font: {font_path}")
                                break
                        except:
                            continue

                    if not font_loaded:
                        # Fallback to default font
                        self.font = pygame.font.Font(None, 36)
                        self.japanese_font_path = None
                        logger.warning("Could not load Japanese font, using default")

                except Exception as e:
                    logger.error(f"Error loading font: {e}")
                    self.font = pygame.font.Font(None, 36)
                    self.japanese_font_path = None
            
            if self.small_font is None:
                try:
                    # Use the same font path if available
                    if self.japanese_font_path:
                        self.small_font = pygame.font.Font(self.japanese_font_path, 18)
                    else:
                        # Try to load a Japanese font
                        japanese_fonts = [
                            "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
                            "/usr/share/fonts/truetype/fonts-japanese-mincho.ttf",
                            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                            "/usr/share/fonts/truetype/noto-cjk/NotoSansCJK-Regular.ttc",
                            "C:/Windows/Fonts/msgothic.ttc",
                            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                        ]

                        font_loaded = False
                        for font_path in japanese_fonts:
                            try:
                                if Path(font_path).exists():
                                    self.small_font = pygame.font.Font(font_path, 18)
                                    font_loaded = True
                                    break
                            except:
                                continue

                        if not font_loaded:
                            self.small_font = pygame.font.Font(None, 24)

                except Exception as e:
                    logger.error(f"Error loading small font: {e}")
                    self.small_font = pygame.font.Font(None, 24)

            # Initialize effect systems
            self.effects = BattleEffects(self.screen)
            self.animator = CharacterAnimator()

            logger.info("Battle display initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize battle display: {e}")
            return False
    
    def start_battle(self, char1: Character, char2: Character, visual_mode: bool = True) -> Battle:
        """Start a battle between two characters"""
        try:
            logger.info(f"Starting battle: {char1.name} vs {char2.name}")
            
            # Create new battle
            battle = Battle(
                character1_id=char1.id,
                character2_id=char2.id
            )
            self.current_battle = battle
            
            # Start battle BGM if visual mode
            if visual_mode:
                # Try to play battle BGM (will create a simple one if no file exists)
                self._start_battle_bgm()
            
            # Initialize character HP for battle
            char1_current_hp = char1.hp
            char2_current_hp = char2.hp
            
            # Add battle start log
            battle.add_log_entry(f"🥊 バトル開始！ {char1.name} VS {char2.name}")
            battle.add_log_entry(f"💚 {char1.name} HP: {char1_current_hp} / {char2.name} HP: {char2_current_hp}")
            
            # Initialize display if visual mode
            if visual_mode:
                if not self.initialize_display():
                    visual_mode = False
            
            # Battle loop
            start_time = time.time()
            turn_number = 1
            
            while turn_number <= self.max_turns:
                # Check if battle should end
                if char1_current_hp <= 0 or char2_current_hp <= 0:
                    break
                
                # Determine turn order
                turn_order = self.determine_turn_order(char1, char2)
                
                for attacker, defender in turn_order:
                    if attacker.id == char1.id:
                        attacker_hp, defender_hp = char1_current_hp, char2_current_hp
                    else:
                        attacker_hp, defender_hp = char2_current_hp, char1_current_hp
                    
                    # Skip turn if attacker is defeated
                    if attacker_hp <= 0:
                        continue
                    
                    # Execute turn
                    turn = self.execute_turn(attacker, defender, turn_number, attacker_hp, defender_hp)
                    battle.add_turn(turn)

                    # Add log entry
                    log_message = self._create_turn_log(attacker, defender, turn)
                    battle.add_log_entry(log_message)

                    # Visual update - animate BEFORE updating HP
                    if visual_mode and self.screen:
                        # Pass current HP (before damage) to animation
                        self._animate_turn(char1, char2, turn, char1_current_hp, char2_current_hp)

                    # Update HP AFTER animation
                    if attacker.id == char1.id:
                        char2_current_hp = turn.defender_hp_after
                    else:
                        char1_current_hp = turn.defender_hp_after

                    # Final display with updated HP
                    if visual_mode and self.screen:
                        self._update_battle_display(char1, char2, char1_current_hp, char2_current_hp, turn, battle.battle_log[-5:])
                        time.sleep(0.5 * self.battle_speed)
                    
                    # Check if battle should end
                    if char1_current_hp <= 0 or char2_current_hp <= 0:
                        break
                
                turn_number += 1
            
            # Determine winner
            if char1_current_hp > char2_current_hp:
                battle.winner_id = char1.id
                winner_name = char1.name
            elif char2_current_hp > char1_current_hp:
                battle.winner_id = char2.id
                winner_name = char2.name
            else:
                battle.winner_id = None
                winner_name = "Draw"
            
            # Calculate battle duration
            battle.duration = time.time() - start_time
            
            # Add final log
            if battle.winner_id:
                battle.add_log_entry(f"🎉 バトル終了！勝者: {winner_name}")
            else:
                battle.add_log_entry("⚖️ バトル終了！引き分け！")
            
            battle.add_log_entry(f"⏱️ バトル時間: {battle.duration:.2f}秒")
            battle.add_log_entry(f"🔄 総ターン数: {len(battle.turns)}")
            
            logger.info(f"Battle completed: Winner - {winner_name}")
            
            # Stop battle BGM and play victory sound
            if visual_mode:
                audio_manager.stop_bgm(fade_out=1000)  # 1 second fade out
                audio_manager.play_sound("victory")
            
            # Final display update
            if visual_mode and self.screen:
                self._show_battle_result(battle, char1, char2, char1_current_hp, char2_current_hp)
            
            # Clean up battle state
            self._cleanup_battle()
            
            return battle
            
        except Exception as e:
            logger.error(f"Error in battle execution: {e}")
            # Clean up on error
            self._cleanup_battle()
            
            if self.current_battle:
                self.current_battle.add_log_entry(f"Battle error: {e}")
                return self.current_battle
            else:
                # Return error battle
                error_battle = Battle(character1_id=char1.id, character2_id=char2.id)
                error_battle.add_log_entry(f"Battle failed: {e}")
                return error_battle
    
    def calculate_damage(self, attacker: Character, defender: Character, action_type: str = "attack") -> Tuple[int, bool, bool]:
        """Calculate damage, critical hit, and miss status"""
        try:
            is_critical = False
            is_miss = False
            base_damage = 0
            
            # Calculate hit chance based on speed difference
            speed_diff = attacker.speed - defender.speed
            hit_chance = max(0.8, min(0.95, 0.85 + speed_diff * 0.001))
            
            # Check for miss
            if random.random() > hit_chance:
                is_miss = True
                return 0, is_critical, is_miss
            
            # Calculate base damage
            if action_type == "magic":
                base_damage = attacker.magic + random.randint(-10, 10)
                # Magic ignores some defense
                effective_defense = max(0, defender.defense * 0.5)
            else:  # Physical attack
                base_damage = attacker.attack + random.randint(-15, 15)
                effective_defense = defender.defense
            
            # Apply defense
            damage = max(1, base_damage - effective_defense + random.randint(-5, 5))
            
            # Check for critical hit
            critical_chance = self.critical_chance
            if action_type == "magic":
                critical_chance *= 0.7  # Magic has lower critical chance
            
            if random.random() < critical_chance:
                is_critical = True
                damage = int(damage * self.critical_multiplier)
            
            return damage, is_critical, is_miss
            
        except Exception as e:
            logger.error(f"Error calculating damage: {e}")
            return 10, False, False  # Fallback damage
    
    def determine_turn_order(self, char1: Character, char2: Character) -> List[Tuple[Character, Character]]:
        """Determine who goes first based on speed"""
        try:
            # Add some randomness to speed to prevent predictable patterns
            char1_speed = char1.speed + random.randint(-5, 5)
            char2_speed = char2.speed + random.randint(-5, 5)
            
            if char1_speed >= char2_speed:
                return [(char1, char2), (char2, char1)]
            else:
                return [(char2, char1), (char1, char2)]
                
        except Exception as e:
            logger.error(f"Error determining turn order: {e}")
            return [(char1, char2), (char2, char1)]  # Default order
    
    def execute_turn(self, attacker: Character, defender: Character, turn_number: int, attacker_hp: int, defender_hp: int) -> BattleTurn:
        """Execute a single battle turn"""
        try:
            # Determine action type based on character stats and situation
            action_type = self._choose_action(attacker, defender, defender_hp)
            
            # Calculate damage
            damage, is_critical, is_miss = self.calculate_damage(attacker, defender, action_type)
            
            # Apply damage
            defender_hp_after = max(0, defender_hp - damage)
            
            # Create turn record
            turn = BattleTurn(
                turn_number=turn_number,
                attacker_id=attacker.id,
                defender_id=defender.id,
                action_type=action_type,
                damage=damage,
                is_critical=is_critical,
                is_miss=is_miss,
                attacker_hp_after=attacker_hp,
                defender_hp_after=defender_hp_after
            )
            
            return turn
            
        except Exception as e:
            logger.error(f"Error executing turn: {e}")
            # Return safe default turn
            return BattleTurn(
                turn_number=turn_number,
                attacker_id=attacker.id,
                defender_id=defender.id,
                action_type="attack",
                damage=0,
                is_critical=False,
                is_miss=True,
                attacker_hp_after=attacker_hp,
                defender_hp_after=defender_hp
            )
    
    def _choose_action(self, attacker: Character, defender: Character, defender_hp: int) -> str:
        """Choose action type based on character stats and battle situation"""
        try:
            # Calculate probabilities based on stats
            magic_prob = min(0.4, attacker.magic / 200)  # Higher magic = more likely to use magic
            
            # Increase magic usage if defender has high defense
            if defender.defense > 70:
                magic_prob += 0.2
            
            # Increase magic usage if defender is low on HP (finishing move)
            if defender_hp < defender.hp * 0.3:
                magic_prob += 0.15
            
            # Choose action
            if random.random() < magic_prob:
                return "magic"
            else:
                return "attack"
                
        except Exception as e:
            logger.error(f"Error choosing action: {e}")
            return "attack"
    
    def _create_turn_log(self, attacker: Character, defender: Character, turn: BattleTurn) -> str:
        """Create descriptive log message for a turn"""
        try:
            if turn.is_miss:
                return f"💨 {attacker.name}の攻撃は外れた！"
            
            if turn.action_type == "magic":
                if turn.is_critical:
                    return f"✨💥 {attacker.name}のクリティカル魔法攻撃！{defender.name}に{turn.damage}ダメージ！"
                else:
                    return f"🔮 {attacker.name}の魔法攻撃！{defender.name}に{turn.damage}ダメージ"
            else:
                if turn.is_critical:
                    return f"⚔️💥 {attacker.name}のクリティカル攻撃！{defender.name}に{turn.damage}ダメージ！"
                else:
                    return f"⚔️ {attacker.name}の攻撃！{defender.name}に{turn.damage}ダメージ"
                
        except Exception as e:
            logger.error(f"Error creating turn log: {e}")
            return f"{attacker.name} attacks {defender.name}"
    
    def _animate_turn(self, char1: Character, char2: Character, turn: BattleTurn, char1_hp: int, char2_hp: int):
        """Animate a battle turn with smooth effects
        Note: char1_hp and char2_hp are the HP values BEFORE damage
        """
        if not self.screen or not self.effects or not self.animator:
            return

        try:
            # Get recent battle logs
            recent_logs = self.current_battle.battle_log[-5:] if self.current_battle else []

            # Determine attacker and defender
            if turn.attacker_id == char1.id:
                attacker, defender = char1, char2
                attacker_pos = (200, 300)
                defender_pos = (Settings.SCREEN_WIDTH - 200, 300)
                # Defender is char2
                defender_hp_before = char2_hp
                defender_hp_after = turn.defender_hp_after
            else:
                attacker, defender = char2, char1
                attacker_pos = (Settings.SCREEN_WIDTH - 200, 300)
                defender_pos = (200, 300)
                # Defender is char1
                defender_hp_before = char1_hp
                defender_hp_after = turn.defender_hp_after

            # Calculate frame counts based on battle_speed
            # battle_speed: 0.01 (fastest) to 3.0 (slowest), default 0.5
            # Higher battle_speed = more frames = slower animation
            speed_multiplier = self.battle_speed * 2  # Convert to reasonable multiplier (0.02 to 6.0)

            bounce_frames = int(50 * speed_multiplier)
            charge_frames = int(30 * speed_multiplier)
            windup_frames = int(15 * speed_multiplier)
            recovery_frames = int(50 * speed_multiplier)
            miss_frames = int(30 * speed_multiplier)
            shake_frames = int(20 * speed_multiplier)

            # Phase 1: Pre-attack animation (jump/charge) - no damage display yet
            bounce_duration = bounce_frames
            self.animator.start_animation(attacker.id, 'bounce', bounce_duration, bounces=3, height=20)

            for _ in range(bounce_frames):
                self._render_battle_frame(char1, char2, char1_hp, char2_hp, None, recent_logs)
                self.clock.tick(60)

            # Phase 2: Attack animation
            if not turn.is_miss:
                # Create attack direction
                direction = (
                    defender_pos[0] - attacker_pos[0],
                    defender_pos[1] - attacker_pos[1]
                )
                length = math.sqrt(direction[0]**2 + direction[1]**2)
                if length > 0:
                    direction = (direction[0]/length, direction[1]/length)

                if turn.action_type == "magic":
                    # Magic attack animation - charge phase (no damage display yet)
                    self.effects.create_charge_effect(attacker_pos[0], attacker_pos[1], 25)
                    for _ in range(charge_frames):
                        self._render_battle_frame(char1, char2, char1_hp, char2_hp, None, recent_logs)
                        self.clock.tick(60)

                    # Play sound immediately when charge completes
                    if turn.is_critical:
                        audio_manager.play_sound("magic", 1.2)
                        audio_manager.play_sound("critical")
                    else:
                        audio_manager.play_sound("magic", 1.0)

                    # Impact phase - now show damage
                    self.effects.create_magic_particles(defender_pos[0], defender_pos[1], 50)
                    if turn.is_critical:
                        self.effects.screen_shake(20, 12)
                        self.effects.create_explosion(defender_pos[0], defender_pos[1], 60, (200, 100, 255))
                    else:
                        self.effects.screen_shake(10, 10)

                else:
                    # Physical attack animation - brief windup before impact
                    for _ in range(windup_frames):
                        self._render_battle_frame(char1, char2, char1_hp, char2_hp, None, recent_logs)
                        self.clock.tick(60)

                    # Play sound immediately at impact moment
                    if turn.is_critical:
                        audio_manager.play_sound("critical")
                    else:
                        audio_manager.play_sound("attack")

                    # Now create impact effects and show damage
                    self.effects.create_slash_trail(attacker_pos, defender_pos)
                    self.effects.create_impact_particles(
                        defender_pos[0], defender_pos[1],
                        direction, 25
                    )

                    if turn.is_critical:
                        self.effects.screen_shake(18, 12)
                        self.effects.create_explosion(defender_pos[0], defender_pos[1], 50, (255, 200, 0))
                    else:
                        self.effects.screen_shake(8, 8)

                # Defender reaction animation
                self.animator.start_animation(defender.id, 'shake', shake_frames, intensity=8)

            else:
                # Miss animation
                self.animator.start_animation(defender.id, 'jump', miss_frames, height=25)
                audio_manager.play_sound("miss")

            # Phase 3: Impact and recovery - gradually reduce HP
            for i in range(recovery_frames):
                # Calculate HP reduction progress (0.0 to 1.0)
                progress = (i + 1) / recovery_frames

                # Interpolate HP from before to after
                if turn.attacker_id == char1.id:
                    # char2 is defender
                    current_char2_hp = int(defender_hp_before - (defender_hp_before - defender_hp_after) * progress)
                    self._render_battle_frame(char1, char2, char1_hp, current_char2_hp, turn, recent_logs)
                else:
                    # char1 is defender
                    current_char1_hp = int(defender_hp_before - (defender_hp_before - defender_hp_after) * progress)
                    self._render_battle_frame(char1, char2, current_char1_hp, char2_hp, turn, recent_logs)

                self.clock.tick(60)

        except Exception as e:
            logger.error(f"Error animating turn: {e}")

    def _render_battle_frame(self, char1: Character, char2: Character, char1_hp: int, char2_hp: int, current_turn: Optional[BattleTurn], recent_logs: List[str]):
        """Render a single battle frame with all effects"""
        if not self.screen:
            return

        try:
            # Update effect systems
            if self.effects:
                self.effects.update(1.0)
            if self.animator:
                self.animator.update(1.0)

            # Clear screen with shake offset
            shake_offset = self.effects.screen_offset if self.effects else [0, 0]
            self.screen.fill((240, 248, 255))

            # Draw battle arena
            arena_rect = pygame.Rect(
                50 + shake_offset[0],
                100 + shake_offset[1],
                Settings.SCREEN_WIDTH - 100,
                400
            )
            pygame.draw.rect(self.screen, (200, 220, 200), arena_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), arena_rect, 3)

            # Character positions with animation offsets
            char1_base_pos = (200, 300)
            char2_base_pos = (Settings.SCREEN_WIDTH - 200, 300)

            char1_offset = self.animator.get_offset(char1.id) if self.animator else (0, 0)
            char2_offset = self.animator.get_offset(char2.id) if self.animator else (0, 0)

            char1_pos = (
                char1_base_pos[0] + int(char1_offset[0]) + shake_offset[0],
                char1_base_pos[1] + int(char1_offset[1]) + shake_offset[1]
            )
            char2_pos = (
                char2_base_pos[0] + int(char2_offset[0]) + shake_offset[0],
                char2_base_pos[1] + int(char2_offset[1]) + shake_offset[1]
            )

            # Draw characters
            self._draw_character(char1, char1_pos, char1_hp)
            self._draw_character(char2, char2_pos, char2_hp)

            # Draw HP bars
            self._draw_hp_bars(char1, char2, char1_pos, char2_pos, char1_hp, char2_hp, shake_offset)

            # Draw character names
            name1_surface = self.font.render(char1.name, True, (0, 0, 0))
            name2_surface = self.font.render(char2.name, True, (0, 0, 0))
            self.screen.blit(name1_surface, (char1_pos[0] - 40, char1_pos[1] + 70))
            self.screen.blit(name2_surface, (char2_pos[0] - 40, char2_pos[1] + 70))

            # Draw effects
            if self.effects:
                self.effects.draw()

            # Draw damage text
            if current_turn and not current_turn.is_miss and current_turn.damage > 0:
                defender_pos = char2_pos if current_turn.attacker_id == char1.id else char1_pos
                self._draw_damage_text(current_turn, defender_pos)

            # Draw recent battle log
            if recent_logs:
                log_start_y = 520
                for i, log_entry in enumerate(recent_logs):
                    log_surface = self.small_font.render(log_entry, True, (0, 0, 0))
                    self.screen.blit(log_surface, (50, log_start_y + i * 25))

            # Update display
            pygame.display.flip()

        except Exception as e:
            logger.error(f"Error rendering battle frame: {e}")

    def _draw_hp_bars(self, char1: Character, char2: Character, char1_pos: Tuple[int, int], char2_pos: Tuple[int, int], char1_hp: int, char2_hp: int, shake_offset: List[int]):
        """Draw HP bars for both characters"""
        try:
            hp_bar_width = 100
            hp_bar_height = 20

            # Calculate HP ratios
            char1_hp_ratio = max(0, char1_hp / char1.hp)
            char2_hp_ratio = max(0, char2_hp / char2.hp)

            # Character 1 HP bar
            hp1_bar_rect = pygame.Rect(char1_pos[0] - 50, char1_pos[1] - 80, hp_bar_width, hp_bar_height)
            hp1_fill_width = int(hp_bar_width * char1_hp_ratio)
            hp1_fill_rect = pygame.Rect(char1_pos[0] - 50, char1_pos[1] - 80, hp1_fill_width, hp_bar_height)

            pygame.draw.rect(self.screen, (255, 255, 255), hp1_bar_rect)
            pygame.draw.rect(self.screen, (0, 255, 0), hp1_fill_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), hp1_bar_rect, 2)

            # Character 2 HP bar
            hp2_bar_rect = pygame.Rect(char2_pos[0] - 50, char2_pos[1] - 80, hp_bar_width, hp_bar_height)
            hp2_fill_width = int(hp_bar_width * char2_hp_ratio)
            hp2_fill_rect = pygame.Rect(char2_pos[0] - 50, char2_pos[1] - 80, hp2_fill_width, hp_bar_height)

            pygame.draw.rect(self.screen, (255, 255, 255), hp2_bar_rect)
            pygame.draw.rect(self.screen, (0, 255, 0), hp2_fill_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), hp2_bar_rect, 2)

            # Draw HP text
            hp1_text = f"HP: {char1_hp}/{char1.hp}"
            hp2_text = f"HP: {char2_hp}/{char2.hp}"
            hp1_surface = self.small_font.render(hp1_text, True, (0, 0, 0))
            hp2_surface = self.small_font.render(hp2_text, True, (0, 0, 0))
            self.screen.blit(hp1_surface, (char1_pos[0] - 50, char1_pos[1] - 100))
            self.screen.blit(hp2_surface, (char2_pos[0] - 50, char2_pos[1] - 100))

        except Exception as e:
            logger.error(f"Error drawing HP bars: {e}")

    def _update_battle_display(self, char1: Character, char2: Character, char1_hp: int, char2_hp: int, current_turn: BattleTurn, recent_logs: List[str]):
        """Update the battle visualization"""
        if not self.screen:
            return

        try:
            # Process pygame events to keep window responsive
            should_quit = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    should_quit = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_quit = True
            
            # If user wants to quit, return early to end battle
            if should_quit:
                return

            # Just render one final frame with logs
            self._render_battle_frame(char1, char2, char1_hp, char2_hp, current_turn, recent_logs)
            
        except Exception as e:
            logger.error(f"Error updating battle display: {e}")
    
    def _draw_damage_text(self, turn: BattleTurn, position: Tuple[int, int]):
        """Draw animated damage text"""
        try:
            # Determine text color and style
            if turn.is_critical:
                damage_color = (255, 255, 50)  # Bright yellow for critical
                font_size = 72
                damage_text = f"{turn.damage}!!"
            else:
                damage_color = (255, 80, 80)  # Red for normal
                font_size = 52
                damage_text = str(turn.damage)

            # Create font for damage text
            damage_font = self._create_font(font_size)

            damage_surface = damage_font.render(damage_text, True, damage_color)

            # Add floating animation with larger movement
            float_offset = int(25 * math.sin(pygame.time.get_ticks() * 0.008))
            text_pos = (position[0] - damage_surface.get_width() // 2,
                       position[1] - 180 - float_offset)

            # Draw text with thicker outline for better visibility
            try:
                outline_surface = damage_font.render(damage_text, True, (0, 0, 0))
                for dx in [-3, -1, 0, 1, 3]:
                    for dy in [-3, -1, 0, 1, 3]:
                        if dx != 0 or dy != 0:
                            self.screen.blit(outline_surface, (text_pos[0] + dx, text_pos[1] + dy))
            except:
                pass  # Skip outline if it fails

            self.screen.blit(damage_surface, text_pos)

        except Exception as e:
            logger.error(f"Error drawing damage text: {e}")
    
    def _start_battle_bgm(self):
        """Start battle background music"""
        try:
            # Try to load and play battle BGM file
            if audio_manager.load_bgm("battle.mp3") or audio_manager.load_bgm("battle.ogg") or audio_manager.load_bgm("battle.wav"):
                audio_manager.play_bgm(loops=-1, fade_in=1000)
                logger.debug("Started battle BGM from file")
            else:
                logger.debug("No battle BGM file found, continuing without background music")
        except Exception as e:
            logger.warning(f"Failed to start battle BGM: {e}")
    
    def _draw_character(self, character: Character, position: Tuple[int, int], current_hp: int):
        """Draw character with image or fallback to colored rectangle"""
        try:
            max_width, max_height = 120, 120  # Maximum display size

            # Try to load and display character image
            character_sprite = self._load_character_sprite(character)

            if character_sprite:
                # Scale image while preserving aspect ratio
                original_width, original_height = character_sprite.get_size()
                scale_x = max_width / original_width
                scale_y = max_height / original_height
                scale = min(scale_x, scale_y)  # Use smaller scale to fit within bounds

                new_width = int(original_width * scale)
                new_height = int(original_height * scale)

                scaled_sprite = pygame.transform.scale(character_sprite, (new_width, new_height))

                # Calculate position to center the image
                char_x = position[0] - new_width // 2
                char_y = position[1] - new_height // 2

                # Apply HP-based effects
                hp_ratio = max(0, current_hp / character.hp)

                if hp_ratio < 0.5:  # Apply red tint when HP is low
                    # Create a red overlay with simpler blending
                    red_overlay = pygame.Surface((new_width, new_height))
                    alpha = int(60 * (1 - hp_ratio * 2))  # More red as HP decreases
                    red_overlay.set_alpha(alpha)
                    red_overlay.fill((255, 80, 80))  # Red damage indicator
                    scaled_sprite.blit(red_overlay, (0, 0))

                # Draw the character image
                self.screen.blit(scaled_sprite, (char_x, char_y))
            else:
                # Fallback to colored rectangle
                char_width, char_height = 80, 120
                char_x = position[0] - char_width // 2
                char_y = position[1] - char_height // 2
                char_rect = pygame.Rect(char_x, char_y, char_width, char_height)
                hp_ratio = max(0, current_hp / character.hp)
                char_color = (int(255 * (1 - hp_ratio)), int(255 * hp_ratio), 0)

                pygame.draw.rect(self.screen, char_color, char_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), char_rect, 2)

        except Exception as e:
            logger.error(f"Error drawing character {character.name}: {e}")
            # Emergency fallback - draw simple rectangle
            char_rect = pygame.Rect(position[0] - 40, position[1] - 60, 80, 120)
            pygame.draw.rect(self.screen, (128, 128, 128), char_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), char_rect, 2)
    
    def _load_character_sprite(self, character: Character) -> Optional[pygame.Surface]:
        """Load character sprite with caching"""
        try:
            # Check cache first
            if character.id in self.battle_sprites:
                return self.battle_sprites[character.id]
            
            # Check if display is initialized
            if not pygame.get_init() or not self.screen:
                logger.warning(f"Pygame display not initialized, cannot load sprite for {character.name}")
                return None
            
            # Try to load sprite image (background removed) first, fallback to original image
            image_path = character.sprite_path or character.image_path
            if image_path:
                # If it's a relative path, make it relative to the project root
                if not Path(image_path).is_absolute():
                    image_path = str(Path.cwd() / image_path)
                
                if Path(image_path).exists():
                    try:
                        sprite = pygame.image.load(image_path)
                        # Convert for better performance (only after display is initialized)
                        sprite = sprite.convert_alpha()
                        # Cache the sprite
                        self.battle_sprites[character.id] = sprite
                        sprite_type = "sprite" if character.sprite_path else "original image"
                        logger.debug(f"Loaded {sprite_type} for character {character.name} from {image_path}")
                        return sprite
                    except pygame.error as e:
                        logger.warning(f"Failed to load image {image_path}: {e}")
                else:
                    logger.warning(f"Image file not found for character {character.name}: {image_path}")
            else:
                logger.warning(f"No sprite or image path specified for character {character.name}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading character sprite: {e}")
            return None

    def _create_font(self, size: int) -> pygame.font.Font:
        """Create a font with Japanese support at the specified size"""
        try:
            if self.japanese_font_path:
                return pygame.font.Font(self.japanese_font_path, size)
            else:
                # Fallback to default font if no Japanese font available
                return pygame.font.Font(None, size)
        except Exception as e:
            logger.warning(f"Failed to create font with size {size}: {e}")
            return self.font  # Return the default font as fallback

    def _show_battle_result(self, battle: Battle, char1: Character, char2: Character, char1_hp: int, char2_hp: int):
        """Show final battle result screen"""
        if not self.screen:
            return

        try:
            # Clear any pending events first
            pygame.event.clear()

            # Draw gradient background overlay
            for y in range(Settings.SCREEN_HEIGHT):
                alpha = int(230 * (y / Settings.SCREEN_HEIGHT))
                line_surface = pygame.Surface((Settings.SCREEN_WIDTH, 1))
                line_surface.set_alpha(alpha)
                line_surface.fill((20, 20, 40))
                self.screen.blit(line_surface, (0, y))

            # Determine winner and colors
            if battle.winner_id == char1.id:
                winner = char1
                loser = char2
                winner_name = char1.name
                winner_color = (255, 215, 0)  # Gold
                winner_bg_color = (80, 60, 0)  # Dark gold
            elif battle.winner_id == char2.id:
                winner = char2
                loser = char1
                winner_name = char2.name
                winner_color = (255, 215, 0)  # Gold
                winner_bg_color = (80, 60, 0)  # Dark gold
            else:
                winner = None
                loser = None
                winner_name = "引き分け"
                winner_color = (200, 200, 200)  # Silver
                winner_bg_color = (60, 60, 60)  # Dark gray

            # Draw large "VICTORY" or "DRAW" text at top
            victory_font = self._create_font(120)

            if winner:
                victory_text = "VICTORY!"
                victory_surface = victory_font.render(victory_text, True, winner_color)
            else:
                victory_text = "DRAW!"
                victory_surface = victory_font.render(victory_text, True, winner_color)

            # Draw with glow effect
            for offset in [(0, 0), (-3, -3), (3, 3), (-3, 3), (3, -3)]:
                glow_surface = victory_font.render(victory_text, True, winner_bg_color)
                glow_rect = glow_surface.get_rect(center=(Settings.SCREEN_WIDTH // 2 + offset[0], 80 + offset[1]))
                self.screen.blit(glow_surface, glow_rect)

            victory_rect = victory_surface.get_rect(center=(Settings.SCREEN_WIDTH // 2, 80))
            self.screen.blit(victory_surface, victory_rect)

            # Draw character images side by side
            char_display_size = 200

            # Winner character (left side, larger)
            if winner:
                winner_sprite = self._load_character_sprite(winner)
                if winner_sprite:
                    # Scale to fit
                    original_w, original_h = winner_sprite.get_size()
                    scale = min(char_display_size / original_w, char_display_size / original_h)
                    new_w, new_h = int(original_w * scale * 1.3), int(original_h * scale * 1.3)  # 30% larger for winner
                    scaled_winner = pygame.transform.scale(winner_sprite, (new_w, new_h))

                    # Draw winner with golden border
                    winner_pos = (Settings.SCREEN_WIDTH // 2 - 250, Settings.SCREEN_HEIGHT // 2 - 50)
                    border_rect = pygame.Rect(winner_pos[0] - 10, winner_pos[1] - 10, new_w + 20, new_h + 20)
                    pygame.draw.rect(self.screen, winner_color, border_rect, 8)
                    pygame.draw.rect(self.screen, winner_bg_color, border_rect, 4)
                    self.screen.blit(scaled_winner, winner_pos)

                    # Draw crown symbol above winner (using simple shapes instead of emoji)
                    crown_center_x = winner_pos[0] + new_w // 2
                    crown_center_y = winner_pos[1] - 40

                    # Draw crown shape with triangles
                    crown_points = [
                        (crown_center_x, crown_center_y - 15),  # Top point
                        (crown_center_x - 20, crown_center_y),   # Left point
                        (crown_center_x - 15, crown_center_y + 10), # Left base
                        (crown_center_x + 15, crown_center_y + 10), # Right base
                        (crown_center_x + 20, crown_center_y),   # Right point
                    ]
                    pygame.draw.polygon(self.screen, winner_color, crown_points)
                    pygame.draw.polygon(self.screen, winner_bg_color, crown_points, 3)

                    # Crown jewels (circles)
                    pygame.draw.circle(self.screen, (255, 50, 50), (crown_center_x, crown_center_y - 10), 5)
                    pygame.draw.circle(self.screen, (50, 255, 50), (crown_center_x - 15, crown_center_y), 4)
                    pygame.draw.circle(self.screen, (50, 50, 255), (crown_center_x + 15, crown_center_y), 4)

                # Loser character (right side, smaller, dimmed)
                if loser:
                    loser_sprite = self._load_character_sprite(loser)
                    if loser_sprite:
                        original_w, original_h = loser_sprite.get_size()
                        scale = min(char_display_size / original_w, char_display_size / original_h)
                        new_w, new_h = int(original_w * scale * 0.8), int(original_h * scale * 0.8)  # 20% smaller for loser
                        scaled_loser = pygame.transform.scale(loser_sprite, (new_w, new_h))

                        # Apply gray overlay
                        gray_overlay = pygame.Surface((new_w, new_h))
                        gray_overlay.set_alpha(120)
                        gray_overlay.fill((80, 80, 80))
                        scaled_loser.blit(gray_overlay, (0, 0))

                        # Draw loser with gray border
                        loser_pos = (Settings.SCREEN_WIDTH // 2 + 100, Settings.SCREEN_HEIGHT // 2 - 20)
                        border_rect = pygame.Rect(loser_pos[0] - 5, loser_pos[1] - 5, new_w + 10, new_h + 10)
                        pygame.draw.rect(self.screen, (100, 100, 100), border_rect, 4)
                        self.screen.blit(scaled_loser, loser_pos)

            # Draw winner name with large font
            name_font = self._create_font(72)

            winner_name_surface = name_font.render(winner_name, True, winner_color)
            # Draw with outline
            for dx in [-3, 0, 3]:
                for dy in [-3, 0, 3]:
                    if dx != 0 or dy != 0:
                        outline_surface = name_font.render(winner_name, True, (0, 0, 0))
                        outline_rect = outline_surface.get_rect(center=(Settings.SCREEN_WIDTH // 2 + dx, 180 + dy))
                        self.screen.blit(outline_surface, outline_rect)

            name_rect = winner_name_surface.get_rect(center=(Settings.SCREEN_WIDTH // 2, 180))
            self.screen.blit(winner_name_surface, name_rect)

            # Draw battle stats with better formatting
            stats_y = Settings.SCREEN_HEIGHT - 220

            # Stats background panel
            stats_panel = pygame.Rect(Settings.SCREEN_WIDTH // 2 - 300, stats_y - 20, 600, 140)
            panel_surface = pygame.Surface((600, 140))
            panel_surface.set_alpha(180)
            panel_surface.fill((40, 40, 60))
            self.screen.blit(panel_surface, (Settings.SCREEN_WIDTH // 2 - 300, stats_y - 20))
            pygame.draw.rect(self.screen, winner_color, stats_panel, 3)

            stats_font = self._create_font(32)

            # Draw stats with custom icons (no emojis)
            stats_data = [
                ("TIME", f"バトル時間: {battle.duration:.2f}秒", (100, 200, 255)),
                ("TURN", f"総ターン数: {len(battle.turns)}", (255, 200, 100)),
                ("HP1", f"{char1.name}: {char1_hp} HP", (255, 100, 100)),
                ("HP2", f"{char2.name}: {char2_hp} HP", (255, 100, 100))
            ]

            for i, (icon_type, stat_text, icon_color) in enumerate(stats_data):
                stat_y = stats_y + 10 + i * 30

                # Draw icon on the left
                icon_x = Settings.SCREEN_WIDTH // 2 - 250
                if icon_type == "TIME":
                    # Clock icon
                    pygame.draw.circle(self.screen, icon_color, (icon_x, stat_y + 8), 12, 2)
                    pygame.draw.line(self.screen, icon_color, (icon_x, stat_y + 8), (icon_x, stat_y + 2), 2)
                    pygame.draw.line(self.screen, icon_color, (icon_x, stat_y + 8), (icon_x + 6, stat_y + 8), 2)
                elif icon_type == "TURN":
                    # Circular arrow icon
                    pygame.draw.circle(self.screen, icon_color, (icon_x, stat_y + 8), 10, 2)
                    pygame.draw.polygon(self.screen, icon_color, [
                        (icon_x + 8, stat_y + 8),
                        (icon_x + 12, stat_y + 4),
                        (icon_x + 12, stat_y + 12)
                    ])
                elif icon_type.startswith("HP"):
                    # Heart icon
                    pygame.draw.circle(self.screen, icon_color, (icon_x - 4, stat_y + 4), 6)
                    pygame.draw.circle(self.screen, icon_color, (icon_x + 4, stat_y + 4), 6)
                    pygame.draw.polygon(self.screen, icon_color, [
                        (icon_x - 10, stat_y + 4),
                        (icon_x, stat_y + 14),
                        (icon_x + 10, stat_y + 4)
                    ])

                # Draw stat text
                stat_surface = stats_font.render(stat_text, True, (255, 255, 200))
                stat_rect = stat_surface.get_rect(left=icon_x + 25, centery=stat_y + 8)
                self.screen.blit(stat_surface, stat_rect)
            
            # Draw OK button with improved styling
            button_width = 200
            button_height = 60
            button_x = Settings.SCREEN_WIDTH // 2 - button_width // 2
            button_y = Settings.SCREEN_HEIGHT - 80
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            # Button with gradient effect
            pygame.draw.rect(self.screen, (100, 180, 100), button_rect)
            pygame.draw.rect(self.screen, (150, 255, 150), button_rect, 4)

            # Button text
            button_font = self._create_font(48)

            button_text = button_font.render("OK", True, (255, 255, 255))
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)

            # Draw instruction text
            instruction_text = "クリックまたはスペースキーで閉じる"
            instruction_font = self._create_font(24)

            instruction_surface = instruction_font.render(instruction_text, True, (180, 180, 200))
            instruction_rect = instruction_surface.get_rect(center=(Settings.SCREEN_WIDTH // 2, button_y - 20))
            self.screen.blit(instruction_surface, instruction_rect)
            
            pygame.display.flip()
            
            # Wait for user input
            waiting = True
            clock = pygame.time.Clock()
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        self._force_close_window()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                            waiting = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if button_rect.collidepoint(mouse_pos):
                            # OK button clicked
                            waiting = False
                        else:
                            # Clicked anywhere else - also close
                            waiting = False
                            
                clock.tick(30)  # Limit to 30 FPS while waiting
            
        except Exception as e:
            logger.error(f"Error showing battle result: {e}")
        finally:
            # Ensure window gets closed
            self._close_battle_window()
    
    def get_battle_result(self, battle: Battle, char1: Character, char2: Character) -> BattleResult:
        """Generate comprehensive battle result summary"""
        try:
            result = BattleResult(
                winner=battle.winner_id,
                total_turns=len(battle.turns),
                duration=battle.duration
            )
            
            # Calculate statistics
            char1_damage = 0
            char2_damage = 0
            char1_criticals = 0
            char2_criticals = 0
            char1_magic = 0
            char2_magic = 0
            
            for turn in battle.turns:
                if turn.attacker_id == char1.id:
                    char1_damage += turn.damage
                    if turn.is_critical:
                        char1_criticals += 1
                    if turn.action_type == "magic":
                        char1_magic += 1
                else:
                    char2_damage += turn.damage
                    if turn.is_critical:
                        char2_criticals += 1
                    if turn.action_type == "magic":
                        char2_magic += 1
            
            result.damage_dealt = {char1.id: char1_damage, char2.id: char2_damage}
            result.critical_hits = {char1.id: char1_criticals, char2.id: char2_criticals}
            result.magic_used = {char1.id: char1_magic, char2.id: char2_magic}
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating battle result: {e}")
            return BattleResult(
                winner=battle.winner_id,
                total_turns=len(battle.turns),
                duration=battle.duration
            )
    
    def _cleanup_battle(self):
        """Clean up battle state after each battle"""
        try:
            # Reset battle state
            self.current_battle = None

            # Clear sprite cache to free memory
            self.battle_sprites.clear()

            # Clear effect systems
            if self.effects:
                self.effects.clear()
            if self.animator:
                self.animator.clear()

            # Close the battle window properly
            self._close_battle_window()

            logger.debug("Battle state cleaned up")
        except Exception as e:
            logger.error(f"Error during battle cleanup: {e}")
    
    def _close_battle_window(self):
        """Close the battle window properly"""
        try:
            if self.screen:
                # Fill screen with black and update to visually indicate closure
                self.screen.fill((0, 0, 0))
                pygame.display.flip()
                
                # Close the display
                pygame.display.quit()
                self.screen = None
                
            logger.debug("Battle window closed")
        except Exception as e:
            logger.error(f"Error closing battle window: {e}")
    
    def _force_close_window(self):
        """Force close the battle window immediately"""
        try:
            if pygame.get_init():
                pygame.display.quit()
                self.screen = None
            logger.debug("Battle window force closed")
        except Exception as e:
            logger.error(f"Error force closing window: {e}")
    
    def cleanup(self):
        """Clean up pygame resources"""
        try:
            # Stop any playing audio
            audio_manager.stop_bgm()
            audio_manager.cleanup()
            
            if pygame.get_init():
                pygame.quit()
                self.pygame_initialized = False
                self.screen = None
                self.clock = None
                self.font = None
                self.small_font = None
            logger.info("Battle engine cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")