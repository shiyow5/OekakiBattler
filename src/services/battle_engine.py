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
        self.background_image = None  # Battle arena background image

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
            # Note: pygame.init() should be called on main thread (done in main.py for macOS 15+)
            if not pygame.get_init():
                logger.warning("Pygame not initialized on main thread - attempting initialization")
                pygame.init()
                self.pygame_initialized = True
                logger.info("Pygame initialized (fallback)")
            
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

            # Load background image
            self._load_background_image()

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
                else:
                    # Show battle start screen with countdown
                    self._show_battle_start_screen(char1, char2)
            
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
            
            # Calculate battle statistics
            battle.char1_final_hp = char1_current_hp
            battle.char2_final_hp = char2_current_hp

            # Calculate total damage dealt by each character
            for turn in battle.turns:
                if turn.attacker_id == char1.id:
                    battle.char1_damage_dealt += turn.damage
                elif turn.attacker_id == char2.id:
                    battle.char2_damage_dealt += turn.damage

            # Determine winner and result type
            if char1_current_hp <= 0 or char2_current_hp <= 0:
                battle.result_type = "KO"
            elif turn_number > self.max_turns:
                battle.result_type = "Time Limit"
            else:
                battle.result_type = "Draw"

            if char1_current_hp > char2_current_hp:
                battle.winner_id = char1.id
                winner_name = char1.name
            elif char2_current_hp > char1_current_hp:
                battle.winner_id = char2.id
                winner_name = char2.name
            else:
                battle.winner_id = None
                winner_name = "Draw"
                battle.result_type = "Draw"

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
            # Get screen size and calculate scale
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            scale_x = screen_width / 1024
            scale_y = screen_height / 768

            # Get recent battle logs
            recent_logs = self.current_battle.battle_log[-5:] if self.current_battle else []

            # Determine attacker and defender with scaled positions
            if turn.attacker_id == char1.id:
                attacker, defender = char1, char2
                attacker_pos = (int(250 * scale_x), int(350 * scale_y))
                defender_pos = (int((screen_width - 250 * scale_x)), int(350 * scale_y))
                # Defender is char2
                defender_hp_before = char2_hp
                defender_hp_after = turn.defender_hp_after
            else:
                attacker, defender = char2, char1
                attacker_pos = (int((screen_width - 250 * scale_x)), int(350 * scale_y))
                defender_pos = (int(250 * scale_x), int(350 * scale_y))
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
            # Get actual screen size and calculate scale
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            scale_x = screen_width / 1024
            scale_y = screen_height / 768
            scale = min(scale_x, scale_y)

            # Update effect systems
            if self.effects:
                self.effects.update(1.0)
            if self.animator:
                self.animator.update(1.0)

            # Clear screen with shake offset
            shake_offset = self.effects.screen_offset if self.effects else [0, 0]

            # Draw background image or solid color
            if self.background_image:
                # Scale background image to screen size
                screen_bg = pygame.transform.scale(self.background_image, (screen_width, screen_height))
                self.screen.blit(screen_bg, (shake_offset[0], shake_offset[1]))
            else:
                # Fallback to solid color background
                self.screen.fill((240, 248, 255))

            # Draw battle arena (taller) - white background
            arena_x = int(50 * scale_x) + shake_offset[0]
            arena_y = int(50 * scale_y) + shake_offset[1]
            arena_width = screen_width - int(100 * scale_x)
            arena_height = int(550 * scale_y)  # Increased from 400 to 550
            arena_rect = pygame.Rect(arena_x, arena_y, arena_width, arena_height)

            # Arena interior is always white
            pygame.draw.rect(self.screen, (255, 255, 255), arena_rect)
            # Draw arena border
            pygame.draw.rect(self.screen, (100, 100, 100), arena_rect, int(3 * scale))

            # Character positions with animation offsets (adjusted for taller arena)
            char1_base_pos = (int(250 * scale_x), int(350 * scale_y))
            char2_base_pos = (int((screen_width - 250 * scale_x)), int(350 * scale_y))

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

            # Draw characters (pass scale for proper sizing)
            self._draw_character(char1, char1_pos, char1_hp, scale)
            self._draw_character(char2, char2_pos, char2_hp, scale)

            # Draw HP bars
            self._draw_hp_bars(char1, char2, char1_pos, char2_pos, char1_hp, char2_hp, shake_offset, scale)

            # Draw character names (below the character images)
            name1_surface = self.font.render(char1.name, True, (0, 0, 0))
            name2_surface = self.font.render(char2.name, True, (0, 0, 0))
            self.screen.blit(name1_surface, (char1_pos[0] - int(40 * scale), char1_pos[1] + int(170 * scale)))
            self.screen.blit(name2_surface, (char2_pos[0] - int(40 * scale), char2_pos[1] + int(170 * scale)))

            # Draw effects
            if self.effects:
                self.effects.draw()

            # Draw damage text
            if current_turn and not current_turn.is_miss and current_turn.damage > 0:
                defender_pos = char2_pos if current_turn.attacker_id == char1.id else char1_pos
                self._draw_damage_text(current_turn, defender_pos, scale)

            # Draw recent battle log (moved down to fit taller arena)
            if recent_logs:
                log_start_y = int(620 * scale_y)  # Moved from 520 to 620
                log_line_height = int(22 * scale_y)  # Slightly reduced from 25 to 22
                for i, log_entry in enumerate(recent_logs):
                    log_surface = self.small_font.render(log_entry, True, (0, 0, 0))
                    self.screen.blit(log_surface, (int(50 * scale_x), log_start_y + i * log_line_height))

            # Update display
            pygame.display.flip()

        except Exception as e:
            logger.error(f"Error rendering battle frame: {e}")

    def _draw_hp_bars(self, char1: Character, char2: Character, char1_pos: Tuple[int, int], char2_pos: Tuple[int, int], char1_hp: int, char2_hp: int, shake_offset: List[int], scale: float = 1.0):
        """Draw HP bars for both characters"""
        try:
            # Larger HP bars to match bigger characters
            hp_bar_width = int(250 * scale)  # Increased to 250 for even longer bar
            hp_bar_height = int(25 * scale)  # Increased from 20 to 25
            hp_bar_offset_x = int(125 * scale)  # Increased to 125 to center the longer bar
            hp_bar_offset_y = int(180 * scale)  # Increased from 80 to 180 for bigger characters

            # Calculate HP ratios
            char1_hp_ratio = max(0, char1_hp / char1.hp)
            char2_hp_ratio = max(0, char2_hp / char2.hp)

            # Character 1 HP bar
            hp1_bar_rect = pygame.Rect(char1_pos[0] - hp_bar_offset_x, char1_pos[1] - hp_bar_offset_y, hp_bar_width, hp_bar_height)
            hp1_fill_width = int(hp_bar_width * char1_hp_ratio)
            hp1_fill_rect = pygame.Rect(char1_pos[0] - hp_bar_offset_x, char1_pos[1] - hp_bar_offset_y, hp1_fill_width, hp_bar_height)

            pygame.draw.rect(self.screen, (255, 255, 255), hp1_bar_rect)
            pygame.draw.rect(self.screen, (0, 255, 0), hp1_fill_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), hp1_bar_rect, max(1, int(3 * scale)))  # Thicker border

            # Character 2 HP bar
            hp2_bar_rect = pygame.Rect(char2_pos[0] - hp_bar_offset_x, char2_pos[1] - hp_bar_offset_y, hp_bar_width, hp_bar_height)
            hp2_fill_width = int(hp_bar_width * char2_hp_ratio)
            hp2_fill_rect = pygame.Rect(char2_pos[0] - hp_bar_offset_x, char2_pos[1] - hp_bar_offset_y, hp2_fill_width, hp_bar_height)

            pygame.draw.rect(self.screen, (255, 255, 255), hp2_bar_rect)
            pygame.draw.rect(self.screen, (0, 255, 0), hp2_fill_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), hp2_bar_rect, max(1, int(3 * scale)))  # Thicker border

            # Draw HP text (using regular font for larger display)
            hp1_text = f"HP: {char1_hp}/{char1.hp}"
            hp2_text = f"HP: {char2_hp}/{char2.hp}"
            hp1_surface = self.font.render(hp1_text, True, (0, 0, 0))
            hp2_surface = self.font.render(hp2_text, True, (0, 0, 0))
            hp_text_offset_y = int(215 * scale)  # Increased from 205 to 215 to avoid overlap
            self.screen.blit(hp1_surface, (char1_pos[0] - hp_bar_offset_x, char1_pos[1] - hp_text_offset_y))
            self.screen.blit(hp2_surface, (char2_pos[0] - hp_bar_offset_x, char2_pos[1] - hp_text_offset_y))

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
    
    def _draw_damage_text(self, turn: BattleTurn, position: Tuple[int, int], display_scale: float = 1.0):
        """Draw animated damage text"""
        try:
            # Determine text color and style
            if turn.is_critical:
                damage_color = (255, 255, 50)  # Bright yellow for critical
                font_size = int(72 * display_scale)
                damage_text = f"{turn.damage}!!"
            else:
                damage_color = (255, 80, 80)  # Red for normal
                font_size = int(52 * display_scale)
                damage_text = str(turn.damage)

            # Create font for damage text
            damage_font = self._create_font(font_size)

            damage_surface = damage_font.render(damage_text, True, damage_color)

            # Add floating animation with larger movement
            float_offset = int(25 * display_scale * math.sin(pygame.time.get_ticks() * 0.008))
            text_pos = (position[0] - damage_surface.get_width() // 2,
                       position[1] - int(180 * display_scale) - float_offset)

            # Draw text with thicker outline for better visibility
            try:
                outline_surface = damage_font.render(damage_text, True, (0, 0, 0))
                outline_offset = int(3 * display_scale)
                for dx in [-outline_offset, -1, 0, 1, outline_offset]:
                    for dy in [-outline_offset, -1, 0, 1, outline_offset]:
                        if dx != 0 or dy != 0:
                            self.screen.blit(outline_surface, (text_pos[0] + dx, text_pos[1] + dy))
            except:
                pass  # Skip outline if it fails

            self.screen.blit(damage_surface, text_pos)

        except Exception as e:
            logger.error(f"Error drawing damage text: {e}")
    
    def _show_battle_start_screen(self, char1: Character, char2: Character):
        """Show battle start screen with VS display and countdown"""
        if not self.screen:
            return

        try:
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()

            # Load VS background image
            vs_bg_path = Path("assets/images/vs.jpg")
            if vs_bg_path.exists():
                vs_bg = pygame.image.load(str(vs_bg_path))
                vs_bg = pygame.transform.scale(vs_bg, (screen_width, screen_height))
            else:
                # Fallback: create gradient background
                vs_bg = pygame.Surface((screen_width, screen_height))
                for y in range(screen_height):
                    color_value = int(20 + (y / screen_height) * 60)
                    pygame.draw.line(vs_bg, (color_value, color_value, color_value + 20), (0, y), (screen_width, y))

            # Calculate positions for character circles
            circle_radius = int(150)
            left_circle_x = screen_width // 5  # Move left character more to the left
            right_circle_x = screen_width * 4 // 5  # Move right character more to the right
            circle_y = screen_height // 2

            # Load character sprites
            char1_sprite = self._load_character_sprite(char1)
            char2_sprite = self._load_character_sprite(char2)

            # Countdown from 3 to 1
            for count in [3, 2, 1]:
                # Draw background
                self.screen.blit(vs_bg, (0, 0))

                # Draw white circles for characters
                pygame.draw.circle(self.screen, (255, 255, 255), (left_circle_x, circle_y), circle_radius)
                pygame.draw.circle(self.screen, (255, 255, 255), (right_circle_x, circle_y), circle_radius)

                # Draw character 1 (left)
                if char1_sprite:
                    # Scale to fit in circle
                    char_size = circle_radius * 2 - 40  # Leave some padding
                    original_w, original_h = char1_sprite.get_size()
                    scale_factor = min(char_size / original_w, char_size / original_h)
                    new_w = int(original_w * scale_factor)
                    new_h = int(original_h * scale_factor)
                    scaled_char1 = pygame.transform.scale(char1_sprite, (new_w, new_h))
                    char1_pos = (left_circle_x - new_w // 2, circle_y - new_h // 2)
                    self.screen.blit(scaled_char1, char1_pos)

                # Draw character 2 (right)
                if char2_sprite:
                    # Scale to fit in circle
                    char_size = circle_radius * 2 - 40
                    original_w, original_h = char2_sprite.get_size()
                    scale_factor = min(char_size / original_w, char_size / original_h)
                    new_w = int(original_w * scale_factor)
                    new_h = int(original_h * scale_factor)
                    scaled_char2 = pygame.transform.scale(char2_sprite, (new_w, new_h))
                    char2_pos = (right_circle_x - new_w // 2, circle_y - new_h // 2)
                    self.screen.blit(scaled_char2, char2_pos)

                # Draw character names below circles
                name_font = self._create_font(36)
                name1_surface = name_font.render(char1.name, True, (255, 255, 255))
                name2_surface = name_font.render(char2.name, True, (255, 255, 255))
                name1_rect = name1_surface.get_rect(center=(left_circle_x, circle_y + circle_radius + 40))
                name2_rect = name2_surface.get_rect(center=(right_circle_x, circle_y + circle_radius + 40))

                # Draw with outline
                for dx in [-2, 0, 2]:
                    for dy in [-2, 0, 2]:
                        if dx != 0 or dy != 0:
                            outline1 = name_font.render(char1.name, True, (0, 0, 0))
                            outline2 = name_font.render(char2.name, True, (0, 0, 0))
                            self.screen.blit(outline1, (name1_rect.x + dx, name1_rect.y + dy))
                            self.screen.blit(outline2, (name2_rect.x + dx, name2_rect.y + dy))

                self.screen.blit(name1_surface, name1_rect)
                self.screen.blit(name2_surface, name2_rect)

                # Draw countdown number in upper center
                countdown_font = self._create_font(180)
                countdown_text = countdown_font.render(str(count), True, (255, 255, 0))
                countdown_rect = countdown_text.get_rect(center=(screen_width // 2, screen_height // 4))

                # Draw with thick outline
                for dx in [-4, 0, 4]:
                    for dy in [-4, 0, 4]:
                        if dx != 0 or dy != 0:
                            outline = countdown_font.render(str(count), True, (0, 0, 0))
                            self.screen.blit(outline, (countdown_rect.x + dx, countdown_rect.y + dy))

                self.screen.blit(countdown_text, countdown_rect)

                pygame.display.flip()
                pygame.time.wait(1000)  # Wait 1 second

            # Final "FIGHT!" display
            self.screen.blit(vs_bg, (0, 0))

            # Draw circles and characters one more time
            pygame.draw.circle(self.screen, (255, 255, 255), (left_circle_x, circle_y), circle_radius)
            pygame.draw.circle(self.screen, (255, 255, 255), (right_circle_x, circle_y), circle_radius)

            if char1_sprite:
                char_size = circle_radius * 2 - 40
                original_w, original_h = char1_sprite.get_size()
                scale_factor = min(char_size / original_w, char_size / original_h)
                new_w = int(original_w * scale_factor)
                new_h = int(original_h * scale_factor)
                scaled_char1 = pygame.transform.scale(char1_sprite, (new_w, new_h))
                char1_pos = (left_circle_x - new_w // 2, circle_y - new_h // 2)
                self.screen.blit(scaled_char1, char1_pos)

            if char2_sprite:
                char_size = circle_radius * 2 - 40
                original_w, original_h = char2_sprite.get_size()
                scale_factor = min(char_size / original_w, char_size / original_h)
                new_w = int(original_w * scale_factor)
                new_h = int(original_h * scale_factor)
                scaled_char2 = pygame.transform.scale(char2_sprite, (new_w, new_h))
                char2_pos = (right_circle_x - new_w // 2, circle_y - new_h // 2)
                self.screen.blit(scaled_char2, char2_pos)

            # Draw names
            name1_surface = name_font.render(char1.name, True, (255, 255, 255))
            name2_surface = name_font.render(char2.name, True, (255, 255, 255))
            name1_rect = name1_surface.get_rect(center=(left_circle_x, circle_y + circle_radius + 40))
            name2_rect = name2_surface.get_rect(center=(right_circle_x, circle_y + circle_radius + 40))

            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        outline1 = name_font.render(char1.name, True, (0, 0, 0))
                        outline2 = name_font.render(char2.name, True, (0, 0, 0))
                        self.screen.blit(outline1, (name1_rect.x + dx, name1_rect.y + dy))
                        self.screen.blit(outline2, (name2_rect.x + dx, name2_rect.y + dy))

            self.screen.blit(name1_surface, name1_rect)
            self.screen.blit(name2_surface, name2_rect)

            # Draw "FIGHT!" text in upper center
            fight_font = self._create_font(120)
            fight_text = fight_font.render("FIGHT!", True, (255, 100, 100))
            fight_rect = fight_text.get_rect(center=(screen_width // 2, screen_height // 4))

            for dx in [-4, 0, 4]:
                for dy in [-4, 0, 4]:
                    if dx != 0 or dy != 0:
                        outline = fight_font.render("FIGHT!", True, (0, 0, 0))
                        self.screen.blit(outline, (fight_rect.x + dx, fight_rect.y + dy))

            self.screen.blit(fight_text, fight_rect)

            pygame.display.flip()
            pygame.time.wait(1000)  # Show FIGHT! for 1 second

        except Exception as e:
            logger.error(f"Error showing battle start screen: {e}")

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
    
    def _draw_character(self, character: Character, position: Tuple[int, int], current_hp: int, display_scale: float = 1.0):
        """Draw character with image or fallback to colored rectangle"""
        try:
            max_width, max_height = int(300 * display_scale), int(300 * display_scale)  # Maximum display size

            # Try to load and display character image
            character_sprite = self._load_character_sprite(character)

            if character_sprite:
                # Scale image while preserving aspect ratio
                original_width, original_height = character_sprite.get_size()
                scale_x = max_width / original_width
                scale_y = max_height / original_height
                char_scale = min(scale_x, scale_y)  # Use smaller scale to fit within bounds

                new_width = int(original_width * char_scale)
                new_height = int(original_height * char_scale)

                scaled_sprite = pygame.transform.scale(character_sprite, (new_width, new_height))

                # Calculate position to center the image
                char_x = position[0] - new_width // 2
                char_y = position[1] - new_height // 2

                # Draw the character image (no HP-based color effects)
                self.screen.blit(scaled_sprite, (char_x, char_y))
            else:
                # Fallback to colored rectangle
                char_width, char_height = int(80 * display_scale), int(120 * display_scale)
                char_x = position[0] - char_width // 2
                char_y = position[1] - char_height // 2
                char_rect = pygame.Rect(char_x, char_y, char_width, char_height)
                hp_ratio = max(0, current_hp / character.hp)
                char_color = (int(255 * (1 - hp_ratio)), int(255 * hp_ratio), 0)

                pygame.draw.rect(self.screen, char_color, char_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), char_rect, max(1, int(2 * display_scale)))

        except Exception as e:
            logger.error(f"Error drawing character {character.name}: {e}")
            # Emergency fallback - draw simple rectangle
            fallback_width, fallback_height = int(80 * display_scale), int(120 * display_scale)
            char_rect = pygame.Rect(position[0] - fallback_width // 2, position[1] - fallback_height // 2,
                                   fallback_width, fallback_height)
            pygame.draw.rect(self.screen, (128, 128, 128), char_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), char_rect, max(1, int(2 * display_scale)))
    
    def _load_background_image(self):
        """Load battle arena background image"""
        try:
            background_path = Path("assets/images/battle_arena.png")

            if background_path.exists():
                self.background_image = pygame.image.load(str(background_path))
                logger.info(f"Loaded background image from {background_path}")
            else:
                logger.warning(f"Background image not found at {background_path}, using default background")
                self.background_image = None
        except Exception as e:
            logger.error(f"Error loading background image: {e}")
            self.background_image = None

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
            # Get actual screen size
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()

            # Calculate scale factor based on screen size (base: 1024x768)
            scale_x = screen_width / 1024
            scale_y = screen_height / 768
            scale = min(scale_x, scale_y)  # Use the smaller scale to maintain aspect ratio

            # Clear any pending events first
            pygame.event.clear()

            # Draw gradient background overlay
            for y in range(screen_height):
                alpha = int(230 * (y / screen_height))
                line_surface = pygame.Surface((screen_width, 1))
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
            victory_font = self._create_font(int(120 * scale))

            if winner:
                victory_text = "VICTORY!"
                victory_surface = victory_font.render(victory_text, True, winner_color)
            else:
                victory_text = "DRAW!"
                victory_surface = victory_font.render(victory_text, True, winner_color)

            # Draw with glow effect
            glow_offset = int(3 * scale)
            victory_y = int(60 * scale_y)
            for offset in [(0, 0), (-glow_offset, -glow_offset), (glow_offset, glow_offset),
                          (-glow_offset, glow_offset), (glow_offset, -glow_offset)]:
                glow_surface = victory_font.render(victory_text, True, winner_bg_color)
                glow_rect = glow_surface.get_rect(center=(screen_width // 2 + offset[0], victory_y + offset[1]))
                self.screen.blit(glow_surface, glow_rect)

            victory_rect = victory_surface.get_rect(center=(screen_width // 2, victory_y))
            self.screen.blit(victory_surface, victory_rect)

            # Draw winner name with large font (below VICTORY text)
            name_font = self._create_font(int(60 * scale))
            winner_name_surface = name_font.render(winner_name, True, winner_color)
            # Draw with outline
            outline_offset = int(2 * scale)
            name_y = int(150 * scale_y)
            for dx in [-outline_offset, 0, outline_offset]:
                for dy in [-outline_offset, 0, outline_offset]:
                    if dx != 0 or dy != 0:
                        outline_surface = name_font.render(winner_name, True, (0, 0, 0))
                        outline_rect = outline_surface.get_rect(center=(screen_width // 2 + dx, name_y + dy))
                        self.screen.blit(outline_surface, outline_rect)

            name_rect = winner_name_surface.get_rect(center=(screen_width // 2, name_y))
            self.screen.blit(winner_name_surface, name_rect)

            # Draw character images side by side (in the middle area)
            char_display_size = int(180 * scale)
            char_y_winner = int(220 * scale_y)
            char_x_offset = int(220 * scale_x)

            # Winner character (left side, larger)
            if winner:
                winner_sprite = self._load_character_sprite(winner)
                if winner_sprite:
                    # Scale to fit
                    original_w, original_h = winner_sprite.get_size()
                    char_scale = min(char_display_size / original_w, char_display_size / original_h)
                    new_w, new_h = int(original_w * char_scale * 1.2), int(original_h * char_scale * 1.2)  # 20% larger for winner
                    scaled_winner = pygame.transform.scale(winner_sprite, (new_w, new_h))

                    # Draw white background for character
                    winner_pos = (screen_width // 2 - char_x_offset, char_y_winner)
                    border_padding = int(10 * scale)
                    bg_rect = pygame.Rect(winner_pos[0] - border_padding, winner_pos[1] - border_padding,
                                         new_w + border_padding * 2, new_h + border_padding * 2)
                    pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)  # White background

                    # Draw winner with golden border
                    border_width = int(8 * scale)
                    pygame.draw.rect(self.screen, winner_color, bg_rect, border_width)
                    pygame.draw.rect(self.screen, winner_bg_color, bg_rect, int(4 * scale))
                    self.screen.blit(scaled_winner, winner_pos)

                    # Draw crown symbol above winner (using simple shapes instead of emoji)
                    crown_center_x = winner_pos[0] + new_w // 2
                    crown_center_y = winner_pos[1] - int(40 * scale)
                    crown_size = scale

                    # Draw crown shape with triangles
                    crown_points = [
                        (crown_center_x, crown_center_y - int(15 * crown_size)),  # Top point
                        (crown_center_x - int(20 * crown_size), crown_center_y),   # Left point
                        (crown_center_x - int(15 * crown_size), crown_center_y + int(10 * crown_size)), # Left base
                        (crown_center_x + int(15 * crown_size), crown_center_y + int(10 * crown_size)), # Right base
                        (crown_center_x + int(20 * crown_size), crown_center_y),   # Right point
                    ]
                    pygame.draw.polygon(self.screen, winner_color, crown_points)
                    pygame.draw.polygon(self.screen, winner_bg_color, crown_points, int(3 * scale))

                    # Crown jewels (circles)
                    pygame.draw.circle(self.screen, (255, 50, 50),
                                     (crown_center_x, crown_center_y - int(10 * crown_size)), int(5 * crown_size))
                    pygame.draw.circle(self.screen, (50, 255, 50),
                                     (crown_center_x - int(15 * crown_size), crown_center_y), int(4 * crown_size))
                    pygame.draw.circle(self.screen, (50, 50, 255),
                                     (crown_center_x + int(15 * crown_size), crown_center_y), int(4 * crown_size))

                # Loser character (right side, smaller)
                if loser:
                    loser_sprite = self._load_character_sprite(loser)
                    if loser_sprite:
                        original_w, original_h = loser_sprite.get_size()
                        char_scale_loser = min(char_display_size / original_w, char_display_size / original_h)
                        new_w, new_h = int(original_w * char_scale_loser * 0.75), int(original_h * char_scale_loser * 0.75)  # 25% smaller for loser
                        scaled_loser = pygame.transform.scale(loser_sprite, (new_w, new_h))

                        # Draw white background for character
                        char_y_loser = int(250 * scale_y)
                        loser_x_offset = int(80 * scale_x)
                        loser_pos = (screen_width // 2 + loser_x_offset, char_y_loser)
                        loser_border_padding = int(5 * scale)
                        bg_rect = pygame.Rect(loser_pos[0] - loser_border_padding, loser_pos[1] - loser_border_padding,
                                             new_w + loser_border_padding * 2, new_h + loser_border_padding * 2)
                        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)  # White background

                        # Draw loser with gray border
                        pygame.draw.rect(self.screen, (100, 100, 100), bg_rect, int(4 * scale))
                        self.screen.blit(scaled_loser, loser_pos)

            # Draw battle stats with better formatting
            stats_y = screen_height - int(240 * scale_y)
            panel_width = int(600 * scale_x)
            panel_height = int(130 * scale_y)
            panel_x = screen_width // 2 - panel_width // 2
            panel_padding = int(10 * scale)

            # Stats background panel
            stats_panel = pygame.Rect(panel_x, stats_y - panel_padding, panel_width, panel_height)
            panel_surface = pygame.Surface((panel_width, panel_height))
            panel_surface.set_alpha(180)
            panel_surface.fill((40, 40, 60))
            self.screen.blit(panel_surface, (panel_x, stats_y - panel_padding))
            pygame.draw.rect(self.screen, winner_color, stats_panel, int(3 * scale))

            stats_font = self._create_font(int(28 * scale))

            # Draw stats with custom icons (no emojis)
            stats_data = [
                ("TIME", f"バトル時間: {battle.duration:.2f}秒", (100, 200, 255)),
                ("TURN", f"総ターン数: {len(battle.turns)}", (255, 200, 100)),
                ("HP1", f"{char1.name}: {char1_hp} HP", (255, 100, 100)),
                ("HP2", f"{char2.name}: {char2_hp} HP", (255, 100, 100))
            ]

            stat_line_height = int(28 * scale_y)
            stat_start_y = int(5 * scale)
            icon_size = int(12 * scale)

            for i, (icon_type, stat_text, icon_color) in enumerate(stats_data):
                stat_y = stats_y + stat_start_y + i * stat_line_height

                # Draw icon on the left
                icon_x = panel_x + int(50 * scale_x)
                icon_center_y = stat_y + int(8 * scale)

                if icon_type == "TIME":
                    # Clock icon
                    pygame.draw.circle(self.screen, icon_color, (icon_x, icon_center_y), icon_size, int(2 * scale))
                    pygame.draw.line(self.screen, icon_color, (icon_x, icon_center_y),
                                   (icon_x, icon_center_y - int(6 * scale)), int(2 * scale))
                    pygame.draw.line(self.screen, icon_color, (icon_x, icon_center_y),
                                   (icon_x + int(6 * scale), icon_center_y), int(2 * scale))
                elif icon_type == "TURN":
                    # Circular arrow icon
                    pygame.draw.circle(self.screen, icon_color, (icon_x, icon_center_y), int(10 * scale), int(2 * scale))
                    arrow_points = [
                        (icon_x + int(8 * scale), icon_center_y),
                        (icon_x + int(12 * scale), icon_center_y - int(4 * scale)),
                        (icon_x + int(12 * scale), icon_center_y + int(4 * scale))
                    ]
                    pygame.draw.polygon(self.screen, icon_color, arrow_points)
                elif icon_type.startswith("HP"):
                    # Heart icon
                    pygame.draw.circle(self.screen, icon_color,
                                     (icon_x - int(4 * scale), icon_center_y - int(4 * scale)), int(6 * scale))
                    pygame.draw.circle(self.screen, icon_color,
                                     (icon_x + int(4 * scale), icon_center_y - int(4 * scale)), int(6 * scale))
                    heart_points = [
                        (icon_x - int(10 * scale), icon_center_y - int(4 * scale)),
                        (icon_x, icon_center_y + int(6 * scale)),
                        (icon_x + int(10 * scale), icon_center_y - int(4 * scale))
                    ]
                    pygame.draw.polygon(self.screen, icon_color, heart_points)

                # Draw stat text
                stat_surface = stats_font.render(stat_text, True, (255, 255, 200))
                stat_rect = stat_surface.get_rect(left=icon_x + int(25 * scale_x), centery=icon_center_y)
                self.screen.blit(stat_surface, stat_rect)
            
            # Draw OK button with improved styling
            button_width = int(180 * scale_x)
            button_height = int(50 * scale_y)
            button_x = screen_width // 2 - button_width // 2
            button_y = screen_height - int(70 * scale_y)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            # Button with gradient effect
            pygame.draw.rect(self.screen, (100, 180, 100), button_rect)
            pygame.draw.rect(self.screen, (150, 255, 150), button_rect, int(4 * scale))

            # Button text
            button_font = self._create_font(int(40 * scale))

            button_text = button_font.render("OK", True, (255, 255, 255))
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)

            # Draw instruction text with countdown
            instruction_font = self._create_font(int(20 * scale))

            pygame.display.flip()

            # Wait for user input or auto-close after 3 seconds
            waiting = True
            clock = pygame.time.Clock()
            auto_close_time = 3.0  # Auto-close after 3 seconds
            elapsed_time = 0.0

            while waiting:
                dt = clock.tick(30) / 1000.0  # Delta time in seconds
                elapsed_time += dt

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

                # Auto-close after timeout
                if elapsed_time >= auto_close_time:
                    waiting = False

                # Update countdown display
                remaining_time = max(0, auto_close_time - elapsed_time)
                if remaining_time > 0:
                    instruction_text = f"クリックまたはスペースキーで閉じる ({remaining_time:.1f}秒後に自動で閉じます)"
                else:
                    instruction_text = "閉じています..."

                # Redraw instruction text with countdown
                instruction_surface = instruction_font.render(instruction_text, True, (180, 180, 200))
                instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, button_y - int(15 * scale_y)))

                # Clear the instruction area and redraw
                clear_rect = pygame.Rect(0, button_y - int(30 * scale_y), screen_width, int(30 * scale_y))

                # Redraw the background for this area
                for y in range(clear_rect.top, clear_rect.bottom):
                    alpha = int(230 * (y / screen_height))
                    line_surface = pygame.Surface((screen_width, 1))
                    line_surface.set_alpha(alpha)
                    line_surface.fill((20, 20, 40))
                    self.screen.blit(line_surface, (0, y))

                self.screen.blit(instruction_surface, instruction_rect)
                pygame.display.flip()
            
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