# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**お絵描きバトラー (Oekaki Battler)** is a Python-based automatic fighting game that brings hand-drawn characters to life. The workflow involves:

1. **Analog Drawing**: Users draw characters on paper
2. **Digital Capture**: Drawings are scanned/photographed to create digital images
3. **Character Extraction**: AI extracts and processes character sprites from the images
4. **Stat Generation**: Google's Generative AI analyzes character illustrations and generates RPG-style stats (HP, attack, defense, speed, magic) and descriptions
5. **Automated Battle**: Characters fight automatically on screen based on their generated stats - no user control during combat
6. **Data Persistence**: Character data, battle history, and rankings are stored in Google Sheets (online mode) or local SQLite database (offline mode)

This creates a unique experience where the artistic style and appearance of hand-drawn characters directly influence their battle performance through AI analysis.

## Development Environment

### Python Environment
- **Python Version**: 3.11+ (based on virtual environment)
- **Virtual Environment**: `.venv/` (already configured)
- **Dependencies**: Managed via `requirements.txt`

### Key Dependencies
```
# Core Libraries
pygame              # Game engine and graphics
pillow              # Image processing
opencv-python       # Advanced image processing

# AI & Cloud Services
google-generativeai # Google Gemini AI integration
gspread            # Google Sheets API client
google-auth        # Google API authentication
google-api-python-client  # Google Drive API

# Data & Validation
pydantic           # Data validation and parsing
python-dotenv      # Environment variable management
sqlalchemy         # SQL database ORM (SQLite)

# LINE Bot Integration (optional)
Node.js 14+        # Required for LINE Bot server
@line/bot-sdk      # LINE Bot SDK
express            # Web server framework
```

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# For LINE Bot functionality
cd server
npm install
```

## Running the Application

### Main Application (GUI)
```bash
python main.py
```
Launches the Tkinter-based GUI for character management and battles.

### LINE Bot Server (Optional)
```bash
./server_up.sh
```
Starts the Node.js server with ngrok for LINE Bot integration.

### Environment Variables

#### Main Application (`.env`)
Required in root directory:
```
GOOGLE_API_KEY=your_google_api_key          # Google Generative AI
MODEL_NAME=gemini-2.5-flash-lite-preview-06-17
SPREADSHEET_ID=your_spreadsheet_id          # Google Sheets ID
WORKSHEET_NAME=Characters                   # Default worksheet
BATTLE_HISTORY_SHEET=BattleHistory         # Battle history worksheet
RANKING_SHEET=Rankings                     # Rankings worksheet
GOOGLE_CREDENTIALS_PATH=credentials.json    # Service account JSON
DRIVE_FOLDER_ID=your_folder_id             # Optional: Google Drive folder
```

#### LINE Bot Server (`server/.env`)
Required for LINE Bot functionality:
```
PORT=3000
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
GAS_WEBHOOK_URL=https_script.google.com/macros/s/XXXXX/exec
SHARED_SECRET=your_shared_secret_for_gas
```

## Code Architecture

### Project Structure
```
OekakiBattler/
├── main.py                    # Application entry point
├── img2txt.py                 # Standalone AI image analysis
├── config/
│   ├── settings.py           # Global settings & env vars
│   └── database.py           # SQLAlchemy database setup
├── src/
│   ├── models/
│   │   ├── character.py      # Character data model (Pydantic)
│   │   └── battle.py         # Battle data model with statistics
│   ├── services/
│   │   ├── ai_analyzer.py    # Google Gemini AI analysis
│   │   ├── image_processor.py # Image extraction & sprite processing
│   │   ├── battle_engine.py  # Battle simulation engine
│   │   ├── sheets_manager.py # Google Sheets/Drive manager (online mode)
│   │   ├── database_manager.py # SQLite manager (offline mode)
│   │   ├── audio_manager.py  # Sound effects manager
│   │   └── settings_manager.py # User settings persistence
│   ├── ui/
│   │   └── main_menu.py      # Tkinter/Pygame GUI
│   └── utils/
│       ├── image_utils.py    # Image utility functions
│       └── file_utils.py     # File I/O utilities
├── server/
│   ├── server.js             # Node.js LINE Bot server
│   └── .env                  # LINE Bot configuration
├── assets/
│   ├── images/               # Battle backgrounds, UI elements
│   └── sounds/               # Sound effects (optional)
├── data/
│   ├── database.db           # SQLite database (offline mode)
│   ├── characters/           # Original character images
│   └── sprites/              # Processed character sprites
└── tests/                    # Unit and integration tests
```

### Data Models

#### Character Model (`src/models/character.py`)
```python
class Character(BaseModel):
    id: str                    # UUID
    name: str
    image_path: str           # Local path or Google Drive URL
    sprite_path: str          # Local path or Google Drive URL
    hp: int                   # 50-150
    attack: int               # 30-120
    defense: int              # 20-100
    speed: int                # 40-130
    magic: int                # 10-100
    description: str          # AI-generated description
    created_at: datetime
    wins: int = 0
    losses: int = 0
    draws: int = 0
