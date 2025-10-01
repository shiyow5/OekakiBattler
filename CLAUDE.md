# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**お絵描きバトラー (Oekaki Battler)** is a Python-based automatic fighting game that brings hand-drawn characters to life. The workflow involves:

1. **Analog Drawing**: Users draw characters on paper
2. **Digital Capture**: Drawings are scanned/photographed to create digital images
3. **Character Extraction**: AI extracts and processes character sprites from the images
4. **Stat Generation**: Google's Generative AI analyzes character illustrations and generates RPG-style stats (HP, attack, speed) and descriptions
5. **Automated Battle**: Characters fight automatically on screen based on their generated stats - no user control during combat

This creates a unique experience where the artistic style and appearance of hand-drawn characters directly influence their battle performance through AI analysis.

## Development Environment

### Python Environment
- **Python Version**: 3.11+ (based on virtual environment)
- **Virtual Environment**: `.venv/` (already configured)
- **Dependencies**: Managed via `requirements.txt`

### Key Dependencies
```
pillow              # Image processing
google-generativeai # Google Gemini AI integration  
pydantic           # Data validation and parsing
python-dotenv      # Environment variable management
```

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Image-to-Stats Generation
```bash
python img2txt.py
```
This analyzes the `pikachu_modoki.png` image and generates character stats using Google's Gemini model.

### Environment Variables
Required in `.env` file:
- `GOOGLE_API_KEY`: Google Generative AI API key
- `MODEL_NAME`: Gemini model name (currently "gemini-2.5-flash-lite-preview-06-17")

## Code Architecture

### Current Structure
- **`img2txt.py`**: Main AI image analysis module
  - Uses Pydantic models for structured data validation
  - Integrates with Google Generative AI for character stat generation
  - Processes images to generate RPG-style character attributes

### Data Models
- **`ImageDescriptionRequest`**: Pydantic model defining character stats structure
  - `hp`: Health points (0-100)
  - `attack`: Attack power (0-100) 
  - `speed`: Speed stat (0-100)
  - `discription`: Character description in Japanese

### Core System Components

#### 1. Image Processing Pipeline
- **Scanner Integration**: Process scanned drawings from physical paper
- **Character Extraction**: AI-powered sprite extraction from scanned images
- **Image Preprocessing**: Clean and optimize character sprites for battle

#### 2. AI Analysis System
- **Visual Analysis**: Analyze drawing style, character features, and artistic elements
- **Stat Generation**: Convert visual characteristics into battle statistics
- **Character Profiling**: Generate personality and fighting style based on artwork

#### 3. Automated Battle System
- **No User Input**: Battles proceed automatically without player control
- **Stat-Based Combat**: Battle outcomes determined by AI-generated character stats
- **Visual Battle Display**: Real-time combat visualization using extracted character sprites

#### 4. Future Development Goals
Based on README.md references:
- Pygame-based fighting game engine implementation
- Advanced character animation systems
- Multiple battle modes and tournament systems

## Development Guidelines

### Code Style
- Follow Japanese naming conventions where culturally appropriate
- Use Pydantic for data validation and API schemas
- Keep environment-sensitive data in `.env` files
- Structure AI prompts in clear, descriptive Japanese

### Testing
Currently no formal test framework is configured. When adding tests, consider:
- Unit tests for Pydantic model validation
- Integration tests for AI API responses
- Image processing validation tests

### Git Workflow
- Main branch: `main`
- Feature branches: Use descriptive names
- Current working branch: `s1300221`

### Security Notes
- Never commit API keys to version control
- Use `.env` files for sensitive configuration
- Google API keys should be kept secure and rotated regularly

## Common Commands

```bash
# Run the image analysis
python img2txt.py

# Install new dependencies
pip install <package_name>
pip freeze > requirements.txt

# Activate development environment  
source .venv/bin/activate
```