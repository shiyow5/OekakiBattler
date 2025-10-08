# 06. データ管理

## 6.1 オンライン/オフラインモード

### 6.1.1 モード判定ロジック

**起動時の自動判定:**

```python
# src/services/sheets_manager.py

class SheetsManager:
    def __init__(self):
        self.online_mode = False
        try:
            # 1. credentials.json存在チェック
            if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
                raise FileNotFoundError("credentials.json not found")

            # 2. サービスアカウント認証
            credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_CREDENTIALS_PATH,
                scopes=SCOPES
            )

            # 3. Google Sheets接続
            self.client = gspread.authorize(credentials)
            self.sheet = self.client.open_by_key(SPREADSHEET_ID)

            # 4. シート初期化
            self.initialize_sheets()

            self.online_mode = True
            logging.info("オンラインモードで起動しました")

        except Exception as e:
            logging.warning(f"オンラインモード接続失敗: {e}")
            logging.info("オフラインモードにフォールバックします")
            self.online_mode = False
```

### 6.1.2 モード別機能比較

| 機能 | オンラインモード | オフラインモード |
|------|-----------------|-----------------|
| キャラクター管理 | ✅ Google Sheets | ✅ SQLite |
| 画像保存 | ✅ Google Drive + ローカルキャッシュ | ✅ ローカルのみ |
| バトル実行 | ✅ 可能 | ✅ 可能 |
| バトル履歴 | ✅ 記録される | ❌ 記録されない |
| ランキング | ✅ 自動更新 | ❌ なし |
| ストーリーモード進行 | ✅ 保存される | ❌ 保存されない |
| デバイス間同期 | ✅ 可能 | ❌ 不可 |

---

## 6.2 Google Sheets統合 (オンラインモード)

### 6.2.1 スプレッドシート構造

**スプレッドシート:** 1つ (SPREADSHEET_IDで指定)
**ワークシート:** 5枚

```
OekakiBattler Spreadsheet
├── Characters (15列)
├── BattleHistory (15列)
├── Rankings (10列)
├── StoryBosses (11列)
└── StoryProgress (6列)
```

### 6.2.2 Characters シート

**列構成:**
| 列 | 項目 | データ型 | 例 |
|----|------|---------|-----|
| A | ID | UUID | 123e4567-e89b-12d3-a456-426614174000 |
| B | Name | 文字列 | 勇者くん |
| C | Image URL | URL | https://drive.google.com/... |
| D | Sprite URL | URL | https://drive.google.com/... |
| E | HP | 10-200 | 150 |
| F | Attack | 10-150 | 80 |
| G | Defense | 10-100 | 60 |
| H | Speed | 10-100 | 70 |
| I | Magic | 10-100 | 50 |
| J | Luck | 0-100 | 40 |
| K | Description | 文字列 | 剣を持った勇敢な戦士... |
| L | Created At | ISO8601 | 2025-10-08T10:30:00 |
| M | Wins | 整数 | 15 |
| N | Losses | 整数 | 3 |
| O | Draws | 整数 | 2 |

**初期化コード:**
```python
def _initialize_characters_sheet(self):
    """Charactersシートを初期化"""
    try:
        worksheet = self.sheet.worksheet("Characters")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = self.sheet.add_worksheet("Characters", rows=1000, cols=15)

    # ヘッダー行
    headers = [
        "ID", "Name", "Image URL", "Sprite URL",
        "HP", "Attack", "Defense", "Speed", "Magic", "Luck",
        "Description", "Created At", "Wins", "Losses", "Draws"
    ]
    worksheet.update('A1:O1', [headers])
```

### 6.2.3 BattleHistory シート

**列構成:**
| 列 | 項目 | データ型 |
|----|------|---------|
| A | Battle ID | UUID |
| B | Date | ISO8601 |
| C | Character1 ID | UUID |
| D | Character1 Name | 文字列 |
| E | Character2 ID | UUID |
| F | Character2 Name | 文字列 |
| G | Winner ID | UUID (NULL可) |
| H | Winner Name | 文字列 (NULL可) |
| I | Total Turns | 整数 |
| J | Duration (seconds) | 浮動小数 |
| K | Char1 Final HP | 整数 |
| L | Char2 Final HP | 整数 |
| M | Char1 Damage Dealt | 整数 |
| N | Char2 Damage Dealt | 整数 |
| O | Result Type | KO/Time Limit/Draw |

**バトル記録例:**
```python
def save_battle_history(self, battle: Battle):
    """バトル履歴を保存"""
    worksheet = self.sheet.worksheet("BattleHistory")

    row = [
        battle.id,
        battle.created_at.isoformat(),
        battle.character1_id,
        battle.character1_name,
        battle.character2_id,
        battle.character2_name,
        battle.winner_id or "",
        battle.winner_name or "",
        battle.total_turns,
        battle.duration,
        battle.char1_final_hp,
        battle.char2_final_hp,
        battle.char1_damage_dealt,
        battle.char2_damage_dealt,
        battle.result_type
    ]

    worksheet.append_row(row)
```