```

#### Battle Model (`src/models/battle.py`)
```python
class Battle(BaseModel):
    id: str
    character1_id: str
    character2_id: str
    winner_id: Optional[str]
    battle_log: List[str]
    turns: List[BattleTurn]
    duration: float
    created_at: datetime

    # Battle statistics
    char1_final_hp: int
    char2_final_hp: int
    char1_damage_dealt: int
    char2_damage_dealt: int
    result_type: str          # "KO", "Time Limit", "Draw"
```

### Core System Components

#### 1. Image Processing Pipeline (`image_processor.py`)
- **Background Removal**: Removes background from scanned images
- **Sprite Extraction**: Isolates character from drawing
- **Image Optimization**: Resizes and formats for battle display
- **Multi-format Support**: Handles PNG, JPG, JPEG

#### 2. AI Analysis System (`ai_analyzer.py`)
- **Visual Analysis**: Google Gemini analyzes character appearance
- **Stat Generation**: Converts visual features to RPG stats
- **Character Profiling**: Generates Japanese descriptions
- **Structured Output**: Uses Pydantic models for validation

#### 3. Automated Battle System (`battle_engine.py`)
- **Turn-Based Combat**: Speed determines action order
- **Damage Calculation**: `damage = attack - defense + random_factor`
- **Special Mechanics**: Critical hits (5%), magic attacks, evasion
- **Battle Statistics**: Tracks damage dealt, final HP, result type
- **Visual Display**: Real-time Pygame rendering with HP bars and animations

#### 4. Data Persistence Layer

**Online Mode (`sheets_manager.py`):**
- **Google Sheets Integration**: 3 worksheets (Characters, BattleHistory, Rankings)
- **Google Drive Upload**: Automatic image upload with public URLs
- **Battle History Recording**: Detailed 15-column battle logs
- **Auto-Ranking Updates**: Rating = (Wins × 3) + Draws
- **Image Caching**: Downloads and caches images from Drive URLs

**Offline Mode (`database_manager.py`):**
- **SQLite Database**: Local data persistence
- **Automatic Fallback**: Used when Google Sheets unavailable
- **Limited Features**: No battle history or rankings
- **File Storage**: Images stored locally only

**Mode Detection:**
```python
# Application automatically detects mode on startup
sheets_manager = SheetsManager()
if sheets_manager.online_mode:
    # Use Google Sheets/Drive
    self.db_manager = sheets_manager
else:
    # Fallback to SQLite
    self.db_manager = DatabaseManager()
