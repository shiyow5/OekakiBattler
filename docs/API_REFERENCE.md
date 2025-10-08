# API Reference - Oekaki Battler

## Overview

This document provides technical reference for the Oekaki Battler system components, classes, and methods for developers who want to extend or modify the system.

## Table of Contents

1. [Models](#models)
   - [Character](#character)
   - [Battle](#battle)
   - [StoryBoss](#storyboss)
   - [StoryProgress](#storyprogress)
2. [Services](#services)
3. [Configuration](#configuration)
4. [Database](#database)
5. [Utilities](#utilities)
6. [Usage Examples](#usage-examples)

---

## Models

### Character

Represents a character in the battle system.

```python
from src.models import Character

class Character(BaseModel):
    id: str                    # Unique identifier (UUID)
    name: str                  # Character name
    hp: int                    # Health Points (10-200)
    attack: int                # Attack power (10-150)
    defense: int               # Defense power (10-100)
    speed: int                 # Speed (10-100)
    magic: int                 # Magic power (10-100)
    luck: int                  # Luck (0-100)
    description: str           # Character description
    image_path: str            # Original image file path
    sprite_path: Optional[str] # Processed sprite path
    created_at: datetime       # Creation timestamp
    battle_count: int          # Total battles participated
    win_count: int            # Total wins
```

**Stat Constraints:**
- Total stats maximum: 350 (sum of hp + attack + defense + speed + magic + luck)
- Model validator enforces this limit automatically

**Properties:**
- `win_rate: float` - Win rate percentage
- `total_stats: int` - Sum of all stats (includes luck)

**Methods:**
- `to_dict() -> dict` - Convert to dictionary for database storage
- `from_dict(data: dict) -> Character` - Create from dictionary

### Battle

Represents a battle between two characters.

```python
from src.models import Battle, BattleTurn

class Battle(BaseModel):
    id: str                    # Unique battle identifier
    character1_id: str         # First fighter ID
    character2_id: str         # Second fighter ID
    winner_id: Optional[str]   # Winner's character ID
    battle_log: List[str]      # Battle event log
    turns: List[BattleTurn]    # Detailed turn data
    duration: float            # Battle duration in seconds
    created_at: datetime       # Battle timestamp
```

**Properties:**
- `is_finished: bool` - Whether battle is completed
- `turn_count: int` - Number of turns played

**Methods:**
- `add_log_entry(message: str)` - Add entry to battle log
- `add_turn(turn: BattleTurn)` - Add turn to battle

### BattleTurn

Represents a single turn in battle.

```python
class BattleTurn(BaseModel):
    turn_number: int          # Turn sequence number
    attacker_id: str          # Attacking character ID
    defender_id: str          # Defending character ID
    action_type: str          # "attack", "magic", etc.
    damage: int               # Damage dealt
    is_critical: bool         # Whether it was critical hit
    is_miss: bool            # Whether attack missed
    attacker_hp_after: int    # Attacker HP after turn
    defender_hp_after: int    # Defender HP after turn
```

### StoryBoss

Represents a story mode boss character.

```python
from src.models.story_boss import StoryBoss

class StoryBoss(BaseModel):
    level: int                 # Boss level (1-5)
    name: str                  # Boss name
    hp: int                    # Health Points (10-300)
    attack: int                # Attack power (10-200)
    defense: int               # Defense power (10-150)
    speed: int                 # Speed (10-150)
    magic: int                 # Magic power (10-150)
    luck: int                  # Luck (0-100)
    description: str           # Boss description
    image_path: Optional[str]  # Original image file path/URL
    sprite_path: Optional[str] # Processed sprite path/URL
```

**Stat Constraints:**
- Total stats maximum: 500 (higher than regular characters)
- Model validator enforces this limit automatically

**Properties:**
- Wider stat ranges and higher total limit compared to regular characters
- Level determines boss difficulty (1=easiest, 5=hardest)

**Methods:**
- `to_dict() -> dict` - Convert to dictionary for database storage
- `from_dict(data: dict) -> StoryBoss` - Create from dictionary

### StoryProgress

Represents a player's story mode progress.

```python
from src.models.story_boss import StoryProgress

class StoryProgress(BaseModel):
    character_id: str          # Player character ID
    current_level: int         # Current level (1-5)
    completed: bool            # Whether story mode is completed
    victories: list[int]       # List of defeated boss levels
    attempts: int              # Total attempts
    last_played: datetime      # Last played timestamp
```

**Properties:**
- Tracks per-character progress
- Persists through sessions

**Methods:**
- `to_dict() -> dict` - Convert to dictionary for database storage
- `from_dict(data: dict) -> StoryProgress` - Create from dictionary

---

## Services

### DatabaseManager

Handles all database operations for characters and battles.

```python
from src.services.database_manager import DatabaseManager

db_manager = DatabaseManager()
```

**Character Operations:**
```python
# Save character
success = db_manager.save_character(character)

# Get character by ID
character = db_manager.get_character(character_id)

# Get all characters
characters = db_manager.get_all_characters()

# Search characters
results = db_manager.search_characters(
    name_pattern="dragon",
    min_total_stats=300,
    max_total_stats=500
)

# Delete character
success = db_manager.delete_character(character_id)
```

**Battle Operations:**
```python
# Save battle
success = db_manager.save_battle(battle)

# Get battle details
battle = db_manager.get_battle(battle_id)

# Get recent battles
battles = db_manager.get_recent_battles(limit=20)

# Get character's battles
battles = db_manager.get_character_battles(character_id)

# Get statistics
stats = db_manager.get_statistics()
```

### ImageProcessor

Handles image processing for character extraction.

```python
from src.services.image_processor import ImageProcessor

processor = ImageProcessor()
```

**Core Methods:**
```python
# Load image
image = processor.load_image(image_path)

# Extract character from background
extracted = processor.extract_character(image)

# Preprocess for AI analysis
processed = processor.preprocess_image(image)

# Save sprite
success = processor.save_sprite(sprite, output_path)

# Validate image
is_valid, message = processor.validate_image(image_path)

# Complete processing pipeline
success, message, sprite_path = processor.process_character_image(
    input_path,
    output_dir,
    character_name
)
```

**Configuration:**
- `target_size: tuple` - Target image size (300x300)
- `supported_formats: list` - Supported file formats
- `min_resolution: tuple` - Minimum required resolution

### AIAnalyzer

Handles AI-powered character stat generation.

```python
from src.services.ai_analyzer import AIAnalyzer

analyzer = AIAnalyzer()
```

**Core Methods:**
```python
# Analyze character image
stats = analyzer.analyze_character(image_path, fallback_stats=True)

# Batch analysis
results = analyzer.analyze_batch(image_paths)

# Test API connection
success = analyzer.test_api_connection()
```

**Configuration:**
- Requires `GOOGLE_API_KEY` environment variable
- Uses Google Gemini AI model
- Includes fallback stat generation

**Stat Generation:**
- Analyzes visual features to determine stats:
  - HP (10-200): Body size, robustness
  - Attack (10-150): Weapons, muscular appearance
  - Defense (10-100): Armor, shields
  - Speed (10-100): Body type, limb length
  - Magic (10-100): Magic items, mystical decorations
  - Luck (0-100): Lucky symbols, bright expressions, sparkly decorations
- Automatically enforces total stats ≤ 350
- Proportionally scales down if AI generates stats exceeding limit

### BattleEngine

Handles automated character battles with Pygame visualization.

```python
from src.services.battle_engine import BattleEngine

engine = BattleEngine()
```

**Core Methods:**
```python
# Initialize display
success = engine.initialize_display()

# Start battle
battle = engine.start_battle(char1, char2, visual_mode=True)

# Calculate damage
damage, is_critical, is_miss = engine.calculate_damage(
    attacker, defender, action_type="attack"
)

# Get battle result summary
result = engine.get_battle_result(battle, char1, char2)

# Cleanup resources
engine.cleanup()
```

### StoryModeEngine

Manages story mode progression and battles.

```python
from src.services.story_mode_engine import StoryModeEngine

story_engine = StoryModeEngine(db_manager)
```

**Core Methods:**
```python
# Load all bosses
success = story_engine.load_bosses()

# Get boss by level
boss = story_engine.get_boss(level=1)

# Get player progress
progress = story_engine.get_player_progress(character_id)

# Start battle
battle = story_engine.start_battle(player, boss_level=1)

# Execute battle
result = story_engine.execute_battle(visual_mode=True)

# Update progress
success = story_engine.update_progress(character_id, boss_level=1, victory=True)

# Get next boss level
next_level = story_engine.get_next_boss_level(character_id)

# Check completion
is_completed = story_engine.is_completed(character_id)

# Reset progress
success = story_engine.reset_progress(character_id)
```

**Features:**
- Sequential boss battles (Lv1-Lv5)
- Per-character progress tracking
- Automatic level progression
- Integration with BattleEngine
- Sprite caching for boss images

**Boss Management:**
- Bosses stored in Google Sheets (StoryBosses worksheet)
- Progress stored in Google Sheets (StoryProgress worksheet)
- Automatic sprite downloading and caching
```

**Configuration:**
- `max_turns: int` - Maximum battle turns (50)
- `critical_chance: float` - Critical hit probability (0.05)
- `critical_multiplier: float` - Critical damage multiplier (2.0)

---

## Configuration

### Settings

Central configuration management.

```python
from config.settings import Settings

# Access configuration
api_key = Settings.GOOGLE_API_KEY
target_size = Settings.TARGET_IMAGE_SIZE
screen_width = Settings.SCREEN_WIDTH
```

**Available Settings:**
- `GOOGLE_API_KEY` - Google AI API key
- `MODEL_NAME` - AI model name
- `TARGET_IMAGE_SIZE` - Image processing target size
- `MAX_TURNS` - Battle system max turns
- `SCREEN_WIDTH/HEIGHT` - Display dimensions
- `FPS` - Frame rate for battles

### Database Configuration

```python
from config.database import initialize_database, get_connection

# Initialize database
initialize_database()

# Get connection
conn = get_connection()

# Execute query
result = execute_query(query, params)
```

---

## Database

### Schema

**Characters Table:**
```sql
CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    hp INTEGER NOT NULL,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    speed INTEGER NOT NULL,
    magic INTEGER NOT NULL,
    description TEXT,
    image_path TEXT NOT NULL,
    sprite_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    battle_count INTEGER DEFAULT 0,
    win_count INTEGER DEFAULT 0
);
```

**Battles Table:**
```sql
CREATE TABLE battles (
    id TEXT PRIMARY KEY,
    character1_id TEXT NOT NULL,
    character2_id TEXT NOT NULL,
    winner_id TEXT,
    battle_log TEXT,
    duration REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character1_id) REFERENCES characters (id),
    FOREIGN KEY (character2_id) REFERENCES characters (id),
    FOREIGN KEY (winner_id) REFERENCES characters (id)
);
```

**Battle Turns Table:**
```sql
CREATE TABLE battle_turns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    battle_id TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    attacker_id TEXT NOT NULL,
    defender_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    damage INTEGER DEFAULT 0,
    is_critical BOOLEAN DEFAULT 0,
    is_miss BOOLEAN DEFAULT 0,
    attacker_hp_after INTEGER NOT NULL,
    defender_hp_after INTEGER NOT NULL,
    FOREIGN KEY (battle_id) REFERENCES battles (id)
);
```

---

## Utilities

### Image Utils

```python
from src.utils.image_utils import (
    auto_rotate_image,
    remove_noise,
    crop_to_content,
    normalize_size_aspect_ratio,
    enhance_drawing_features
)

# Auto-rotate image
rotated = auto_rotate_image(image)

# Remove noise
cleaned = remove_noise(image)

# Crop to content
cropped = crop_to_content(image, padding=10)

# Normalize size
normalized = normalize_size_aspect_ratio(image, (300, 300))

# Enhance drawing features
enhanced = enhance_drawing_features(image)
```

### File Utils

```python
from src.utils.file_utils import (
    ensure_directory,
    get_file_hash,
    copy_file_with_unique_name,
    save_json,
    load_json,
    clean_filename
)

# Ensure directory exists
ensure_directory("path/to/dir")

# Get file hash
hash_value = get_file_hash("file.png")

# Save/load JSON
save_json(data, "data.json")
data = load_json("data.json")

# Clean filename
clean_name = clean_filename("invalid<>filename.txt")
```

---

## Usage Examples

### Complete Character Registration

```python
from src.services import ImageProcessor, AIAnalyzer, DatabaseManager
from src.models import Character

# Initialize services
processor = ImageProcessor()
analyzer = AIAnalyzer()
db_manager = DatabaseManager()

# Process image
success, message, sprite_path = processor.process_character_image(
    "character.png", "sprites/", "MyCharacter"
)

if success:
    # Analyze with AI
    stats = analyzer.analyze_character("character.png")
    
    if stats:
        # Create character
        character = Character(
            name="MyCharacter",
            hp=stats.hp,
            attack=stats.attack,
            defense=stats.defense,
            speed=stats.speed,
            magic=stats.magic,
            luck=stats.luck,
            description=stats.description,
            image_path="character.png",
            sprite_path=sprite_path
        )
        
        # Save to database
        db_manager.save_character(character)
```

### Run Battle

```python
from src.services import BattleEngine, DatabaseManager

# Initialize services
engine = BattleEngine()
db_manager = DatabaseManager()

# Get characters
chars = db_manager.get_all_characters()
if len(chars) >= 2:
    # Start battle
    battle = engine.start_battle(chars[0], chars[1], visual_mode=True)
    
    # Save battle
    db_manager.save_battle(battle)
    
    # Get results
    result = engine.get_battle_result(battle, chars[0], chars[1])
    print(f"Winner: {battle.winner_id}")
    print(f"Duration: {battle.duration}s")
    print(f"Turns: {len(battle.turns)}")
```

### Custom AI Analysis

```python
from src.services.ai_analyzer import AIAnalyzer

class CustomAnalyzer(AIAnalyzer):
    def _get_detailed_analysis_prompt(self):
        return """
        Custom prompt for your specific analysis needs...
        """
    
    def custom_analysis_method(self, image_path):
        # Your custom analysis logic
        pass

# Use custom analyzer
analyzer = CustomAnalyzer()
stats = analyzer.analyze_character("image.png")
```

### Extend Battle Engine

```python
from src.services.battle_engine import BattleEngine

class CustomBattleEngine(BattleEngine):
    def calculate_damage(self, attacker, defender, action_type="attack"):
        # Custom damage calculation
        base_damage, is_critical, is_miss = super().calculate_damage(
            attacker, defender, action_type
        )
        
        # Apply custom modifiers
        if action_type == "special":
            base_damage *= 1.5
        
        return base_damage, is_critical, is_miss
```

---

## Error Handling

All services include comprehensive error handling with logging:

```python
import logging

# Service methods return appropriate error indicators
success = service.method()
if not success:
    # Check logs for details
    logging.error("Operation failed")

# Optional objects return None on error
result = service.get_something(id)
if result is None:
    # Handle missing/error case
    pass
```

---

## Extension Points

### Adding New Stats

1. Update `Character` model
2. Modify AI analysis prompts
3. Update database schema
4. Adjust battle calculations

### Custom Battle Mechanics

1. Extend `BattleEngine` class
2. Override damage/turn calculation methods
3. Add new action types
4. Modify win conditions

### Additional AI Models

1. Create new analyzer classes
2. Implement analysis interface
3. Add configuration options
4. Integrate with registration system

---

For more detailed information, refer to the source code and inline documentation.