### 6.2.4 Rankings シート

**列構成:**
| 列 | 項目 | 計算方法 |
|----|------|---------|
| A | Rank | 順位 (Rating順) |
| B | Character ID | UUID |
| C | Name | 文字列 |
| D | Total Battles | Wins + Losses + Draws |
| E | Wins | 整数 |
| F | Losses | 整数 |
| G | Draws | 整数 |
| H | Win Rate | Wins / Total Battles |
| I | Avg Damage | 平均与ダメージ |
| J | Rating | (Wins × 3) + Draws |

**ランキング更新:**
```python
def update_rankings(self):
    """ランキングを更新"""
    # 全キャラクター取得
    characters = self.get_all_characters()

    # レーティング順にソート
    characters.sort(key=lambda c: c.rating, reverse=True)

    # Rankingsシートをクリア
    rankings_sheet = self.sheet.worksheet("Rankings")
    rankings_sheet.clear()

    # ヘッダー
    headers = [
        "Rank", "Character ID", "Name", "Total Battles",
        "Wins", "Losses", "Draws", "Win Rate", "Avg Damage", "Rating"
    ]
    rankings_sheet.update('A1:J1', [headers])

    # データ書き込み
    rows = []
    for rank, char in enumerate(characters, start=1):
        total_battles = char.wins + char.losses + char.draws
        win_rate = char.wins / total_battles if total_battles > 0 else 0
        avg_damage = self._calculate_avg_damage(char.id)

        rows.append([
            rank,
            char.id,
            char.name,
            total_battles,
            char.wins,
            char.losses,
            char.draws,
            f"{win_rate:.2%}",
            avg_damage,
            char.rating
        ])

    # 一括書き込み (API呼び出し削減)
    if rows:
        rankings_sheet.update(f'A2:J{len(rows)+1}', rows)
```

### 6.2.5 バッチ更新による最適化

**問題:** Google Sheets APIは100 requests/100秒の制限あり

**解決策:** バッチ更新を使用

```python
def bulk_import_characters(self, characters: list[Character]):
    """複数キャラクターを一括登録"""
    worksheet = self.sheet.worksheet("Characters")

    # 既存データの行数を取得
    current_rows = len(worksheet.get_all_values())

    # データ準備
    rows = []
    for char in characters:
        row = [
            char.id, char.name, char.image_path, char.sprite_path,
            char.hp, char.attack, char.defense, char.speed,
            char.magic, char.luck, char.description,
            char.created_at.isoformat(),
            char.wins, char.losses, char.draws
        ]
        rows.append(row)

    # 一括書き込み (1回のAPI呼び出し)
    start_row = current_rows + 1
    end_row = start_row + len(rows) - 1
    worksheet.update(f'A{start_row}:O{end_row}', rows)
```

---

## 6.3 Google Drive統合

### 6.3.1 Drive API設定

**スコープ:**
```python
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
```

**初期化:**
```python
from googleapiclient.discovery import build

def __init__(self):
    # ... (Sheets認証後)
    self.drive_service = build('drive', 'v3', credentials=credentials)
    self.drive_folder_id = DRIVE_FOLDER_ID  # .envから取得
```

### 6.3.2 画像アップロード

```python
def upload_image_to_drive(self, image_path: str, file_name: str) -> str:
    """画像をGoogle Driveにアップロード

    Args:
        image_path: ローカル画像パス
        file_name: Driveでのファイル名

    Returns:
        公開URL
    """
    file_metadata = {
        'name': file_name,
        'mimeType': 'image/png'
    }

    # フォルダ指定がある場合
    if self.drive_folder_id:
        file_metadata['parents'] = [self.drive_folder_id]

    # ファイルアップロード
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(image_path, mimetype='image/png')

    file = self.drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    file_id = file['id']

    # 公開設定
    self.drive_service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    # 直接アクセス可能なURL
    public_url = f"https://drive.google.com/uc?id={file_id}"

    return public_url
```

### 6.3.3 画像キャッシュ戦略

**目的:** API呼び出し削減、オフライン対応