```

#### 5. LINE Bot Integration (`server/server.js`)
- **Webhook Server**: Express.js server for LINE messages
- **Image Processing**: Receives images from LINE, forwards to Google Apps Script
- **Google Drive Storage**: Images stored via GAS to Drive
- **Spreadsheet Logging**: Records uploaded images in spreadsheet
- **ngrok Tunneling**: HTTPS endpoint for local development

#### 6. User Interface (`main_menu.py`)
- **Tkinter GUI**: Main application window with character management
- **Pygame Battle Display**: Real-time battle visualization
- **Character Registration**: Image upload, AI analysis, data entry
- **Battle Management**: Fighter selection, visual mode toggle
- **Statistics Viewer**: Win rates, rankings, battle history
- **Settings Manager**: User preferences, battle speed, sound options

### Google Sheets Structure

The application manages 3 worksheets:

**1. Characters Sheet (14 columns)**
- ID, Name, Image URL, Sprite URL, HP, Attack, Defense, Speed, Magic
- Description, Created At, Wins, Losses, Draws

**2. BattleHistory Sheet (15 columns)**
- Battle ID, Date, Fighter IDs/Names, Winner ID/Name
- Total Turns, Duration, Final HPs, Damage Dealt, Result Type

**3. Rankings Sheet (10 columns)**
- Rank, Character ID/Name, Total Battles, Wins/Losses/Draws
- Win Rate (%), Avg Damage, Rating

All worksheets are automatically created on first run with proper headers.

## Development Guidelines

### Code Style
- **Language**: Python 3.11+ with type hints
- **Naming**: Follow PEP 8, use Japanese for UI text and descriptions
- **Data Validation**: Use Pydantic models for all data structures
- **Error Handling**: Graceful degradation (e.g., online/offline mode fallback)
- **Logging**: Use Python's logging module, not print statements
- **Environment**: All sensitive data in `.env` files (never commit)

### Architecture Patterns
- **Layered Architecture**: Models → Services → UI
- **Dependency Injection**: Services receive dependencies via constructor
- **Single Responsibility**: Each module has one clear purpose
- **Interface Segregation**: Abstract database operations via manager classes

### Testing
Test framework: `pytest` with fixtures in `tests/conftest.py`

Available test suites:
- `tests/test_models.py` - Pydantic model validation
- `tests/test_ai_analyzer.py` - AI analysis mocking
- `tests/test_image_processor.py` - Image processing
- `tests/test_battle_engine.py` - Battle simulation
- `tests/test_database.py` - SQLite database operations
- `tests/test_integration.py` - End-to-end workflows

Run tests:
```bash
pytest tests/
pytest tests/test_battle_engine.py -v  # Specific test file
```

### Key Technical Decisions

**1. Online/Offline Mode Architecture**
- Application detects Google Sheets availability on startup
- Falls back to SQLite without throwing exceptions
- User is notified via status bar
- Critical features work in both modes

**2. Image Storage Strategy**
- Online: Images uploaded to Google Drive, URLs stored in Sheets
- Offline: Images stored locally in `data/characters/` and `data/sprites/`
- Caching: Online mode downloads and caches images locally for performance

**3. Battle Statistics Tracking**
- All battles record detailed statistics (damage, final HP, result type)
- Online mode: Full history and rankings in Google Sheets
- Offline mode: Basic win/loss tracking in SQLite

**4. LINE Bot Integration**
- Decoupled from main application (separate Node.js server)
- Uses Google Apps Script as middleware for Drive uploads
- Optional feature - main app works without it

### Important File Locations

**Configuration:**
- `config/settings.py` - All environment variables and constants
- `.env` - Main application secrets
- `server/.env` - LINE Bot secrets
- `credentials.json` - Google service account (not in git)

**Core Services:**
- `src/services/sheets_manager.py` - Google Sheets/Drive operations (online mode)
- `src/services/database_manager.py` - SQLite operations (offline mode)
- `src/services/battle_engine.py` - Battle simulation logic
- `src/services/ai_analyzer.py` - Google Gemini AI integration
- `src/services/image_processor.py` - Image extraction and sprite processing

**User Interface:**
- `src/ui/main_menu.py` - Main application window (2000+ lines)
- Combines Tkinter (GUI) and Pygame (battle display)

**Data Models:**
- `src/models/character.py` - Character with stats and battle record
- `src/models/battle.py` - Battle with turns and statistics

### Git Workflow
- Main branch: `main`
- Feature branches: Use descriptive names (e.g., `feature/ranking-system`)
- Current working branch: `s1300221`
- Commit messages: Use conventional commits (e.g., `feat:`, `fix:`, `docs:`)

### Security Notes
- ⚠️ **Never commit** API keys, tokens, or credentials to version control
- `.gitignore` excludes: `.env`, `server/.env`, `credentials.json`, `*.db`
- Google API keys: Rotate regularly, restrict by IP/domain in production
- LINE Bot secrets: Use webhook verification in production
- Service account: Limit permissions to only required APIs

### Common Development Tasks

```bash
# Activate development environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Run main application
python main.py

# Run standalone image analysis
python img2txt.py

# Start LINE Bot server (with ngrok)
./server_up.sh

# Install new dependency
pip install <package_name>
pip freeze > requirements.txt

# Run tests
pytest tests/ -v

# Check code style
flake8 src/ tests/
black src/ tests/ --check

# Database inspection (SQLite)
sqlite3 data/database.db
# Example queries:
# SELECT * FROM characters;
# SELECT * FROM battles;
```

### Troubleshooting Common Issues

**Google Sheets Connection Failures:**
1. Check `credentials.json` exists and is valid
2. Verify spreadsheet is shared with service account email
3. Ensure Google Sheets API and Google Drive API are enabled
4. Check `.env` has correct `SPREADSHEET_ID`
5. Application will automatically fall back to offline mode if any fail

**Image Processing Errors:**
- Ensure Pillow and OpenCV are installed: `pip install pillow opencv-python`
- Check image format is supported (PNG, JPG, JPEG)
- Verify image file is not corrupted

**Battle Display Issues:**
- Ensure Pygame is installed: `pip install pygame`
- Check screen resolution supports 1024x768 display
- Verify sprite files exist and are valid PNGs

**LINE Bot Webhook Failures:**
- Verify ngrok is running and HTTPS URL is correct
- Check LINE Developers Console webhook settings
- Ensure `server/.env` has correct channel secret and token
- Test webhook with LINE's "Verify" button

### Performance Considerations

- **Image Caching**: Downloaded images are cached locally to avoid repeated API calls
- **Batch Operations**: Use `bulk_import_characters()` for multiple character imports
- **API Rate Limits**: Google Sheets API has quotas - avoid excessive writes
- **Battle Speed**: Configurable via settings (0.1-2.0 seconds per turn)
- **Database Indexing**: SQLite uses indexes on character IDs for fast lookups

### Future Development Areas

Based on README roadmap:
- [ ] Web version (Flask/FastAPI backend, React frontend)
- [ ] Mobile app (React Native or Flutter)
- [ ] Online multiplayer battles
- [ ] Tournament bracket system
- [ ] Character evolution/leveling system
- [ ] Advanced AI models (GPT-4V, Claude Vision)
- [ ] Character editing UI
- [ ] LINE Bot direct battle commands
- [ ] Real-time battle spectating
- [ ] Character marketplace/sharing

## Platform-Specific Setup

### Windows

**System Requirements:**
- Python 3.11+ (includes Tkinter by default)
- Microsoft C++ Build Tools (for some Python dependencies)
- Node.js 14+ (for LINE Bot server)
- ngrok (for LINE Bot webhook)

**Installation Steps:**
```cmd
REM Activate virtual environment
.venv\Scripts\activate

