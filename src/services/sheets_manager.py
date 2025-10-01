"""
Google Sheets manager for character data management with Google Drive integration
"""

import logging
import gspread
import io
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from PIL import Image
from src.models import Character
from config.settings import Settings

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
                'Defense', 'Speed', 'Magic', 'Description', 'Created At',
                'Wins', 'Losses', 'Draws'
            ]

            if not headers or headers != expected_headers:
                self.worksheet.update('A1:N1', [expected_headers])
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
                'F1 Final HP', 'F2 Final HP', 'F1 Damage Dealt', 'F2 Damage Dealt', 'Result Type'
            ]

            if not headers or headers != expected_headers:
                self.battle_history_sheet.update('A1:O1', [expected_headers])
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

    def upload_to_drive(self, file_path: str, file_name: str = None) -> Optional[str]:
        """
        Upload a file to Google Drive and return its public URL

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

            # Read file
            with open(path, 'rb') as f:
                file_data = io.BytesIO(f.read())

            # Create file metadata
            file_metadata = {
                'name': file_name,
                'parents': [Settings.DRIVE_FOLDER_ID] if hasattr(Settings, 'DRIVE_FOLDER_ID') and Settings.DRIVE_FOLDER_ID else []
            }

            # Upload file
            media = MediaIoBaseUpload(file_data, mimetype=mime_type, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()

            file_id = file.get('id')

            # Make file publicly accessible
            self.drive_service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()

            # Get public URL for direct access
            public_url = f"https://drive.google.com/uc?export=view&id={file_id}"

            logger.info(f"Successfully uploaded {file_name} to Google Drive: {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"Failed to upload file to Google Drive: {e}")
            return None

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
                    logger.info(f"Uploaded original image to Drive: {image_url}")

            if character.sprite_path and Path(character.sprite_path).exists():
                # Upload sprite image
                uploaded_url = self.upload_to_drive(
                    character.sprite_path,
                    f"char_{next_id}_sprite{Path(character.sprite_path).suffix}"
                )
                if uploaded_url:
                    sprite_url = uploaded_url
                    logger.info(f"Uploaded sprite to Drive: {sprite_url}")

            # Prepare row data with Drive URLs
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
                character.description or '',
                datetime.now().isoformat(),
                character.wins,
                character.losses,
                character.draws
            ]

            # Append to sheet
            self.worksheet.append_row(row)
            character.id = next_id

            logger.info(f"Character created: {character.name} (ID: {next_id})")
            return True

        except Exception as e:
            logger.error(f"Error creating character: {e}")
            return False

    def get_character(self, character_id: int) -> Optional[Character]:
        """Get a character by ID"""
        try:
            all_records = self.worksheet.get_all_records()

            for record in all_records:
                if record.get('ID') == character_id:
                    return self._record_to_character(record)

            logger.warning(f"Character not found: ID {character_id}")
            return None

        except Exception as e:
            logger.error(f"Error getting character: {e}")
            return None

    def get_all_characters(self) -> List[Character]:
        """Get all characters"""
        try:
            all_records = self.worksheet.get_all_records()
            characters = []

            for record in all_records:
                char = self._record_to_character(record)
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

            for idx, record in enumerate(all_records):
                if record.get('ID') == character.id:
                    # Row number in sheet (accounting for header)
                    row_num = idx + 2

                    # Prepare updated row
                    row = [
                        character.id,
                        character.name,
                        character.image_path or '',
                        character.sprite_path or '',
                        character.hp,
                        character.attack,
                        character.defense,
                        character.speed,
                        character.magic,
                        character.description or '',
                        record.get('Created At', ''),  # Keep original creation time
                        character.wins,
                        character.losses,
                        character.draws
                    ]

                    # Update the row
                    self.worksheet.update(f'A{row_num}:N{row_num}', [row])
                    logger.info(f"Character updated: {character.name} (ID: {character.id})")
                    return True

            logger.warning(f"Character not found for update: ID {character.id}")
            return False

        except Exception as e:
            logger.error(f"Error updating character: {e}")
            return False

    def delete_character(self, character_id: int) -> bool:
        """Delete a character"""
        try:
            all_records = self.worksheet.get_all_records()

            for idx, record in enumerate(all_records):
                if record.get('ID') == character_id:
                    # Row number in sheet (accounting for header)
                    row_num = idx + 2
                    self.worksheet.delete_rows(row_num)
                    logger.info(f"Character deleted: ID {character_id}")
                    return True

            logger.warning(f"Character not found for deletion: ID {character_id}")
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

            character.wins += wins
            character.losses += losses
            character.draws += draws

            return self.update_character(character)

        except Exception as e:
            logger.error(f"Error updating battle stats: {e}")
            return False

    def _record_to_character(self, record: Dict[str, Any]) -> Optional[Character]:
        """Convert spreadsheet record to Character object with URL support"""
        try:
            image_url = str(record.get('Image URL', '')) if record.get('Image URL') else None
            sprite_url = str(record.get('Sprite URL', '')) if record.get('Sprite URL') else None

            # Download images from URLs to local cache if they're URLs
            if image_url and image_url.startswith('http'):
                local_path = Settings.CHARACTERS_DIR / f"char_{record.get('ID')}_original.png"
                if not local_path.exists():
                    self.download_from_url(image_url, str(local_path))
                image_path = str(local_path) if local_path.exists() else image_url
            else:
                image_path = image_url

            if sprite_url and sprite_url.startswith('http'):
                local_path = Settings.SPRITES_DIR / f"char_{record.get('ID')}_sprite.png"
                if not local_path.exists():
                    self.download_from_url(sprite_url, str(local_path))
                sprite_path = str(local_path) if local_path.exists() else sprite_url
            else:
                sprite_path = sprite_url

            return Character(
                id=int(record.get('ID', 0)),
                name=str(record.get('Name', '')),
                image_path=image_path,
                sprite_path=sprite_path,
                hp=int(record.get('HP', 100)),
                attack=int(record.get('Attack', 50)),
                defense=int(record.get('Defense', 50)),
                speed=int(record.get('Speed', 50)),
                magic=int(record.get('Magic', 50)),
                description=str(record.get('Description', '')) if record.get('Description') else None,
                wins=int(record.get('Wins', 0)),
                losses=int(record.get('Losses', 0)),
                draws=int(record.get('Draws', 0))
            )
        except Exception as e:
            logger.error(f"Error converting record to character: {e}")
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
                battle_data.get('result_type', 'Unknown')
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
                total_battles = char.wins + char.losses + char.draws
                win_rate = (char.wins / total_battles * 100) if total_battles > 0 else 0

                # Calculate rating (simple formula: wins * 3 + draws * 1)
                rating = char.wins * 3 + char.draws * 1

                # Get average damage from battle history
                avg_damage = self._calculate_avg_damage(char.id)

                rankings.append({
                    'char_id': char.id,
                    'name': char.name,
                    'total_battles': total_battles,
                    'wins': char.wins,
                    'losses': char.losses,
                    'draws': char.draws,
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