**実装:**
```python
def get_sprite_image(self, character: Character) -> str:
    """スプライト画像を取得 (キャッシュ優先)

    Returns:
        ローカルファイルパス
    """
    # キャッシュパス
    cache_path = f"data/sprites/{character.id}_sprite.png"

    # キャッシュ存在チェック
    if os.path.exists(cache_path):
        return cache_path

    # オンラインモード: Driveからダウンロード
    if self.online_mode and character.sprite_path.startswith("http"):
        self._download_from_drive(character.sprite_path, cache_path)
        return cache_path

    # オフラインモードまたはローカルパス
    return character.sprite_path

def _download_from_drive(self, drive_url: str, save_path: str):
    """DriveURLから画像をダウンロード"""
    import requests

    # URL変換: webViewLink → 直接ダウンロードURL
    file_id = self._extract_file_id(drive_url)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    response = requests.get(download_url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

def _extract_file_id(self, url: str) -> str:
    """DriveURLからファイルIDを抽出"""
    if 'id=' in url:
        return url.split('id=')[1].split('&')[0]
    elif '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    else:
        raise ValueError(f"Invalid Drive URL: {url}")
```

---

## 6.4 SQLite データベース (オフラインモード)

### 6.4.1 データベース構造

**ファイル:** `data/database.db`

**テーブル:**

```sql
-- characters テーブル
CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    image_path TEXT,
    sprite_path TEXT,
    hp INTEGER,
    attack INTEGER,
    defense INTEGER,
    speed INTEGER,
    magic INTEGER,
    luck INTEGER,
    description TEXT,
    created_at TIMESTAMP,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0
);

-- battles テーブル (オフラインモードでは使用しない)
CREATE TABLE battles (
    id TEXT PRIMARY KEY,
    character1_id TEXT,
    character2_id TEXT,
    winner_id TEXT,
    created_at TIMESTAMP
);
```

### 6.4.2 SQLAlchemy モデル

**ファイル:** `config/database.py`

```python
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class CharacterDB(Base):
    __tablename__ = 'characters'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    image_path = Column(String)
    sprite_path = Column(String)
    hp = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)
    speed = Column(Integer)
    magic = Column(Integer)
    luck = Column(Integer)
    description = Column(String)
    created_at = Column(DateTime)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)

# データベース初期化
engine = create_engine('sqlite:///data/database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
```

### 6.4.3 DatabaseManager クラス

**ファイル:** `src/services/database_manager.py`

```python
class DatabaseManager:
    def __init__(self):
        self.online_mode = False
        self.session = Session()

    def add_character(self, character: Character):
        """キャラクターを追加"""
        char_db = CharacterDB(
            id=character.id,
            name=character.name,
            image_path=character.image_path,
            sprite_path=character.sprite_path,
            hp=character.hp,
            attack=character.attack,
            defense=character.defense,
            speed=character.speed,
            magic=character.magic,
            luck=character.luck,
            description=character.description,
            created_at=character.created_at,
            wins=character.wins,
            losses=character.losses,
            draws=character.draws
        )
        self.session.add(char_db)
        self.session.commit()

    def get_all_characters(self) -> list[Character]:
        """全キャラクター取得"""
        char_dbs = self.session.query(CharacterDB).all()
        return [self._db_to_model(char_db) for char_db in char_dbs]

    def update_character(self, character: Character):
        """キャラクター更新"""
        char_db = self.session.query(CharacterDB).filter_by(id=character.id).first()
        if char_db:
            char_db.wins = character.wins
            char_db.losses = character.losses
            char_db.draws = character.draws
            self.session.commit()

    def delete_character(self, character_id: str):
        """キャラクター削除"""
        char_db = self.session.query(CharacterDB).filter_by(id=character_id).first()
        if char_db:
            self.session.delete(char_db)
            self.session.commit()

    def _db_to_model(self, char_db: CharacterDB) -> Character:
        """DBモデルをPydanticモデルに変換"""
        return Character(
            id=char_db.id,
            name=char_db.name,
            image_path=char_db.image_path,
            sprite_path=char_db.sprite_path,
            hp=char_db.hp,
            attack=char_db.attack,
            defense=char_db.defense,
            speed=char_db.speed,
            magic=char_db.magic,
            luck=char_db.luck,
            description=char_db.description,
            created_at=char_db.created_at,
            wins=char_db.wins,
            losses=char_db.losses,
            draws=char_db.draws
        )
```

---

## 6.5 ローカルファイルストレージ

### 6.5.1 ディレクトリ構造

```
data/
├── database.db              # SQLiteデータベース
├── characters/              # オリジナル画像
│   ├── {uuid}_original.png
│   └── ...
├── sprites/                 # スプライト画像
│   ├── {uuid}_sprite.png
│   └── ...
└── story_bosses/            # ストーリーボス画像
    ├── boss_lv1_original.png
    ├── boss_lv1_sprite.png
    └── ...
```

### 6.5.2 ファイル命名規則

**キャラクター:**
- オリジナル: `{character_id}_original.{ext}`
- スプライト: `{character_id}_sprite.png`