REM Install Python dependencies
pip install -r requirements.txt

REM For LINE Bot server
cd server
npm install
cd ..
```

**Running the Application:**
```cmd
REM Main application
python main.py

REM LINE Bot server
server_up.bat
```

**Known Issues:**
- **Pygame Audio**: MP3/OGG formats may not work. Use WAV format for sound effects.
- **Path Separators**: Code uses `pathlib.Path` for cross-platform compatibility.
- **Japanese Fonts**: Windows includes MS Gothic/MS Mincho by default.
- **Process Management**: When closing ngrok, manually terminate node.exe:
  ```cmd
  tasklist | findstr node
  taskkill /F /IM node.exe
  ```

### macOS

**System Requirements:**
- Python 3.11+ (includes Tkinter by default)
- Xcode Command Line Tools
- Node.js 14+ (for LINE Bot server)
- ngrok (for LINE Bot webhook)

**Installation Steps:**
```bash
# Install Xcode Command Line Tools (if not already installed)
xcode-select --install

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# For LINE Bot server
cd server
npm install
cd ..
```

**Running the Application:**
```bash
# Main application
python main.py

# LINE Bot server
chmod +x server_up.sh
./server_up.sh
```

**Known Issues:**
- **Japanese Fonts**: macOS includes Hiragino Sans by default.
- **Retina Display**: Pygame may have scaling issues on high-DPI displays.
- **Permissions**: May need to grant Terminal access to files in System Preferences.

### Linux (Ubuntu/Debian)

**System Requirements:**
- Python 3.11+
- Tkinter (not included by default)
- System libraries for OpenCV and graphics
- Japanese fonts (not included by default)
- Node.js 14+ (for LINE Bot server)
- ngrok (for LINE Bot webhook)

**Installation Steps:**
```bash
# Update package manager
sudo apt-get update

# Install system dependencies
sudo apt-get install -y \
    python3-tk \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    fonts-noto-cjk \
    build-essential

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# For LINE Bot server
cd server
npm install
cd ..
```

**Running the Application:**
```bash
# Main application
python main.py

# LINE Bot server
chmod +x server_up.sh
./server_up.sh
```

**Known Issues:**
- **Tkinter Missing**: Install with `sudo apt-get install python3-tk`
- **OpenCV Errors**: Install system libraries:
  ```bash
  sudo apt-get install libgl1-mesa-glx libglib2.0-0
  ```
- **Japanese Font Rendering**: Install Japanese fonts:
  ```bash
  sudo apt-get install fonts-noto-cjk fonts-takao-gothic
  ```
- **Display Issues**: Ensure `$DISPLAY` environment variable is set for GUI applications.

### Cross-Platform Compatibility Notes

**✅ Fully Compatible:**
- Core Python code (uses `pathlib.Path`)
- SQLite database
- Google Sheets/Drive API
- Pydantic models
- Environment variable loading (python-dotenv)

**⚠️ Platform-Specific Considerations:**
- **Audio Formats**: Use WAV for maximum compatibility across all platforms
- **Shell Scripts**:
  - Unix (macOS/Linux): `server_up.sh`
  - Windows: `server_up.bat`
- **File Paths**: Always use `pathlib.Path`, never hardcode `/` or `\`
- **Font Rendering**: Japanese text requires appropriate fonts on each platform
- **OpenCV**: Linux requires additional system libraries

**Testing Across Platforms:**
When developing cross-platform features:
1. Test file path operations with `pathlib.Path`
2. Verify font rendering on target platform
3. Check audio playback compatibility
4. Validate GUI scaling on different DPI settings
5. Test environment variable loading