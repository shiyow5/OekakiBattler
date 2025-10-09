"""
Google Sheets manager for character data management with Google Drive integration
"""

import logging
import gspread
import io
import requests
import base64
import uuid
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from PIL import Image
from src.models import Character, Battle
from config.settings import Settings
from src.services.ai_analyzer import AIAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SheetsManager:
    """Manage character data using Google Sheets"""

    def __init__(self):
        self.client = None
        self.sheet = None
        self.worksheet = None
        self.battle_history_sheet = None
        self.ranking_sheet = None
        self.last_id_integrity_check = 0  # Timestamp of last ID integrity check
        self.id_integrity_check_interval = 300  # Check every 5 minutes (300 seconds)
        self.drive_service = None
        self.credentials = None
        self.online_mode = False  # Track if connected to Google Sheets/Drive
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Google Sheets and Google Drive clients"""
        try:
            # Define the scope
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            # Load credentials
            creds_path = Settings.GOOGLE_CREDENTIALS_PATH
            if not creds_path.exists():
                logger.error(f"Google credentials file not found: {creds_path}")
                raise FileNotFoundError(f"Please place your Google credentials JSON file at {creds_path}")

            self.credentials = Credentials.from_service_account_file(str(creds_path), scopes=scope)

            # Initialize Google Sheets client
            self.client = gspread.authorize(self.credentials)

            # Open the spreadsheet
            self.sheet = self.client.open_by_key(Settings.SPREADSHEET_ID)
            self.worksheet = self.sheet.worksheet(Settings.WORKSHEET_NAME)

            # Initialize or create additional worksheets
            self._initialize_worksheets()

            # Initialize Google Drive API client
            self.drive_service = build('drive', 'v3', credentials=self.credentials)

            logger.info(f"Successfully connected to Google Sheets: {Settings.SPREADSHEET_ID}")
            logger.info(f"Successfully connected to Google Drive API")
            self.online_mode = True

        except Exception as e:
            logger.warning(f"Failed to initialize Google Sheets/Drive client: {e}")
            logger.warning("Falling back to offline mode (local database will be used)")
            self.online_mode = False
            # Don't raise exception - allow fallback to local database

    def _initialize_worksheets(self):
        """Initialize or create additional worksheets"""
        try:
            # Get all existing worksheets
            existing_sheets = [ws.title for ws in self.sheet.worksheets()]

            # Create Battle History sheet if it doesn't exist
            if Settings.BATTLE_HISTORY_SHEET not in existing_sheets:
                self.battle_history_sheet = self.sheet.add_worksheet(
                    title=Settings.BATTLE_HISTORY_SHEET,
                    rows=1000,
                    cols=15
                )
                logger.info(f"Created new worksheet: {Settings.BATTLE_HISTORY_SHEET}")
            else:
                self.battle_history_sheet = self.sheet.worksheet(Settings.BATTLE_HISTORY_SHEET)

            # Create Rankings sheet if it doesn't exist
            if Settings.RANKING_SHEET not in existing_sheets:
                self.ranking_sheet = self.sheet.add_worksheet(
                    title=Settings.RANKING_SHEET,
                    rows=100,
                    cols=10
                )
                logger.info(f"Created new worksheet: {Settings.RANKING_SHEET}")
            else:
                self.ranking_sheet = self.sheet.worksheet(Settings.RANKING_SHEET)

            # Initialize StoryBosses and StoryProgress sheets
            self._init_story_sheet()
            self._init_story_progress_sheet()

            # Ensure headers for all sheets
            self._ensure_battle_history_headers()
            self._ensure_ranking_headers()

        except Exception as e:
            logger.error(f"Error initializing worksheets: {e}")

    def _ensure_headers(self):
        """Ensure the spreadsheet has proper headers"""
        try:
            headers = self.worksheet.row_values(1)
            expected_headers = [
                'ID', 'Name', 'Image URL', 'Sprite URL', 'HP', 'Attack',
                'Defense', 'Speed', 'Magic', 'Luck', 'Description', 'Created At',
                'Wins', 'Losses', 'Draws'
            ]

            if not headers or headers != expected_headers:
                self.worksheet.update('A1:O1', [expected_headers])
                logger.info("Headers initialized in spreadsheet")

        except Exception as e:
            logger.error(f"Error ensuring headers: {e}")

    def _ensure_battle_history_headers(self):
        """Ensure the battle history sheet has proper headers"""
        try:
            headers = self.battle_history_sheet.row_values(1) if self.battle_history_sheet else []
            expected_headers = [
                'Battle ID', 'Date', 'Fighter 1 ID', 'Fighter 1 Name', 'Fighter 2 ID', 'Fighter 2 Name',
                'Winner ID', 'Winner Name', 'Total Turns', 'Duration (s)',
                'F1 Final HP', 'F2 Final HP', 'F1 Damage Dealt', 'F2 Damage Dealt', 'Result Type', 'Battle Log'
            ]

            if not headers or headers != expected_headers:
                self.battle_history_sheet.update('A1:P1', [expected_headers])
                logger.info("Battle history headers initialized")

        except Exception as e:
            logger.error(f"Error ensuring battle history headers: {e}")

    def _ensure_ranking_headers(self):
        """Ensure the ranking sheet has proper headers"""
        try:
            headers = self.ranking_sheet.row_values(1) if self.ranking_sheet else []
            expected_headers = [
                'Rank', 'Character ID', 'Character Name', 'Total Battles',
                'Wins', 'Losses', 'Draws', 'Win Rate (%)', 'Avg Damage Dealt', 'Rating'
            ]

            if not headers or headers != expected_headers:
                self.ranking_sheet.update('A1:J1', [expected_headers])
                logger.info("Ranking headers initialized")

        except Exception as e:
            logger.error(f"Error ensuring ranking headers: {e}")

    def upload_to_drive_via_gas(self, file_path: str, file_name: str = None) -> Optional[str]:
        """
        Upload a file to Google Drive via Google Apps Script (uses user's storage quota)

        Args:
            file_path: Local path to the file
            file_name: Optional custom name for the file

        Returns:
            Public URL of the uploaded file, or None if upload failed
        """
        # Check if GAS webhook URL is configured
        if not Settings.GAS_WEBHOOK_URL:
            logger.debug("GAS_WEBHOOK_URL not configured, skipping GAS upload")
            return None

        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return None

            # Use provided file_name or original filename
            if file_name is None:
                file_name = path.name

            # Determine MIME type
            mime_type = 'image/png' if path.suffix.lower() in ['.png'] else 'image/jpeg'

            # Read file and encode to base64
            with open(path, 'rb') as f:
                file_data = f.read()
                b64_data = base64.b64encode(file_data).decode('utf-8')

            # Prepare payload for GAS
            payload = {
                'secret': Settings.GAS_SHARED_SECRET,
                'image': b64_data,
                'mimeType': mime_type,
                'filename': file_name,
                'source': 'python_app'  # Distinguish from LINE bot uploads
            }

            # Send request to GAS
            response = requests.post(
                Settings.GAS_WEBHOOK_URL,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    url = result.get('url')
                    logger.info(f"✓ Successfully uploaded {file_name} via GAS: {url}")
                    return url
                else:
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(f"✗ GAS upload failed: {error_msg}")
                    logger.error(f"  GAS response: {result}")
                    return None
            else:
                logger.error(f"✗ GAS request failed with status {response.status_code}")
                logger.error(f"  Response: {response.text[:200]}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"✗ GAS upload timeout after 30 seconds for {file_name}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"✗ GAS connection error: {e}")
            logger.error(f"  Check if GAS_WEBHOOK_URL is correct: {Settings.GAS_WEBHOOK_URL}")
            return None
        except Exception as e:
            logger.error(f"✗ Failed to upload file via GAS: {e}")
            logger.error(f"  File: {file_path}")
            logger.error(f"  GAS URL: {Settings.GAS_WEBHOOK_URL}")
            return None

    def upload_to_drive(self, file_path: str, file_name: str = None) -> Optional[str]:
        """
        Upload a file to Google Drive via GAS and return its public URL

        Args:
            file_path: Local path to the file
            file_name: Optional custom name for the file

        Returns:
            Public URL of the uploaded file, or None if upload failed (or offline mode)
        """
        # Return None in offline mode (keep local path)
        if not self.online_mode:
            logger.debug("Offline mode: Skipping Drive upload")
            return None

        # Upload via GAS (uses user's storage)
        gas_url = self.upload_to_drive_via_gas(file_path, file_name)
        if gas_url:
            return gas_url
        else:
            logger.error(f"Failed to upload file to Google Drive: {file_path}")
            return None

    def _extract_drive_file_id(self, url: str) -> Optional[str]:
        """
        Extract Google Drive file ID from URL

        Args:
            url: Google Drive URL

        Returns:
            File ID or None if not a valid Drive URL
        """
        if not url or not isinstance(url, str):
            return None

        # Pattern 1: https://drive.google.com/uc?export=view&id=FILE_ID
        if 'drive.google.com/uc' in url and 'id=' in url:
            try:
                file_id = url.split('id=')[1].split('&')[0]
                return file_id
            except Exception:
                pass

        # Pattern 2: https://drive.google.com/file/d/FILE_ID/view
        if 'drive.google.com/file/d/' in url:
            try:
                file_id = url.split('/file/d/')[1].split('/')[0]
                return file_id
            except Exception:
                pass

        # Pattern 3: https://drive.google.com/open?id=FILE_ID
        if 'drive.google.com/open' in url and 'id=' in url:
            try:
                file_id = url.split('id=')[1].split('&')[0]
                return file_id
            except Exception:
                pass

        return None

    def delete_from_drive_via_gas(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive via GAS (Google Apps Script)
        This is necessary when files are owned by the user, not the service account

        Args:
            file_id: Google Drive file ID

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            if not Settings.GAS_WEBHOOK_URL:
                logger.debug("GAS_WEBHOOK_URL not configured")
                return False

            payload = {
                'secret': Settings.GAS_SHARED_SECRET,
                'action': 'delete',
                'fileId': file_id
            }

            logger.info(f"Sending delete request to GAS for file: {file_id}")
            response = requests.post(Settings.GAS_WEBHOOK_URL, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info(f"✓ Successfully deleted file via GAS: {file_id}")
                    return True
                else:
                    logger.warning(f"GAS delete failed: {result.get('error', 'unknown error')}")
                    return False
            else:
                logger.warning(f"GAS request failed with status {response.status_code}")
                return False

        except Exception as e:
            logger.warning(f"Failed to delete via GAS: {e}")
            return False

    def delete_from_drive(self, url: str) -> bool:
        """
        Delete a file from Google Drive using its URL via GAS

        Args:
            url: Google Drive URL of the file to delete

        Returns:
            True if deletion successful, False otherwise
        """
        if not self.online_mode:
            logger.warning("Offline mode: Skipping Drive deletion")
            return False

        try:
            # Extract file ID from URL
            logger.debug(f"Extracting file ID from URL: {url}")
            file_id = self._extract_drive_file_id(url)
            if not file_id:
                logger.warning(f"Could not extract file ID from URL: {url}")
                return False

            logger.info(f"Extracted file ID: {file_id}")

            # Delete via GAS (user's account has permission)
            if self.delete_from_drive_via_gas(file_id):
                logger.info(f"✓ Successfully deleted file from Google Drive: {file_id}")
                return True
            else:
                logger.warning(f"✗ Failed to delete file from Google Drive: {file_id}")
                return False

        except Exception as e:
            logger.error(f"✗ Failed to delete file from Google Drive")
            logger.error(f"  URL: {url}")
            logger.error(f"  Error: {e}")
            return False

    def download_from_url(self, url: str, save_path: str) -> bool:
        """
        Download a file from a URL and save it locally

        Args:
            url: URL of the file (Google Drive or any HTTP URL)
            save_path: Local path to save the file

        Returns:
            True if download succeeded, False otherwise
        """
        try:
            # Convert Google Drive view URLs to direct download URLs
            if 'drive.google.com' in url:
                if '/file/d/' in url:
                    # Extract file ID from share URL
                    file_id = url.split('/file/d/')[1].split('/')[0]
                    url = f"https://drive.google.com/uc?export=download&id={file_id}"
                elif 'id=' in url:
                    # Already in direct download format
                    pass

            # Download file
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Save to file
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Successfully downloaded file from {url} to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download file from {url}: {e}")
            return False

    def save_character(self, character: Character) -> bool:
        """
        Save character to spreadsheet (create new or update existing)

        Args:
            character: Character object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if character already exists by name (since ID format differs)
            # Use silent=True to suppress "not found" warning for new characters
            if character.name:
                existing = self.get_character_by_name(character.name, silent=True)
                if existing:
                    # Update with existing sheet ID
                    character.id = existing.id
                    return self.update_character(character)

            # Create new character
            return self.create_character(character)

        except Exception as e:
            logger.error(f"Error saving character: {e}")
            return False

    def create_character(self, character: Character) -> bool:
        """Create a new character in the spreadsheet with Google Drive upload"""
        try:
            self._ensure_headers()

            # Get next ID
            all_records = self.worksheet.get_all_records()
            next_id = len(all_records) + 1

            # Upload image files to Google Drive if they exist locally
            image_url = character.image_path
            sprite_url = character.sprite_path

            if character.image_path and Path(character.image_path).exists():
                # Upload original image
                uploaded_url = self.upload_to_drive(
                    character.image_path,
                    f"char_{next_id}_original{Path(character.image_path).suffix}"
                )
                if uploaded_url:
                    image_url = uploaded_url
                    logger.info(f"✓ Uploaded original image to Drive: {image_url}")
                else:
                    logger.warning(f"⚠ Failed to upload original image to Drive, using local path: {character.image_path}")

            if character.sprite_path and Path(character.sprite_path).exists():
                # Upload sprite image (always PNG for transparency)
                uploaded_url = self.upload_to_drive(
                    character.sprite_path,
                    f"char_{next_id}_sprite.png"
                )
                if uploaded_url:
                    sprite_url = uploaded_url
                    logger.info(f"✓ Uploaded sprite to Drive: {sprite_url}")
                else:
                    logger.warning(f"⚠ Failed to upload sprite to Drive, using local path: {character.sprite_path}")

            # Prepare row data with Drive URLs
            # Calculate losses and draws from battle_count and win_count
            losses = character.battle_count - character.win_count

            row = [
                next_id,
                character.name,
                image_url or '',
                sprite_url or '',
                character.hp,
                character.attack,
                character.defense,
                character.speed,
                character.magic,
                character.luck,
                character.description or '',
                datetime.now().isoformat(),
                character.win_count,
                losses,
                0  # draws (not tracked in current model)
            ]

            # Append to sheet
            self.worksheet.append_row(row)
            character.id = str(next_id)  # Convert to string to match Character model

            logger.info(f"Character created: {character.name} (ID: {next_id})")
            return True

        except Exception as e:
            logger.error(f"Error creating character: {e}")
            return False

    def get_character(self, character_id) -> Optional[Character]:
        """
        Get a character by ID

        Args:
            character_id: Character ID (int or str that can be converted to int)

        Returns:
            Character object if found, None otherwise
        """
        try:
            # Convert to int if string (for compatibility)
            try:
                char_id = int(character_id) if isinstance(character_id, str) else character_id
            except (ValueError, TypeError):
                logger.warning(f"Invalid character ID format: {character_id}")
                return None

            all_records = self.worksheet.get_all_records()

            for record in all_records:
                if record.get('ID') == char_id:
                    return self._record_to_character(record)

            logger.warning(f"Character not found: ID {char_id}")
            return None

        except Exception as e:
            logger.error(f"Error getting character: {e}")
            return None

    def get_all_characters(self, progress_callback=None) -> List[Character]:
        """Get all characters and generate stats for empty ones

        Args:
            progress_callback: Optional callback function(current, total, char_name, step)
                               to report progress during AI generation and sprite processing
        """
        try:
            # Fix ID integrity before processing (throttled to avoid API quota)
            import time
            current_time = time.time()
            if current_time - self.last_id_integrity_check > self.id_integrity_check_interval:
                logger.info("Running ID integrity check (throttled)...")
                self._fix_id_integrity()
                self.last_id_integrity_check = current_time
            else:
                logger.debug(f"Skipping ID integrity check (last check: {int(current_time - self.last_id_integrity_check)}s ago)")

            # Force fresh data from spreadsheet (avoid cache issues during endless mode)
            # Note: gspread caches worksheet data, so we need to refresh it
            logger.debug("Fetching fresh data from spreadsheet...")
            all_records = self.worksheet.get_all_records()
            logger.debug(f"Retrieved {len(all_records)} records from spreadsheet")

            characters = []

            # First pass: identify characters needing generation or sprite processing
            records_needing_generation = []
            records_needing_sprite = []
            for record in all_records:
                hp_value = record.get('HP')
                name_value = record.get('Name')

                needs_generation = (
                    hp_value == 0 or
                    hp_value == '' or
                    hp_value == '0' or  # Handle string "0" from GAS
                    hp_value is None or
                    name_value == '' or
                    name_value is None or
                    not name_value
                )
                if needs_generation:
                    records_needing_generation.append(record)

                # Check if sprite needs processing (sprite_url == image_url)
                image_url = str(record.get('Image URL', '')) if record.get('Image URL') else None
                sprite_url = str(record.get('Sprite URL', '')) if record.get('Sprite URL') else None
                if sprite_url == image_url and sprite_url and image_url:
                    records_needing_sprite.append(record)

            # Log total characters needing processing
            if records_needing_generation:
                logger.info(f"Found {len(records_needing_generation)} character(s) with empty stats")
            if records_needing_sprite:
                logger.info(f"Found {len(records_needing_sprite)} character(s) needing sprite processing")

            # Second pass: process all records
            generation_count = 0
            sprite_count = 0
            for record in all_records:
                # Check various conditions for needing generation
                hp_value = record.get('HP')
                name_value = record.get('Name')

                # Debug: Log the actual values for troubleshooting
                if hp_value in [0, '', '0', None] or name_value in ['', None]:
                    logger.debug(f"Character ID {record.get('ID')}: HP={repr(hp_value)} (type: {type(hp_value).__name__}), Name={repr(name_value)}")

                needs_generation = (
                    hp_value == 0 or
                    hp_value == '' or
                    hp_value == '0' or  # Handle string "0" from GAS
                    hp_value is None or
                    name_value == '' or
                    name_value is None or
                    not name_value
                )

                if needs_generation:
                    generation_count += 1
                    logger.info(f"Detected character with empty stats: ID {record.get('ID')} (HP={repr(hp_value)}, Name={repr(name_value)})")

                    # Generate stats using AI with progress callback
                    generated_char = self._generate_stats_for_character(
                        record,
                        progress_callback=progress_callback,
                        current=generation_count,
                        total=len(records_needing_generation)
                    )
                    if generated_char:
                        logger.info(f"✓ Successfully generated character: {generated_char.name} (ID: {generated_char.id})")
                        characters.append(generated_char)
                    else:
                        logger.error(f"✗ Failed to generate character for ID {record.get('ID')} - skipping")
                        # Skip this character - it will be retried on next get_all_characters() call
                else:
                    # Check if sprite needs processing
                    image_url = str(record.get('Image URL', '')) if record.get('Image URL') else None
                    sprite_url = str(record.get('Sprite URL', '')) if record.get('Sprite URL') else None
                    needs_sprite = (sprite_url == image_url and sprite_url and image_url)

                    if needs_sprite:
                        sprite_count += 1
                        if progress_callback:
                            progress_callback(
                                sprite_count,
                                len(records_needing_sprite),
                                record.get('Name', f"ID {record.get('ID')}"),
                                "スプライト処理中"
                            )

                    char = self._record_to_character(record, progress_callback=progress_callback if needs_sprite else None)
                    if char:
                        characters.append(char)

            logger.info(f"Retrieved {len(characters)} characters")
            return characters

        except Exception as e:
            logger.error(f"Error getting all characters: {e}")
            return []

    def update_character(self, character: Character) -> bool:
        """Update an existing character"""
        try:
            all_records = self.worksheet.get_all_records()

            # Convert character.id to int for comparison with spreadsheet ID
            try:
                char_id = int(character.id) if isinstance(character.id, str) else character.id
            except (ValueError, TypeError):
                logger.error(f"Invalid character ID format: {character.id}")
                return False

            for idx, record in enumerate(all_records):
                if record.get('ID') == char_id:
                    # Row number in sheet (accounting for header)
                    row_num = idx + 2

                    # Prepare updated row
                    # Calculate losses from battle_count and win_count
                    losses = character.battle_count - character.win_count

                    # Preserve existing Image URL and Sprite URL from the sheet (don't overwrite with local paths)
                    existing_image_url = record.get('Image URL', '')
                    existing_sprite_url = record.get('Sprite URL', '')

                    # Only use character's paths if they are URLs (http/https), otherwise keep existing
                    image_url = existing_image_url
                    sprite_url = existing_sprite_url

                    if character.image_path and (character.image_path.startswith('http://') or character.image_path.startswith('https://')):
                        image_url = character.image_path
                    if character.sprite_path and (character.sprite_path.startswith('http://') or character.sprite_path.startswith('https://')):
                        sprite_url = character.sprite_path

                    row = [
                        character.id,
                        character.name,
                        image_url,  # Preserve existing URL or use new URL (never local path)
                        sprite_url,  # Preserve existing URL or use new URL (never local path)
                        character.hp,
                        character.attack,
                        character.defense,
                        character.speed,
                        character.magic,
                        character.luck,
                        character.description or '',
                        record.get('Created At', ''),  # Keep original creation time
                        character.win_count,
                        losses,
                        0  # draws (not tracked in current model)
                    ]

                    # Update the row
                    self.worksheet.update(f'A{row_num}:O{row_num}', [row])
                    logger.info(f"✓ Character updated: {character.name} (ID: {character.id}) - Image URLs preserved")
                    return True

            logger.warning(f"Character not found for update: ID {character.id}")
            return False

        except Exception as e:
            logger.error(f"Error updating character: {e}")
            return False

    def delete_character(self, character_id: int, force_delete: bool = False) -> bool:
        """
        Delete a character from Google Sheets

        Args:
            character_id: ID of character to delete (int or str)
            force_delete: If True, delete character even if it has battle history

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Convert to int for comparison
            char_id = int(character_id) if isinstance(character_id, str) else character_id

            # Check if character exists in battle history
            battle_count = self.get_character_battle_count(char_id)

            if battle_count > 0 and not force_delete:
                logger.warning(f"Cannot delete character {char_id}: has {battle_count} battle(s) in history. Use force_delete=True to override.")
                return False

            # If force_delete is True and character has battles, delete battle history first
            if force_delete and battle_count > 0 and self.battle_history_sheet:
                logger.info(f"Force deleting character {char_id} with {battle_count} battle(s)")

                # Get all battle history records
                battle_records = self.battle_history_sheet.get_all_records()
                char_id_str = str(char_id)

                # Find and delete rows in reverse order to avoid index shifting
                rows_to_delete = []
                for idx, record in enumerate(battle_records):
                    fighter1_id = str(record.get('Fighter 1 ID', ''))
                    fighter2_id = str(record.get('Fighter 2 ID', ''))

                    if fighter1_id == char_id_str or fighter2_id == char_id_str:
                        # Row number in sheet (accounting for header)
                        row_num = idx + 2
                        rows_to_delete.append(row_num)

                # Delete rows in reverse order to avoid index shifting
                for row_num in sorted(rows_to_delete, reverse=True):
                    self.battle_history_sheet.delete_rows(row_num)

                logger.info(f"Deleted {len(rows_to_delete)} battle history record(s) for character {char_id}")

            # Delete from Rankings sheet if it exists
            if self.ranking_sheet:
                try:
                    ranking_records = self.ranking_sheet.get_all_records()
                    char_id_str = str(char_id)

                    # Find and delete ranking rows in reverse order
                    ranking_rows_to_delete = []
                    for idx, record in enumerate(ranking_records):
                        ranking_char_id = str(record.get('Character ID', ''))

                        if ranking_char_id == char_id_str:
                            # Row number in sheet (accounting for header)
                            row_num = idx + 2
                            ranking_rows_to_delete.append(row_num)

                    # Delete rows in reverse order to avoid index shifting
                    for row_num in sorted(ranking_rows_to_delete, reverse=True):
                        self.ranking_sheet.delete_rows(row_num)

                    if ranking_rows_to_delete:
                        logger.info(f"Deleted {len(ranking_rows_to_delete)} ranking record(s) for character {char_id}")
                except Exception as ranking_e:
                    logger.warning(f"Error deleting from ranking sheet: {ranking_e}")

            # Delete the character from Characters sheet
            all_records = self.worksheet.get_all_records()

            for idx, record in enumerate(all_records):
                if record.get('ID') == char_id:
                    # Get Drive URLs directly from the sheet record (not from character object)
                    # This is important because _record_to_character converts URLs to local paths
                    image_url = str(record.get('Image URL', '')) if record.get('Image URL') else None
                    sprite_url = str(record.get('Sprite URL', '')) if record.get('Sprite URL') else None

                    # Row number in sheet (accounting for header)
                    row_num = idx + 2
                    self.worksheet.delete_rows(row_num)
                    logger.info(f"Character deleted from sheet: ID {char_id}")

                    # Delete images from Google Drive if URLs are available
                    if image_url or sprite_url:
                        logger.info(f"Attempting to delete Drive images for character {char_id}")
                        logger.debug(f"Image URL from sheet: {image_url}")
                        logger.debug(f"Sprite URL from sheet: {sprite_url}")

                        images_deleted = 0

                        # Delete original image from Drive
                        if image_url:
                            if 'drive.google.com' in image_url:
                                logger.info(f"Deleting original image from Drive: {image_url}")
                                if self.delete_from_drive(image_url):
                                    images_deleted += 1
                                    logger.info(f"✓ Deleted original image from Drive for character {char_id}")
                                else:
                                    logger.warning(f"✗ Failed to delete original image from Drive for character {char_id}")
                            else:
                                logger.info(f"Original image is not on Drive (local path): {image_url}")
                        else:
                            logger.info(f"No original image URL for character {char_id}")

                        # Delete sprite image from Drive
                        if sprite_url:
                            if 'drive.google.com' in sprite_url:
                                logger.info(f"Deleting sprite image from Drive: {sprite_url}")
                                if self.delete_from_drive(sprite_url):
                                    images_deleted += 1
                                    logger.info(f"✓ Deleted sprite image from Drive for character {char_id}")
                                else:
                                    logger.warning(f"✗ Failed to delete sprite image from Drive for character {char_id}")
                            else:
                                logger.info(f"Sprite image is not on Drive (local path): {sprite_url}")
                        else:
                            logger.info(f"No sprite URL for character {char_id}")

                        if images_deleted > 0:
                            logger.info(f"Total: Deleted {images_deleted} image(s) from Google Drive for character {char_id}")
                        else:
                            logger.info(f"No Drive images were deleted for character {char_id}")

                    # Delete local cached images
                    local_images_deleted = 0

                    # Delete cached original image
                    cached_original = Settings.CHARACTERS_DIR / f"char_{char_id}_original.png"
                    if cached_original.exists():
                        try:
                            cached_original.unlink()
                            local_images_deleted += 1
                            logger.info(f"✓ Deleted cached original image: {cached_original}")
                        except Exception as e:
                            logger.warning(f"✗ Failed to delete cached original image: {e}")

                    # Also check for .jpg extension
                    cached_original_jpg = Settings.CHARACTERS_DIR / f"char_{char_id}_original.jpg"
                    if cached_original_jpg.exists():
                        try:
                            cached_original_jpg.unlink()
                            local_images_deleted += 1
                            logger.info(f"✓ Deleted cached original image: {cached_original_jpg}")
                        except Exception as e:
                            logger.warning(f"✗ Failed to delete cached original image: {e}")

                    # Delete cached sprite image
                    cached_sprite = Settings.SPRITES_DIR / f"char_{char_id}_sprite.png"
                    if cached_sprite.exists():
                        try:
                            cached_sprite.unlink()
                            local_images_deleted += 1
                            logger.info(f"✓ Deleted cached sprite image: {cached_sprite}")
                        except Exception as e:
                            logger.warning(f"✗ Failed to delete cached sprite image: {e}")

                    if local_images_deleted > 0:
                        logger.info(f"Total: Deleted {local_images_deleted} cached image(s) from local storage")
                    else:
                        logger.debug(f"No cached images found for character {char_id}")

                    return True

            logger.warning(f"Character not found for deletion: ID {char_id}")
            return False

        except Exception as e:
            logger.error(f"Error deleting character: {e}")
            return False

    def update_battle_stats(self, character_id: int, wins: int = 0, losses: int = 0, draws: int = 0) -> bool:
        """Update battle statistics for a character"""
        try:
            character = self.get_character(character_id)
            if not character:
                return False

            # Update battle_count and win_count based on new wins/losses/draws
            character.battle_count += wins + losses + draws
            character.win_count += wins

            return self.update_character(character)

        except Exception as e:
            logger.error(f"Error updating battle stats: {e}")
            return False

    def _record_to_character(self, record: Dict[str, Any], progress_callback=None) -> Optional[Character]:
        """Convert spreadsheet record to Character object with URL support

        Args:
            record: Character record from spreadsheet
            progress_callback: Optional callback for sprite processing progress
        """
        try:
            image_url = str(record.get('Image URL', '')) if record.get('Image URL') else None
            sprite_url = str(record.get('Sprite URL', '')) if record.get('Sprite URL') else None

            # Handle sprite image
            local_sprite_path = Settings.SPRITES_DIR / f"char_{record.get('ID')}_sprite.png"

            # Check if sprite_url is same as image_url (manual registration from LINE/GAS)
            # In this case, sprite has not been processed yet
            sprite_needs_processing = (sprite_url == image_url and sprite_url and image_url)

            if sprite_needs_processing:
                logger.info(f"Character {record.get('ID')}: Sprite URL equals Image URL, needs processing")

            if sprite_url and sprite_url.startswith('http') and not sprite_needs_processing:
                # Sprite URL exists and is different from image URL - download it
                if not local_sprite_path.exists():
                    logger.info(f"Character {record.get('ID')}: Downloading sprite from {sprite_url}")
                    self.download_from_url(sprite_url, str(local_sprite_path))
                sprite_path = str(local_sprite_path) if local_sprite_path.exists() else sprite_url
            elif (sprite_needs_processing or not local_sprite_path.exists()) and image_url and image_url.startswith('http'):
                # Need to create sprite from original image
                logger.info(f"Character {record.get('ID')}: Creating sprite from image URL")
                temp_image_path = Settings.CHARACTERS_DIR / f"char_{record.get('ID')}_temp.png"

                try:
                    # Download original image temporarily
                    if self.download_from_url(image_url, str(temp_image_path)):
                        # Validate downloaded file
                        if not temp_image_path.exists() or temp_image_path.stat().st_size == 0:
                            logger.warning(f"Downloaded file is empty or doesn't exist for character {record.get('ID')}")
                            sprite_path = sprite_url if sprite_url else ''
                        else:
                            # Process image to create sprite with transparency
                            from src.services.image_processor import ImageProcessor
                            processor = ImageProcessor()

                            try:
                                success, message, sprite_output = processor.process_character_image(
                                    str(temp_image_path),
                                    str(Settings.SPRITES_DIR),
                                    f"char_{record.get('ID')}"
                                )

                                if success and sprite_output:
                                    sprite_path = sprite_output
                                    logger.info(f"✓ Created sprite from image URL for character {record.get('ID')}")

                                    # Upload sprite to Google Drive and update sheet
                                    try:
                                        uploaded_sprite_url = self.upload_to_drive(
                                            sprite_output,
                                            f"char_{record.get('ID')}_sprite.png"
                                        )
                                        if uploaded_sprite_url:
                                            # Update Sprite URL in sheet
                                            char_id = int(record.get('ID'))
                                            all_records_for_update = self.worksheet.get_all_records()
                                            for idx, rec in enumerate(all_records_for_update):
                                                if rec.get('ID') == char_id:
                                                    row_num = idx + 2  # +2 for header and 0-indexing
                                                    self.worksheet.update_cell(row_num, 4, uploaded_sprite_url)  # Column 4 is Sprite URL
                                                    logger.info(f"✓ Updated Sprite URL in sheet for character {char_id}")
                                                    break
                                    except Exception as upload_error:
                                        logger.warning(f"Failed to upload sprite to Drive: {upload_error}")
                                else:
                                    logger.warning(f"Failed to create sprite: {message}")
                                    sprite_path = sprite_url if sprite_url else ''
                            except Exception as process_error:
                                logger.error(f"Image processing error for character {record.get('ID')}: {process_error}")
                                sprite_path = sprite_url if sprite_url else ''
                    else:
                        logger.warning(f"Failed to download image for character {record.get('ID')}")
                        sprite_path = sprite_url if sprite_url else ''
                except Exception as e:
                    logger.error(f"Sprite processing failed for character {record.get('ID')}: {e}")
                    sprite_path = sprite_url if sprite_url else ''
                finally:
                    # Clean up temporary file
                    if temp_image_path.exists():
                        try:
                            temp_image_path.unlink()
                        except Exception as cleanup_error:
                            logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
            else:
                sprite_path = sprite_url if sprite_url else str(local_sprite_path) if local_sprite_path.exists() else ''

            # Use URL directly for original image (no local download needed)
            image_path = image_url if image_url else ''

            # Convert wins/losses/draws from spreadsheet to battle_count/win_count
            wins = int(record.get('Wins', 0))
            losses = int(record.get('Losses', 0))
            draws = int(record.get('Draws', 0))
            battle_count = wins + losses + draws
            win_count = wins

            return Character(
                id=str(record.get('ID', 0)),
                name=str(record.get('Name', '')),
                image_path=image_path,
                sprite_path=sprite_path,
                hp=int(record.get('HP', 100)),
                attack=int(record.get('Attack', 50)),
                defense=int(record.get('Defense', 50)),
                speed=int(record.get('Speed', 50)),
                magic=int(record.get('Magic', 50)),
                luck=int(record.get('Luck', 50)),
                description=str(record.get('Description', '')) if record.get('Description') else '',
                battle_count=battle_count,
                win_count=win_count
            )
        except Exception as e:
            logger.error(f"Error converting record to character: {e}")
            return None

    def _generate_stats_for_character(self, record: Dict[str, Any], progress_callback=None, current=1, total=1) -> Optional[Character]:
        """Generate stats for a character with empty stats using AI

        Args:
            record: Character record from spreadsheet
            progress_callback: Optional callback function(current, total, char_name, step)
            current: Current character number being processed
            total: Total number of characters to process
        """
        try:
            char_id = record.get('ID')
            image_url = str(record.get('Image URL', '')) if record.get('Image URL') else None

            logger.info(f"Starting AI generation for character ID {char_id}")
            logger.info(f"  Image URL: {image_url}")

            if not image_url:
                logger.error(f"No image URL found for character {char_id}")
                return None

            # Download image from URL to local cache
            local_path = Settings.CHARACTERS_DIR / f"char_{char_id}_original.png"
            logger.info(f"  Local path: {local_path}")
            logger.info(f"  File exists: {local_path.exists()}")

            if not local_path.exists():
                logger.info(f"Downloading image from {image_url}")
                if progress_callback:
                    progress_callback(current, total, None, "画像をダウンロード中...")

                download_success = self.download_from_url(image_url, str(local_path))
                if download_success:
                    logger.info(f"✓ Image downloaded successfully to {local_path}")
                else:
                    logger.error(f"✗ Failed to download image for character {char_id}")
            else:
                logger.info(f"Using existing local image: {local_path}")

            if not local_path.exists():
                logger.error(f"Failed to download image for character {char_id}")
                return None

            # Use AI analyzer to generate stats BEFORE sprite processing
            # (AI analysis needs the original image)
            logger.info(f"Generating stats using AI for character {char_id}...")
            if progress_callback:
                progress_callback(current, total, None, "AIが画像を分析中...")

            ai_analyzer = AIAnalyzer()
            char_stats = ai_analyzer.analyze_character(str(local_path))

            if not char_stats:
                logger.error(f"✗ AI analysis failed for character {char_id}")
                return None

            logger.info(f"✓ AI analysis completed: {char_stats.name} (HP:{char_stats.hp}, ATK:{char_stats.attack}, DEF:{char_stats.defense}, SPD:{char_stats.speed}, MAG:{char_stats.magic}, LCK:{char_stats.luck})")

            # Process image to create sprite with transparency
            logger.info(f"Processing image to create sprite for character {char_id}...")
            if progress_callback:
                progress_callback(current, total, char_stats.name, "スプライトを作成中...")

            from src.services.image_processor import ImageProcessor
            image_processor = ImageProcessor()

            # Create sprite with transparency
            sprite_path = None
            sprite_url = None
            success, message, sprite_output = image_processor.process_character_image(
                str(local_path),
                str(Settings.SPRITES_DIR),
                f"char_{char_id}"
            )

            if success and sprite_output:
                sprite_path = sprite_output
                logger.info(f"✓ Created sprite with transparency: {sprite_path}")

                # Upload sprite to Google Drive
                logger.info(f"Uploading sprite to Google Drive for character {char_id}...")
                if progress_callback:
                    progress_callback(current, total, char_stats.name, "スプライトをアップロード中...")

                sprite_url = self.upload_to_drive(sprite_path, f"char_{char_id}_sprite.png")
                if sprite_url:
                    logger.info(f"✓ Uploaded sprite to Drive: {sprite_url}")
                else:
                    logger.warning(f"Failed to upload sprite to Drive, using local path")
                    sprite_url = sprite_path

                # Delete original image after sprite creation (no longer needed locally)
                try:
                    if local_path.exists():
                        local_path.unlink()
                        logger.info(f"✓ Deleted original image after sprite creation: {local_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete original image: {e}")
            else:
                logger.warning(f"Failed to create sprite: {message}, using original image")
                sprite_path = str(local_path)
                sprite_url = image_url  # Use existing image URL

            # Create a Character object from the CharacterStats
            from src.models.character import Character

            # For battle display, we need local sprite path
            # sprite_path should be the local file path, not the URL
            # If sprite creation succeeded, sprite_path is already the local path
            # If it failed, use local_path as fallback
            final_sprite_path = sprite_path if sprite_path else str(local_path)

            analyzed_char = Character(
                id=str(char_id),
                name=char_stats.name,
                hp=char_stats.hp,
                attack=char_stats.attack,
                defense=char_stats.defense,
                speed=char_stats.speed,
                magic=char_stats.magic,
                description=char_stats.description,
                image_path=image_url,  # Use original image URL for reference
                sprite_path=final_sprite_path  # Use local sprite path for battle display
            )

            # Update the spreadsheet with generated stats and sprite URL
            logger.info(f"Updating spreadsheet with generated stats for character {char_id}")
            if progress_callback:
                progress_callback(current, total, analyzed_char.name, "スプレッドシートを更新中...")

            self._update_character_stats_in_sheet(char_id, analyzed_char, sprite_url)

            logger.info(f"✓ Successfully generated stats for character '{analyzed_char.name}' (ID: {char_id})")
            if progress_callback:
                progress_callback(current, total, analyzed_char.name, "✓ 完了")

            return analyzed_char

        except Exception as e:
            logger.error(f"✗ Error generating stats for character ID {record.get('ID')}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def _update_character_stats_in_sheet(self, char_id: int, character: Character, sprite_url: str = None) -> bool:
        """Update character stats in spreadsheet using batch update for efficiency

        Args:
            char_id: Character ID
            character: Character object with stats
            sprite_url: Optional sprite URL to update (if None, preserve existing)
        """
        try:
            all_records = self.worksheet.get_all_records()

            for idx, record in enumerate(all_records):
                if record.get('ID') == char_id:
                    row_num = idx + 2  # +2 because of header row and 0-indexing

                    # Get existing Image URL and Sprite URL (don't overwrite them unless specified)
                    existing_image_url = record.get('Image URL', '')
                    existing_sprite_url = record.get('Sprite URL', '')

                    # Use provided sprite_url if available, otherwise preserve existing
                    final_sprite_url = sprite_url if sprite_url else existing_sprite_url

                    # Use update() with range to update multiple cells at once
                    # Columns: B=Name, C=Image URL, D=Sprite URL, E=HP, F=Attack, G=Defense, H=Speed, I=Magic, J=Luck, K=Description
                    cell_range = f'B{row_num}:K{row_num}'
                    values = [[
                        character.name,           # B: Name
                        existing_image_url,       # C: Image URL (preserve existing)
                        final_sprite_url,         # D: Sprite URL (use new if provided, otherwise preserve)
                        character.hp,             # E: HP
                        character.attack,         # F: Attack
                        character.defense,        # G: Defense
                        character.speed,          # H: Speed
                        character.magic,          # I: Magic
                        character.luck,           # J: Luck
                        character.description     # K: Description
                    ]]

                    # Use update() with range for batch update (single API call)
                    self.worksheet.update(cell_range, values, value_input_option='USER_ENTERED')

                    logger.info(f"✓ Updated stats in spreadsheet for character {char_id} (Name: {character.name})")
                    if sprite_url:
                        logger.info(f"✓ Updated sprite URL: {sprite_url}")
                    return True

            logger.warning(f"Character not found in spreadsheet: ID {char_id}")
            return False

        except Exception as e:
            logger.error(f"Error updating character stats in sheet: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def get_character_by_name(self, name: str, silent: bool = False) -> Optional[Character]:
        """
        Get a character by name

        Args:
            name: Character name to search for
            silent: If True, suppress "not found" warning (useful for existence checks)

        Returns:
            Character object if found, None otherwise
        """
        try:
            all_records = self.worksheet.get_all_records()

            for record in all_records:
                if record.get('Name') == name:
                    return self._record_to_character(record)

            if not silent:
                logger.warning(f"Character not found: {name}")
            return None

        except Exception as e:
            logger.error(f"Error getting character by name: {e}")
            return None

    def search_characters(self, query: str) -> List[Character]:
        """Search characters by name"""
        try:
            all_characters = self.get_all_characters()
            return [char for char in all_characters if query.lower() in char.name.lower()]
        except Exception as e:
            logger.error(f"Error searching characters: {e}")
            return []

    def get_character_count(self) -> int:
        """Get total number of characters"""
        try:
            all_records = self.worksheet.get_all_records()
            return len(all_records)
        except Exception as e:
            logger.error(f"Error getting character count: {e}")
            return 0

    def bulk_import_characters(self) -> List[Character]:
        """
        Import all characters from spreadsheet in bulk
        More efficient than calling get_all_characters() repeatedly

        Returns:
            List of Character objects
        """
        try:
            logger.info("Starting bulk import of characters...")
            all_records = self.worksheet.get_all_records()
            characters = []

            for record in all_records:
                char = self._record_to_character(record)
                if char:
                    characters.append(char)

            logger.info(f"Bulk import completed: {len(characters)} characters imported")
            return characters

        except Exception as e:
            logger.error(f"Error during bulk import: {e}")
            return []

    def record_battle_history(self, battle_data: Dict[str, Any]) -> bool:
        """
        Record battle results to the BattleHistory sheet

        Args:
            battle_data: Dictionary containing battle information
                Required keys: fighter1_id, fighter1_name, fighter2_id, fighter2_name,
                              winner_id, winner_name, total_turns, duration,
                              f1_final_hp, f2_final_hp, f1_damage_dealt, f2_damage_dealt, result_type

        Returns:
            True if successful, False otherwise (or offline mode)
        """
        # Skip in offline mode
        if not self.online_mode:
            logger.debug("Offline mode: Skipping battle history recording")
            return False

        try:
            if not self.battle_history_sheet:
                logger.error("Battle history sheet not initialized")
                return False

            # Get next battle ID
            all_records = self.battle_history_sheet.get_all_records()
            next_battle_id = len(all_records) + 1

            # Prepare battle log (join with newlines for readability)
            battle_log = battle_data.get('battle_log', [])
            battle_log_str = '\n'.join(battle_log) if battle_log else ''

            # Prepare row data
            row = [
                next_battle_id,
                datetime.now().isoformat(),
                battle_data.get('fighter1_id', ''),
                battle_data.get('fighter1_name', ''),
                battle_data.get('fighter2_id', ''),
                battle_data.get('fighter2_name', ''),
                battle_data.get('winner_id', ''),
                battle_data.get('winner_name', ''),
                battle_data.get('total_turns', 0),
                battle_data.get('duration', 0.0),
                battle_data.get('f1_final_hp', 0),
                battle_data.get('f2_final_hp', 0),
                battle_data.get('f1_damage_dealt', 0),
                battle_data.get('f2_damage_dealt', 0),
                battle_data.get('result_type', 'Unknown'),
                battle_log_str
            ]

            # Append to sheet
            self.battle_history_sheet.append_row(row)
            logger.info(f"Battle history recorded: Battle ID {next_battle_id}")
            return True

        except Exception as e:
            logger.error(f"Error recording battle history: {e}")
            return False

    def get_battle_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get battle history records

        Args:
            limit: Maximum number of records to return (most recent). None for all records.

        Returns:
            List of battle history dictionaries
        """
        try:
            if not self.battle_history_sheet:
                logger.warning("Battle history sheet not initialized")
                return []

            all_records = self.battle_history_sheet.get_all_records()

            if limit:
                # Return most recent records
                return all_records[-limit:]

            return all_records

        except Exception as e:
            logger.error(f"Error getting battle history: {e}")
            return []

    def update_rankings(self) -> bool:
        """
        Update the Rankings sheet based on current character statistics
        Automatically calculates win rates, ratings, and sorts by performance

        Returns:
            True if successful, False otherwise (or offline mode)
        """
        # Skip in offline mode
        if not self.online_mode:
            logger.debug("Offline mode: Skipping rankings update")
            return False

        try:
            if not self.ranking_sheet:
                logger.error("Rankings sheet not initialized")
                return False

            # Get all characters
            characters = self.get_all_characters()

            if not characters:
                logger.warning("No characters to rank")
                return False

            # Calculate rankings
            rankings = []
            for char in characters:
                # Convert from battle_count/win_count to wins/losses/draws format
                total_battles = char.battle_count
                wins = char.win_count
                losses = char.battle_count - char.win_count  # Assume no draws in current model
                draws = 0

                win_rate = (wins / total_battles * 100) if total_battles > 0 else 0

                # Calculate rating (simple formula: wins * 3 + draws * 1)
                rating = wins * 3 + draws * 1

                # Get average damage from battle history
                avg_damage = self._calculate_avg_damage(char.id)

                rankings.append({
                    'char_id': char.id,
                    'name': char.name,
                    'total_battles': total_battles,
                    'wins': wins,
                    'losses': losses,
                    'draws': draws,
                    'win_rate': round(win_rate, 2),
                    'avg_damage': round(avg_damage, 2),
                    'rating': rating
                })

            # Sort by rating (descending), then by win rate
            rankings.sort(key=lambda x: (x['rating'], x['win_rate']), reverse=True)

            # Clear existing rankings (except header)
            self.ranking_sheet.clear()
            self._ensure_ranking_headers()

            # Prepare rows for batch update
            rows = []
            for rank, entry in enumerate(rankings, start=1):
                row = [
                    rank,
                    entry['char_id'],
                    entry['name'],
                    entry['total_battles'],
                    entry['wins'],
                    entry['losses'],
                    entry['draws'],
                    entry['win_rate'],
                    entry['avg_damage'],
                    entry['rating']
                ]
                rows.append(row)

            # Batch update all rows at once
            if rows:
                self.ranking_sheet.update(f'A2:J{len(rows) + 1}', rows)

            logger.info(f"Rankings updated: {len(rankings)} characters ranked")
            return True

        except Exception as e:
            logger.error(f"Error updating rankings: {e}")
            return False

    def _calculate_avg_damage(self, character_id: int) -> float:
        """Calculate average damage dealt by a character from battle history"""
        try:
            if not self.battle_history_sheet:
                return 0.0

            all_records = self.battle_history_sheet.get_all_records()
            total_damage = 0
            battle_count = 0

            for record in all_records:
                if record.get('Fighter 1 ID') == character_id:
                    total_damage += record.get('F1 Damage Dealt', 0)
                    battle_count += 1
                elif record.get('Fighter 2 ID') == character_id:
                    total_damage += record.get('F2 Damage Dealt', 0)
                    battle_count += 1

            return total_damage / battle_count if battle_count > 0 else 0.0

        except Exception as e:
            logger.error(f"Error calculating average damage: {e}")
            return 0.0

    def get_rankings(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get current rankings

        Args:
            limit: Maximum number of rankings to return. None for all.

        Returns:
            List of ranking dictionaries
        """
        try:
            if not self.ranking_sheet:
                logger.warning("Rankings sheet not initialized")
                return []

            all_records = self.ranking_sheet.get_all_records()

            if limit:
                return all_records[:limit]

            return all_records

        except Exception as e:
            logger.error(f"Error getting rankings: {e}")
            return []

    def update_character_stats(self, character_id: str, won: bool) -> bool:
        """
        Update character battle statistics

        Args:
            character_id: Character ID (string or int)
            won: True if character won, False if lost

        Returns:
            True if successful, False otherwise
        """
        try:
            character = self.get_character(character_id)
            if not character:
                logger.warning(f"Character not found for stats update: {character_id}")
                return False

            # Update stats
            character.battle_count += 1
            if won:
                character.win_count += 1

            # Save updated character
            return self.update_character(character)

        except Exception as e:
            logger.error(f"Error updating character stats: {e}")
            return False

    def save_battle(self, battle: Battle) -> bool:
        """
        Save battle to Google Sheets (via battle history) and update character stats

        Args:
            battle: Battle object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # In online mode, battle history is recorded via record_battle_history()
            # This method is provided for compatibility with DatabaseManager interface
            if not self.online_mode:
                logger.debug("Offline mode: Skipping battle save")
                return False

            # Update character stats (similar to DatabaseManager)
            if battle.character1_id and battle.character2_id:
                self.update_character_stats(battle.character1_id, battle.winner_id == battle.character1_id)
                self.update_character_stats(battle.character2_id, battle.winner_id == battle.character2_id)

            # Battle history is already recorded in the calling code
            logger.debug(f"Battle {battle.id} saved and character stats updated")
            return True

        except Exception as e:
            logger.error(f"Error saving battle: {e}")
            return False

    def get_recent_battles(self, limit: int = 10) -> List[Battle]:
        """
        Get recent battles from battle history
        Converts battle history records to Battle objects for UI compatibility

        Args:
            limit: Maximum number of battles to return

        Returns:
            List of Battle objects constructed from battle history
        """
        try:
            if not self.online_mode or not self.battle_history_sheet:
                logger.debug("Offline mode or battle history not available")
                return []

            # Get battle history records
            battle_records = self.get_battle_history(limit=limit)

            battles = []
            for record in battle_records:
                try:
                    # Parse date
                    try:
                        if isinstance(record.get('Date'), str):
                            created_at = datetime.fromisoformat(record.get('Date'))
                        else:
                            created_at = datetime.now()
                    except Exception:
                        created_at = datetime.now()

                    # Construct Battle object from history record
                    # Keep IDs as strings for Battle model compatibility
                    fighter1_id = record.get('Fighter 1 ID', '')
                    fighter2_id = record.get('Fighter 2 ID', '')
                    winner_id_raw = record.get('Winner ID', '')

                    # Parse battle log (split by newlines)
                    battle_log_str = record.get('Battle Log', '')
                    battle_log = battle_log_str.split('\n') if battle_log_str else []

                    # Get total turns from record
                    total_turns = int(record.get('Total Turns', 0))

                    # Create dummy turns to preserve turn count
                    # (actual turn details are not stored in battle history)
                    from src.models.battle import BattleTurn
                    dummy_turns = []
                    for i in range(total_turns):
                        dummy_turn = BattleTurn(
                            turn_number=i + 1,
                            attacker_id=str(fighter1_id) if i % 2 == 0 else str(fighter2_id),
                            defender_id=str(fighter2_id) if i % 2 == 0 else str(fighter1_id),
                            action_type="unknown",
                            damage=0,
                            attacker_hp_after=0,
                            defender_hp_after=0
                        )
                        dummy_turns.append(dummy_turn)

                    battle = Battle(
                        id=str(record.get('Battle ID', str(uuid.uuid4()))),
                        character1_id=str(fighter1_id) if fighter1_id else '',
                        character2_id=str(fighter2_id) if fighter2_id else '',
                        winner_id=str(winner_id_raw) if winner_id_raw else None,
                        duration=float(record.get('Duration (s)', 0)),
                        created_at=created_at,
                        char1_final_hp=int(record.get('F1 Final HP', 0)),
                        char2_final_hp=int(record.get('F2 Final HP', 0)),
                        char1_damage_dealt=int(record.get('F1 Damage Dealt', 0)),
                        char2_damage_dealt=int(record.get('F2 Damage Dealt', 0)),
                        result_type=str(record.get('Result Type', 'Unknown')),
                        battle_log=battle_log,  # Load from battle history
                        turns=dummy_turns  # Dummy turns to preserve turn count
                    )
                    battles.append(battle)

                except Exception as parse_e:
                    logger.warning(f"Error parsing battle history record: {parse_e}")
                    continue

            logger.info(f"Retrieved {len(battles)} battles from battle history")
            return battles

        except Exception as e:
            logger.error(f"Error getting recent battles: {e}")
            return []

    def get_character_battle_count(self, character_id: str) -> int:
        """
        Get the number of battles a character has participated in

        Args:
            character_id: Character ID (string or int)

        Returns:
            Number of battles the character has participated in
        """
        try:
            if not self.online_mode or not self.battle_history_sheet:
                logger.debug("Offline mode or battle history not available")
                return 0

            # Get all battle history records
            battle_records = self.battle_history_sheet.get_all_records()

            # Convert character_id to string for comparison
            char_id_str = str(character_id)

            # Count battles where this character participated
            battle_count = 0
            for record in battle_records:
                fighter1_id = str(record.get('Fighter 1 ID', ''))
                fighter2_id = str(record.get('Fighter 2 ID', ''))

                if fighter1_id == char_id_str or fighter2_id == char_id_str:
                    battle_count += 1

            logger.debug(f"Character {character_id} has {battle_count} battles")
            return battle_count

        except Exception as e:
            logger.error(f"Error getting battle count for character {character_id}: {e}")
            return 0

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics from Google Sheets

        Returns:
            Dictionary with statistics (characters, battles, rankings)
        """
        try:
            stats = {}

            # Character statistics
            characters = self.get_all_characters()
            stats['total_characters'] = len(characters)

            # Battle statistics from battle history
            if self.battle_history_sheet:
                battle_records = self.battle_history_sheet.get_all_records()
                stats['total_battles'] = len(battle_records)
            else:
                stats['total_battles'] = 0

            # Average character stats
            if characters:
                avg_hp = sum(c.hp for c in characters) / len(characters)
                avg_attack = sum(c.attack for c in characters) / len(characters)
                avg_defense = sum(c.defense for c in characters) / len(characters)
                avg_speed = sum(c.speed for c in characters) / len(characters)
                avg_magic = sum(c.magic for c in characters) / len(characters)

                stats['average_stats'] = {
                    'hp': round(avg_hp, 1),
                    'attack': round(avg_attack, 1),
                    'defense': round(avg_defense, 1),
                    'speed': round(avg_speed, 1),
                    'magic': round(avg_magic, 1)
                }
            else:
                stats['average_stats'] = {
                    'hp': 0, 'attack': 0, 'defense': 0, 'speed': 0, 'magic': 0
                }

            # Top performing characters
            top_characters = []
            for char in characters:
                if char.battle_count > 0:
                    win_rate = (char.win_count / char.battle_count * 100)
                    top_characters.append({
                        'name': char.name,
                        'win_count': char.win_count,
                        'battle_count': char.battle_count,
                        'win_rate': round(win_rate, 1)
                    })

            # Sort by win rate, then by win count
            top_characters.sort(key=lambda x: (x['win_rate'], x['win_count']), reverse=True)
            stats['top_characters'] = top_characters[:5]

            return stats

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                'total_characters': 0,
                'total_battles': 0,
                'average_stats': {'hp': 0, 'attack': 0, 'defense': 0, 'speed': 0, 'magic': 0},
                'top_characters': []
            }

    # ========== Story Mode Methods ==========

    def get_story_boss(self, level: int):
        """Get story boss by level"""
        try:
            from src.models.story_boss import StoryBoss

            if not hasattr(self, 'story_sheet') or self.story_sheet is None:
                self._init_story_sheet()

            if not self.story_sheet:
                logger.warning("Story sheet is not available (offline mode or initialization failed)")
                return None

            logger.info(f"Getting story boss Lv{level}...")
            records = self.story_sheet.get_all_records()
            logger.info(f"Found {len(records)} records in StoryBosses sheet")
            
            for record in records:
                if record.get('Level') == level:
                    logger.info(f"Found matching record: {record}")
                    image_url = str(record.get('Image URL', '')) if record.get('Image URL') else ''
                    sprite_url = str(record.get('Sprite URL', '')) if record.get('Sprite URL') else ''

                    # Download sprite if it's a URL
                    sprite_path = sprite_url
                    if sprite_url and sprite_url.startswith('http'):
                        local_sprite = Settings.SPRITES_DIR / f"boss_lv{level}_sprite.png"
                        if not local_sprite.exists():
                            self.download_from_url(sprite_url, str(local_sprite))
                        if local_sprite.exists():
                            sprite_path = str(local_sprite)

                    return StoryBoss(
                        level=level,
                        name=record.get('Name', f'Boss Lv{level}'),
                        hp=int(record.get('HP', 100)),
                        attack=int(record.get('Attack', 50)),
                        defense=int(record.get('Defense', 50)),
                        speed=int(record.get('Speed', 50)),
                        magic=int(record.get('Magic', 50)),
                        luck=int(record.get('Luck', 50)),
                        description=record.get('Description', ''),
                        image_path=image_url,
                        sprite_path=sprite_path
                    )
            
            logger.info(f"No boss found for Lv{level}")
            return None

        except Exception as e:
            logger.error(f"Error getting story boss: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def save_story_boss(self, boss) -> bool:
        """Save or update story boss"""
        try:
            from src.models.story_boss import StoryBoss

            if not hasattr(self, 'story_sheet') or self.story_sheet is None:
                self._init_story_sheet()

            if not self.story_sheet:
                logger.error("Story sheet is not available (offline mode or initialization failed)")
                return False

            records = self.story_sheet.get_all_records()

            # Check if boss already exists
            for idx, record in enumerate(records):
                if record.get('Level') == boss.level:
                    # Update existing boss
                    row_num = idx + 2
                    values = [[
                        boss.level,
                        boss.name,
                        boss.image_path or '',
                        boss.sprite_path or '',
                        boss.hp,
                        boss.attack,
                        boss.defense,
                        boss.speed,
                        boss.magic,
                        boss.luck,
                        boss.description
                    ]]
                    self.story_sheet.update(f'A{row_num}:K{row_num}', values)
                    logger.info(f"Updated story boss Lv{boss.level}: HP={boss.hp}, ATK={boss.attack}, DEF={boss.defense}, SPD={boss.speed}, MAG={boss.magic}, LCK={boss.luck}")
                    return True

            # Add new boss
            row_values = [
                boss.level,
                boss.name,
                boss.image_path or '',
                boss.sprite_path or '',
                boss.hp,
                boss.attack,
                boss.defense,
                boss.speed,
                boss.magic,
                boss.luck,
                boss.description
            ]
            self.story_sheet.append_row(row_values)
            logger.info(f"Added new story boss Lv{boss.level}: HP={boss.hp}, ATK={boss.attack}, DEF={boss.defense}, SPD={boss.speed}, MAG={boss.magic}, LCK={boss.luck}")
            return True

        except Exception as e:
            logger.error(f"Error saving story boss: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def get_story_progress(self, character_id: str):
        """Get story mode progress for a character"""
        try:
            from src.models.story_boss import StoryProgress
            from datetime import datetime

            if not hasattr(self, 'story_progress_sheet') or self.story_progress_sheet is None:
                self._init_story_progress_sheet()

            if not self.story_progress_sheet:
                logger.warning("Story progress sheet is not available (offline mode or initialization failed)")
                return None

            # Use expected_headers to handle duplicate header values
            expected_headers = ['Character ID', 'Current Level', 'Completed', 'EndlessAccess', 'Victories', 'Attempts', 'Last Played']
            records = self.story_progress_sheet.get_all_records(expected_headers=expected_headers)
            for record in records:
                if str(record.get('Character ID')) == str(character_id):
                    victories = []
                    victories_str = record.get('Victories', '')
                    if victories_str:
                        # Handle both string and integer values, skip non-numeric values
                        if isinstance(victories_str, str):
                            # Skip boolean strings like 'TRUE' or 'FALSE'
                            if victories_str.upper() not in ['TRUE', 'FALSE', '']:
                                try:
                                    victories = [int(x.strip()) for x in victories_str.split(',') if x.strip() and x.strip().upper() not in ['TRUE', 'FALSE']]
                                except ValueError as e:
                                    logger.warning(f"Could not parse victories string: {victories_str}, error: {e}")
                                    victories = []
                        elif isinstance(victories_str, int):
                            victories = [victories_str] if victories_str > 0 else []

                    # Parse attempts field safely
                    attempts = 0
                    attempts_value = record.get('Attempts', 0)
                    try:
                        if isinstance(attempts_value, str) and attempts_value.upper() in ['TRUE', 'FALSE', '']:
                            attempts = 0
                        else:
                            attempts = int(attempts_value)
                    except (ValueError, TypeError):
                        logger.warning(f"Could not parse attempts value: {attempts_value}")
                        attempts = 0

                    return StoryProgress(
                        character_id=str(character_id),
                        current_level=int(record.get('Current Level', 1)),
                        completed=record.get('Completed', 'FALSE') == 'TRUE',
                        endless_access=record.get('EndlessAccess', 'FALSE') == 'TRUE',
                        victories=victories,
                        attempts=attempts,
                        last_played=datetime.fromisoformat(record.get('Last Played', datetime.now().isoformat()))
                    )
            return None

        except Exception as e:
            logger.error(f"Error getting story progress: {e}")
            return None

    def save_story_progress(self, progress) -> bool:
        """Save story mode progress"""
        try:
            from datetime import datetime

            if not hasattr(self, 'story_progress_sheet') or self.story_progress_sheet is None:
                self._init_story_progress_sheet()

            if not self.story_progress_sheet:
                logger.error("Story progress sheet is not available (offline mode or initialization failed)")
                return False

            # Use expected_headers to handle duplicate header values
            expected_headers = ['Character ID', 'Current Level', 'Completed', 'EndlessAccess', 'Victories', 'Attempts', 'Last Played']
            records = self.story_progress_sheet.get_all_records(expected_headers=expected_headers)
            victories_str = ','.join([str(v) for v in progress.victories])

            # Check if progress already exists
            for idx, record in enumerate(records):
                if str(record.get('Character ID')) == str(progress.character_id):
                    # Update existing progress
                    row_num = idx + 2
                    values = [[
                        progress.character_id,
                        progress.current_level,
                        'TRUE' if progress.completed else 'FALSE',
                        'TRUE' if progress.endless_access else 'FALSE',
                        victories_str,
                        progress.attempts,
                        datetime.now().isoformat()
                    ]]
                    self.story_progress_sheet.update(f'A{row_num}:G{row_num}', values)
                    logger.info(f"Updated story progress for character {progress.character_id}")
                    return True

            # Add new progress
            values = [[
                progress.character_id,
                progress.current_level,
                'TRUE' if progress.completed else 'FALSE',
                'TRUE' if progress.endless_access else 'FALSE',
                victories_str,
                progress.attempts,
                datetime.now().isoformat()
            ]]
            self.story_progress_sheet.append_row(values[0])
            logger.info(f"Added new story progress for character {progress.character_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving story progress: {e}")
            return False

    def _init_story_sheet(self):
        """Initialize story bosses worksheet"""
        try:
            if not self.online_mode or not hasattr(self, 'sheet') or self.sheet is None:
                self.story_sheet = None
                return

            try:
                self.story_sheet = self.sheet.worksheet("StoryBosses")
                logger.info("StoryBosses sheet found")
                
                # Verify and fix headers if needed
                self._ensure_story_sheet_headers()
                
            except:
                # Create the sheet if it doesn't exist
                self.story_sheet = self.sheet.add_worksheet(title="StoryBosses", rows=100, cols=11)
                headers = ['Level', 'Name', 'Image URL', 'Sprite URL', 'HP', 'Attack', 'Defense', 'Speed', 'Magic', 'Luck', 'Description']
                self.story_sheet.update('A1:K1', [headers])
                logger.info("Created StoryBosses sheet")

        except Exception as e:
            logger.error(f"Error initializing story sheet: {e}")
            self.story_sheet = None
    
    def _ensure_story_sheet_headers(self):
        """Ensure StoryBosses sheet has correct headers"""
        try:
            if not self.story_sheet:
                return
            
            expected_headers = ['Level', 'Name', 'Image URL', 'Sprite URL', 'HP', 'Attack', 'Defense', 'Speed', 'Magic', 'Luck', 'Description']
            current_headers = self.story_sheet.row_values(1)
            
            # Check if headers are correct
            if current_headers != expected_headers:
                logger.warning(f"StoryBosses headers incorrect. Current: {current_headers}")
                logger.info(f"Fixing StoryBosses headers to: {expected_headers}")
                self.story_sheet.update('A1:K1', [expected_headers])
                logger.info("StoryBosses headers updated successfully")
            else:
                logger.info("StoryBosses headers are correct")
        
        except Exception as e:
            logger.error(f"Error ensuring story sheet headers: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _init_story_progress_sheet(self):
        """Initialize story progress worksheet"""
        try:
            if not self.online_mode or not hasattr(self, 'sheet') or self.sheet is None:
                self.story_progress_sheet = None
                return

            try:
                self.story_progress_sheet = self.sheet.worksheet("StoryProgress")
                logger.info("StoryProgress sheet found")

                # Verify and fix headers if needed
                self._ensure_story_progress_headers()

            except:
                # Create the sheet if it doesn't exist
                self.story_progress_sheet = self.sheet.add_worksheet(title="StoryProgress", rows=1000, cols=7)
                headers = ['Character ID', 'Current Level', 'Completed', 'EndlessAccess', 'Victories', 'Attempts', 'Last Played']
                self.story_progress_sheet.update('A1:G1', [headers])
                logger.info("Created StoryProgress sheet")

        except Exception as e:
            logger.error(f"Error initializing story progress sheet: {e}")
            self.story_progress_sheet = None

    def _ensure_story_progress_headers(self):
        """Ensure StoryProgress sheet has correct headers"""
        try:
            if not self.story_progress_sheet:
                return

            expected_headers = ['Character ID', 'Current Level', 'Completed', 'EndlessAccess', 'Victories', 'Attempts', 'Last Played']
            current_headers = self.story_progress_sheet.row_values(1)

            # Check if headers are correct
            if current_headers != expected_headers:
                logger.warning(f"StoryProgress headers incorrect. Current: {current_headers}")
                logger.info(f"Fixing StoryProgress headers to: {expected_headers}")
                self.story_progress_sheet.update('A1:G1', [expected_headers])
                logger.info("StoryProgress headers fixed")

        except Exception as e:
            logger.error(f"Error ensuring story progress headers: {e}")

    def _fix_id_integrity(self):
        """Fix character ID integrity issues (duplicates, gaps, wrong order)
        Also updates references in BattleHistory, Rankings, and StoryProgress sheets
        """
        try:
            if not self.online_mode:
                return

            logger.info("Checking character ID integrity...")
            all_records = self.worksheet.get_all_records()

            if not all_records:
                return

            # Check for duplicate IDs
            ids = [record.get('ID') for record in all_records]
            id_counts = {}
            for id_val in ids:
                id_counts[id_val] = id_counts.get(id_val, 0) + 1

            duplicates = [id_val for id_val, count in id_counts.items() if count > 1]

            if duplicates:
                logger.warning(f"Found duplicate IDs: {duplicates}")

            # Check for gaps or incorrect sequence
            expected_id = 1
            needs_fixing = False

            for record in all_records:
                current_id = record.get('ID')
                if current_id != expected_id:
                    needs_fixing = True
                    break
                expected_id += 1

            # Fix if needed
            if duplicates or needs_fixing:
                logger.info("Fixing character IDs...")

                # Create ID mapping (old_id -> new_id)
                id_mapping = {}
                for idx, record in enumerate(all_records):
                    old_id = record.get('ID')
                    new_id = idx + 1
                    if old_id != new_id:
                        id_mapping[old_id] = new_id

                # Get all data (including header)
                all_values = self.worksheet.get_all_values()

                if len(all_values) <= 1:  # Only header or empty
                    return

                # Update IDs in Characters sheet (column A, starting from row 2)
                updates = []
                for idx in range(1, len(all_values)):  # Skip header
                    new_id = idx
                    updates.append([new_id])

                # Batch update all IDs at once
                if updates:
                    cell_range = f"A2:A{len(all_values)}"
                    self.worksheet.update(cell_range, updates)
                    logger.info(f"✓ Fixed {len(updates)} character IDs in Characters sheet (1 to {len(updates)})")

                # Update BattleHistory sheet
                if id_mapping:
                    self._update_battle_history_ids(id_mapping)

                # Update Rankings sheet
                if id_mapping:
                    self._update_rankings_ids(id_mapping)

                # Update StoryProgress sheet
                if id_mapping:
                    self._update_story_progress_ids(id_mapping)

            else:
                logger.info("Character IDs are correct")

        except Exception as e:
            logger.error(f"Error fixing ID integrity: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _update_battle_history_ids(self, id_mapping: dict):
        """Update character IDs in BattleHistory sheet (optimized with batch update)"""
        try:
            if not hasattr(self, 'battle_history_sheet') or self.battle_history_sheet is None:
                return

            logger.info("Updating BattleHistory sheet IDs...")
            all_values = self.battle_history_sheet.get_all_values()

            if len(all_values) <= 1:  # Only header or empty
                return

            # Columns: Battle ID, Date, Fighter 1 ID, Fighter 1 Name, Fighter 2 ID, ...
            # Fighter 1 ID is column C (index 2), Fighter 2 ID is column E (index 4)
            # Winner ID is column F (index 5)

            # Collect all updates for batch processing
            updated_rows = []

            for row_idx in range(1, len(all_values)):  # Skip header
                row = list(all_values[row_idx])  # Convert to list for modification
                if len(row) < 6:
                    continue

                row_updated = False

                # Update Fighter 1 ID (column C, index 2)
                if len(row) > 2 and row[2]:
                    try:
                        old_id = int(row[2])
                        if old_id in id_mapping:
                            row[2] = id_mapping[old_id]
                            row_updated = True
                    except (ValueError, TypeError):
                        pass

                # Update Fighter 2 ID (column E, index 4)
                if len(row) > 4 and row[4]:
                    try:
                        old_id = int(row[4])
                        if old_id in id_mapping:
                            row[4] = id_mapping[old_id]
                            row_updated = True
                    except (ValueError, TypeError):
                        pass

                # Update Winner ID (column F, index 5)
                if len(row) > 5 and row[5]:
                    try:
                        old_id = int(row[5])
                        if old_id in id_mapping:
                            row[5] = id_mapping[old_id]
                            row_updated = True
                    except (ValueError, TypeError):
                        pass

                if row_updated:
                    updated_rows.append(row)
                else:
                    updated_rows.append(list(all_values[row_idx]))  # Keep original

            # Batch update all rows at once (1 API call instead of N)
            if any(updated_rows[i] != list(all_values[i + 1]) for i in range(len(updated_rows))):
                cell_range = f'A2:P{len(updated_rows) + 1}'  # P covers all 15 columns
                self.battle_history_sheet.update(cell_range, updated_rows, value_input_option='USER_ENTERED')
                logger.info(f"✓ Updated BattleHistory sheet IDs (batch update: {len(updated_rows)} rows)")

        except Exception as e:
            logger.error(f"Error updating BattleHistory IDs: {e}")

    def _update_rankings_ids(self, id_mapping: dict):
        """Update character IDs in Rankings sheet (optimized with batch update)"""
        try:
            if not hasattr(self, 'ranking_sheet') or self.ranking_sheet is None:
                return

            logger.info("Updating Rankings sheet IDs...")
            all_values = self.ranking_sheet.get_all_values()

            if len(all_values) <= 1:  # Only header or empty
                return

            # Columns: Rank, Character ID, Character Name, ...
            # Character ID is column B (index 1)

            # Collect all updates for batch processing
            updated_rows = []

            for row_idx in range(1, len(all_values)):  # Skip header
                row = list(all_values[row_idx])  # Convert to list for modification
                if len(row) < 2:
                    continue

                # Update Character ID (column B, index 1)
                if row[1]:
                    try:
                        old_id = int(row[1])
                        if old_id in id_mapping:
                            row[1] = id_mapping[old_id]
                    except (ValueError, TypeError):
                        pass

                updated_rows.append(row)

            # Batch update all rows at once (1 API call instead of N)
            if any(updated_rows[i] != list(all_values[i + 1]) for i in range(len(updated_rows))):
                cell_range = f'A2:J{len(updated_rows) + 1}'  # J covers all 10 columns
                self.ranking_sheet.update(cell_range, updated_rows, value_input_option='USER_ENTERED')
                logger.info(f"✓ Updated Rankings sheet IDs (batch update: {len(updated_rows)} rows)")

        except Exception as e:
            logger.error(f"Error updating Rankings IDs: {e}")

    def _update_story_progress_ids(self, id_mapping: dict):
        """Update character IDs in StoryProgress sheet (optimized with batch update)"""
        try:
            if not hasattr(self, 'story_progress_sheet') or self.story_progress_sheet is None:
                return

            logger.info("Updating StoryProgress sheet IDs...")
            all_values = self.story_progress_sheet.get_all_values()

            if len(all_values) <= 1:  # Only header or empty
                return

            # Columns: Character ID, Current Level, ...
            # Character ID is column A (index 0)

            # Collect all updates for batch processing
            updated_rows = []

            for row_idx in range(1, len(all_values)):  # Skip header
                row = list(all_values[row_idx])  # Convert to list for modification
                if len(row) < 1:
                    continue

                # Update Character ID (column A, index 0)
                if row[0]:
                    try:
                        old_id = int(row[0])
                        if old_id in id_mapping:
                            row[0] = id_mapping[old_id]
                    except (ValueError, TypeError):
                        pass

                updated_rows.append(row)

            # Batch update all rows at once (1 API call instead of N)
            if any(updated_rows[i] != list(all_values[i + 1]) for i in range(len(updated_rows))):
                cell_range = f'A2:F{len(updated_rows) + 1}'  # F covers all 6 columns
                self.story_progress_sheet.update(cell_range, updated_rows, value_input_option='USER_ENTERED')
                logger.info(f"✓ Updated StoryProgress sheet IDs (batch update: {len(updated_rows)} rows)")

        except Exception as e:
            logger.error(f"Error updating StoryProgress IDs: {e}")