**ストーリーボス:**
- オリジナル: `boss_lv{level}_original.{ext}`
- スプライト: `boss_lv{level}_sprite.png`

### 6.5.3 ファイル管理ユーティリティ

```python
# src/utils/file_utils.py

import os
import shutil
from pathlib import Path

class FileManager:
    def __init__(self):
        self.data_dir = Path("data")
        self.characters_dir = self.data_dir / "characters"
        self.sprites_dir = self.data_dir / "sprites"
        self.bosses_dir = self.data_dir / "story_bosses"

        # ディレクトリ作成
        self.characters_dir.mkdir(parents=True, exist_ok=True)
        self.sprites_dir.mkdir(parents=True, exist_ok=True)
        self.bosses_dir.mkdir(parents=True, exist_ok=True)

    def save_character_image(self, src_path: str, character_id: str,
                             image_type: str = "original") -> str:
        """キャラクター画像を保存

        Args:
            src_path: 元ファイルパス
            character_id: キャラクターID
            image_type: "original" or "sprite"

        Returns:
            保存先パス
        """
        ext = Path(src_path).suffix
        if image_type == "original":
            dest_path = self.characters_dir / f"{character_id}_original{ext}"
        else:
            dest_path = self.sprites_dir / f"{character_id}_sprite.png"

        shutil.copy2(src_path, dest_path)
        return str(dest_path)

    def delete_character_files(self, character_id: str):
        """キャラクター関連ファイルを削除"""
        # オリジナル画像
        for ext in ['.png', '.jpg', '.jpeg']:
            original = self.characters_dir / f"{character_id}_original{ext}"
            if original.exists():
                original.unlink()

        # スプライト
        sprite = self.sprites_dir / f"{character_id}_sprite.png"
        if sprite.exists():
            sprite.unlink()
```

---

## 6.6 データ同期とバックアップ

### 6.6.1 オンライン→オフライン同期

**シナリオ:** オフライン環境で作業するため、事前にデータをダウンロード

```python
def sync_online_to_offline(self):
    """オンラインデータをオフラインに同期"""
    if not self.sheets_manager.online_mode:
        raise Exception("オンラインモードではありません")

    # 全キャラクター取得
    characters = self.sheets_manager.get_all_characters()

    # SQLiteに保存
    db_manager = DatabaseManager()
    for char in characters:
        # 画像ダウンロード
        if char.sprite_path.startswith("http"):
            local_sprite = self._download_sprite(char)
            char.sprite_path = local_sprite

        db_manager.add_character(char)

    print(f"{len(characters)} キャラクターを同期しました")
```

### 6.6.2 オフライン→オンライン同期

**シナリオ:** オフラインで作成したキャラクターをオンラインにアップロード

```python
def sync_offline_to_online(self):
    """オフラインデータをオンラインに同期"""
    if not self.sheets_manager.online_mode:
        raise Exception("オンラインモードではありません")

    # SQLiteから全キャラクター取得
    db_manager = DatabaseManager()
    local_characters = db_manager.get_all_characters()

    # オンラインの既存キャラクター取得
    online_characters = self.sheets_manager.get_all_characters()
    online_ids = {char.id for char in online_characters}

    # 新規キャラクターのみアップロード
    new_characters = [char for char in local_characters if char.id not in online_ids]

    for char in new_characters:
        # 画像をDriveにアップロード
        if not char.sprite_path.startswith("http"):
            sprite_url = self.sheets_manager.upload_image_to_drive(
                char.sprite_path,
                f"{char.id}_sprite.png"
            )
            char.sprite_path = sprite_url

        self.sheets_manager.save_character(char)

    print(f"{len(new_characters)} キャラクターをアップロードしました")
```

### 6.6.3 バックアップ

**Google Sheets自動バックアップ:**
- Google Driveの版管理機能で自動的にバックアップされる
- 「ファイル」→「版の履歴」→「版の履歴を表示」で復元可能

**SQLiteバックアップ:**
```bash
# 手動バックアップ
cp data/database.db data/database_backup_$(date +%Y%m%d).db

# スクリプトによるバックアップ
python scripts/backup_database.py
```

**バックアップスクリプト例:**
```python
# scripts/backup_database.py

import shutil
from datetime import datetime
from pathlib import Path

def backup_database():
    src = Path("data/database.db")
    if not src.exists():
        print("データベースが見つかりません")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = Path(f"data/backups/database_{timestamp}.db")
    dest.parent.mkdir(exist_ok=True)

    shutil.copy2(src, dest)
    print(f"バックアップ完了: {dest}")

if __name__ == "__main__":
    backup_database()
```

---

## 次のセクション

次は [07_LINE_BOT.md](07_LINE_BOT.md) でLINE Bot連携の詳細を確認してください。
