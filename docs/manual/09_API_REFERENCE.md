# 09. API リファレンス

このセクションでは、お絵描きバトラーシステムの主要なクラスとメソッドの詳細な仕様を提供します。

---

## 9.1 データモデル (Pydantic)

### 9.1.1 Character

**ファイル:** `src/models/character.py`

```python
class Character(BaseModel):
    """キャラクターデータモデル"""

    # 必須フィールド
    id: str
    name: str
    image_path: str
    sprite_path: str
    hp: int = Field(ge=10, le=200)
    attack: int = Field(ge=10, le=150)
    defense: int = Field(ge=10, le=100)
    speed: int = Field(ge=10, le=100)
    magic: int = Field(ge=10, le=100)
    luck: int = Field(ge=0, le=100)
    description: str
    created_at: datetime

    # オプションフィールド
    wins: int = Field(default=0, ge=0)
    losses: int = Field(default=0, ge=0)
    draws: int = Field(default=0, ge=0)
```

**プロパティ:**

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `total_stats` | `int` | 全ステータスの合計 (≤350) |
| `win_rate` | `float` | 勝率 (0.0-1.0) |
| `rating` | `int` | レーティング (Wins×3 + Draws) |

**使用例:**
```python
from src.models.character import Character
from datetime import datetime
import uuid

character = Character(
    id=str(uuid.uuid4()),
    name="勇者くん",
    image_path="data/characters/xxx_original.png",
    sprite_path="data/sprites/xxx_sprite.png",
    hp=150,
    attack=80,
    defense=60,
    speed=70,
    magic=50,
    luck=40,
    description="剣を持った勇敢な戦士",
    created_at=datetime.now()
)

print(f"Total Stats: {character.total_stats}")  # 450
print(f"Win Rate: {character.win_rate}")       # 0.0 (初期値)
```

---

### 9.1.2 Battle

**ファイル:** `src/models/battle.py`

```python
class BattleTurn(BaseModel):
    """バトルの1ターン情報"""
    turn_number: int
    attacker_name: str
    defender_name: str
    damage: int
    is_critical: bool = False
    is_guard_break: bool = False
    is_magic: bool = False
    is_evaded: bool = False
    attacker_hp: int
    defender_hp: int

class Battle(BaseModel):
    """バトル結果データモデル"""
    id: str
    character1_id: str
    character1_name: str
    character2_id: str
    character2_name: str
    winner_id: Optional[str]
    winner_name: Optional[str]
    battle_log: list[str]
    turns: list[BattleTurn]
    duration: float
    created_at: datetime

    # 統計データ
    total_turns: int
    char1_final_hp: int
    char2_final_hp: int
    char1_damage_dealt: int
    char2_damage_dealt: int
    result_type: str  # "KO", "Time Limit", "Draw"
```

**使用例:**
```python
from src.models.battle import Battle, BattleTurn

battle = Battle(
    id=str(uuid.uuid4()),
    character1_id=char1.id,
    character1_name=char1.name,
    character2_id=char2.id,
    character2_name=char2.name,
    winner_id=char1.id,
    winner_name=char1.name,
    battle_log=["勇者くんの攻撃！", "30ダメージ！"],
    turns=[
        BattleTurn(
            turn_number=1,
            attacker_name="勇者くん",
            defender_name="魔王",
            damage=30,
            is_critical=False,
            is_guard_break=False,
            is_magic=False,
            is_evaded=False,
            attacker_hp=150,
            defender_hp=120
        )
    ],
    duration=45.5,
    created_at=datetime.now(),
    total_turns=25,
    char1_final_hp=50,
    char2_final_hp=0,
    char1_damage_dealt=200,
    char2_damage_dealt=100,
    result_type="KO"
)
```

---

### 9.1.3 StoryBoss

**ファイル:** `src/models/story_boss.py`

```python
class StoryBoss(BaseModel):
    """ストーリーボスデータモデル"""
    level: int = Field(ge=1, le=5)
    name: str
    hp: int = Field(ge=50, le=300)
    attack: int = Field(ge=30, le=200)
    defense: int = Field(ge=20, le=150)
    speed: int = Field(ge=40, le=180)
    magic: int = Field(ge=10, le=150)
    luck: int = Field(ge=0, le=100)
    description: str
    image_path: Optional[str] = None
    sprite_path: Optional[str] = None
```

**プロパティ:**
| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `total_stats` | `int` | 全ステータスの合計 (≤500) |

---

### 9.1.4 StoryProgress

```python
class StoryProgress(BaseModel):
    """ストーリーモード進行状況"""
    character_id: str
    current_level: int = Field(default=1, ge=1, le=5)
    completed: bool = False
    victories: list[int] = Field(default_factory=list)
    attempts: int = 0
    last_played: datetime = Field(default_factory=datetime.now)

    def add_victory(self, level: int):
        """ボス撃破を記録"""

    def reset(self):
        """進行状況をリセット"""
```

---

## 9.2 サービスクラス

### 9.2.1 SheetsManager (オンラインモード)

**ファイル:** `src/services/sheets_manager.py`

```python
class SheetsManager:
    """Google Sheets データマネージャー"""

    def __init__(self):
        """初期化とGoogle Sheets接続"""

    @property
    def online_mode(self) -> bool:
        """オンラインモードかどうか"""
```

#### キャラクター操作

```python
def get_all_characters(self) -> list[Character]:
    """全キャラクター取得

    Returns:
        キャラクターリスト
    """

def get_character_by_id(self, character_id: str) -> Optional[Character]:
    """IDでキャラクター取得

    Args:
        character_id: キャラクターID (UUID)

    Returns:
        キャラクター、存在しない場合None
    """

def save_character(self, character: Character):
    """キャラクター保存 (新規または更新)

    Args:
        character: キャラクターオブジェクト
    """

def update_character(self, character: Character):
    """キャラクター更新 (戦績更新等)

    Args:
        character: 更新するキャラクター
    """

def delete_character(self, character_id: str):
    """キャラクター削除

    Args:
        character_id: 削除するキャラクターID
    """

def bulk_import_characters(self, characters: list[Character]):
    """複数キャラクターを一括登録 (API呼び出し削減)

    Args:
        characters: キャラクターリスト
    """
```

#### バトル履歴操作

```python
def save_battle_history(self, battle: Battle):
    """バトル履歴を保存

    Args:
        battle: バトルオブジェクト
    """

def get_battle_history(self, character_id: Optional[str] = None,
                       limit: int = 100) -> list[Battle]:
    """バトル履歴取得

    Args:
        character_id: 特定キャラクターの履歴のみ取得 (Noneで全件)
        limit: 取得件数上限

    Returns:
        バトル履歴リスト
    """
```

#### ランキング操作

```python
def update_rankings(self):
    """ランキングを更新 (全キャラクター対象)"""

def get_rankings(self, limit: int = 10) -> list[dict]:
    """ランキング取得

    Args:
        limit: 取得件数

    Returns:
        ランキングデータ (dict形式)
    """
```

#### ストーリーモード操作

```python
def get_story_boss(self, level: int) -> Optional[StoryBoss]:
    """ストーリーボス取得

    Args:
        level: ボスレベル (1-5)

    Returns:
        ボスオブジェクト、存在しない場合None
    """

def save_story_boss(self, boss: StoryBoss):
    """ストーリーボス保存

    Args:
        boss: ボスオブジェクト
    """

def get_story_progress(self, character_id: str) -> Optional[StoryProgress]:
    """ストーリー進行状況取得

    Args:
        character_id: キャラクターID

    Returns:
        進行状況、存在しない場合None
    """

def save_story_progress(self, progress: StoryProgress):
    """ストーリー進行状況保存

    Args:
        progress: 進行状況オブジェクト
    """
```

#### Google Drive操作

```python
def upload_image_to_drive(self, image_path: str, file_name: str) -> str:
    """画像をGoogle Driveにアップロード

    Args:
        image_path: ローカル画像パス
        file_name: Driveでのファイル名

    Returns:
        公開URL
    """

def download_image_from_drive(self, drive_url: str, save_path: str):
    """DriveURLから画像をダウンロード

    Args:
        drive_url: Drive URL
        save_path: 保存先パス
    """
```

---

### 9.2.2 DatabaseManager (オフラインモード)

**ファイル:** `src/services/database_manager.py`

```python
class DatabaseManager:
    """SQLite データマネージャー"""

    def __init__(self):
        """SQLite データベース初期化"""

    @property
    def online_mode(self) -> bool:
        """常にFalse (オフラインモード)"""
        return False
```

#### キャラクター操作

```python
def add_character(self, character: Character):
    """キャラクター追加

    Args:
        character: キャラクターオブジェクト
    """

def get_all_characters(self) -> list[Character]:
    """全キャラクター取得

    Returns:
        キャラクターリスト
    """

def get_character_by_id(self, character_id: str) -> Optional[Character]:
    """IDでキャラクター取得

    Args:
        character_id: キャラクターID

    Returns:
        キャラクター、存在しない場合None
    """

def update_character(self, character: Character):
    """キャラクター更新

    Args:
        character: 更新するキャラクター
    """

def delete_character(self, character_id: str):
    """キャラクター削除

    Args:
        character_id: 削除するキャラクターID
    """
```

---

### 9.2.3 AIAnalyzer

**ファイル:** `src/services/ai_analyzer.py`

```python
class AIAnalyzer:
    """Google Gemini AI キャラクター解析"""

    def __init__(self):
        """Gemini AI初期化"""

    def analyze_character(self, image_path: str) -> dict:
        """キャラクター画像を解析してステータス生成

        Args:
            image_path: 画像ファイルパス

        Returns:
            ステータス辞書
            {
                'hp': int,
                'attack': int,
                'defense': int,
                'speed': int,
                'magic': int,
                'luck': int,
                'description': str
            }

        Raises:
            Exception: API呼び出し失敗時
        """
```

**内部メソッド:**
```python
def _build_prompt(self) -> str:
    """AI用プロンプトを構築"""

def _extract_json(self, response_text: str) -> str:
    """レスポンスからJSON部分を抽出"""

def _validate_stats(self, stats: dict) -> dict:
    """ステータスをバリデーション・調整"""

def _default_stats(self) -> dict:
    """デフォルトステータス (AI失敗時)"""
```

---

### 9.2.4 ImageProcessor

**ファイル:** `src/services/image_processor.py`

```python
class ImageProcessor:
    """画像処理 (背景除去・スプライト抽出)"""

    def __init__(self):
        self.max_sprite_size = (300, 300)
        self.background_threshold = 240

    def remove_background(self, image_path: str,
                          output_path: str,
                          threshold: int = 240) -> str:
        """背景除去

        Args:
            image_path: 入力画像パス
            output_path: 出力画像パス
            threshold: 背景判定閾値 (0-255)

        Returns:
            出力パス
        """

    def extract_sprite(self, image_path: str,
                       output_path: str) -> str:
        """スプライト抽出 (輪郭検出 + トリミング)

        Args:
            image_path: 入力画像パス (透過PNG推奨)
            output_path: 出力パス

        Returns:
            出力パス
        """

    def process_character_image(self,
                                 original_path: str,
                                 character_id: str) -> tuple[str, str]:
        """キャラクター画像を処理 (背景除去 + スプライト抽出)

        Args:
            original_path: オリジナル画像パス
            character_id: キャラクターID

        Returns:
            (オリジナル保存パス, スプライト保存パス)
        """
```

---

### 9.2.5 BattleEngine

**ファイル:** `src/services/battle_engine.py`

```python
class BattleEngine:
    """バトルエンジン"""

    def __init__(self,
                 character1: Character,
                 character2: Character,
                 battle_speed: float = 1.0):
        """初期化

        Args:
            character1: キャラクター1
            character2: キャラクター2
            battle_speed: バトルスピード (0.1-2.0秒/ターン)
        """

    def execute_battle(self) -> Battle:
        """バトルを実行

        Returns:
            バトル結果
        """
```

**内部メソッド:**
```python
def _execute_turn(self) -> bool:
    """1ターン実行

    Returns:
        継続する場合True、終了する場合False
    """

def _perform_attack(self,
                    attacker: Character,
                    defender: Character) -> int:
    """攻撃を実行

    Args:
        attacker: 攻撃側
        defender: 防御側

    Returns:
        与ダメージ
    """

def _calculate_damage(self,
                      attacker: Character,
                      defender: Character,
                      is_magic: bool,
                      is_critical: bool = False,
                      is_guard_break: bool = False) -> int:
    """ダメージ計算

    Args:
        attacker: 攻撃側
        defender: 防御側
        is_magic: 魔法攻撃か
        is_critical: クリティカルか
        is_guard_break: ガードブレイクか

    Returns:
        ダメージ値
    """

def _check_critical(self, attacker: Character) -> bool:
    """クリティカル判定

    確率: 5% + (luck / 10)%, 最大35%

    Returns:
        True: クリティカル発動
    """

def _check_guard_break(self, attacker: Character) -> bool:
    """ガードブレイク判定 (物理攻撃のみ)

    確率: 15% + (luck / 20)%, 最大30%

    Returns:
        True: ガードブレイク発動
    """

def _check_evasion(self,
                   attacker: Character,
                   defender: Character) -> bool:
    """回避判定

    確率: (speed/500) + (def_luck/1000) - (atk_luck/1000)

    Returns:
        True: 回避成功
    """

def _draw_battle_screen(self):
    """Pygameでバトル画面描画"""

def _show_effect(self, effect_type: str, x: int, y: int):
    """エフェクト表示

    Args:
        effect_type: "critical" / "guard_break" / "magic"
        x, y: 表示座標
    """
```

---

### 9.2.6 StoryModeEngine

**ファイル:** `src/services/story_mode_engine.py`

```python
class StoryModeEngine:
    """ストーリーモードエンジン"""

    def __init__(self,
                 db_manager,
                 character: Character):
        """初期化

        Args:
            db_manager: SheetsManager または DatabaseManager
            character: プレイヤーキャラクター
        """

    def load_bosses(self):
        """全ボスデータを読み込み (Lv1-5)"""

    def load_progress(self) -> StoryProgress:
        """プレイヤーの進行状況を読み込み

        Returns:
            進行状況オブジェクト
        """

    def start_story_mode(self) -> bool:
        """ストーリーモードを開始

        Returns:
            True: Lv5クリア, False: 敗北
        """
```

**内部メソッド:**
```python
def _show_challenge_screen(self, level: int):
    """挑戦画面を2秒表示

    Args:
        level: ボスレベル
    """

def _battle_boss(self, boss: StoryBoss) -> str:
    """ボスとバトル

    Args:
        boss: ボスオブジェクト

    Returns:
        "win" or "lose"
    """

def _show_clear_screen(self):
    """クリア画面表示"""

def _show_game_over_screen(self, level: int):
    """ゲームオーバー画面表示

    Args:
        level: 敗北したレベル
    """
```

---

### 9.2.7 EndlessBattleEngine

**ファイル:** `src/services/endless_battle_engine.py`

```python
class EndlessBattleEngine:
    """エンドレスバトルエンジン"""

    def __init__(self,
                 db_manager,
                 characters: list[Character],
                 battle_speed: float = 1.0):
        """初期化

        Args:
            db_manager: データマネージャー
            characters: 参加キャラクターリスト
            battle_speed: バトルスピード
        """

    def execute_endless_battle(self) -> Character:
        """エンドレスバトルを実行

        Returns:
            優勝キャラクター
        """
```

**処理フロー:**
1. キャラクターをシャッフル
2. 先頭をチャンピオンに設定
3. 残りのキャラクターと順次対戦
4. 勝者がチャンピオン、敗者は除外
5. 挑戦者がいなくなるまで繰り返し

---

## 9.3 ユーティリティ

### 9.3.1 FileManager

**ファイル:** `src/utils/file_utils.py`

```python
class FileManager:
    """ファイル管理ユーティリティ"""

    def __init__(self):
        self.data_dir = Path("data")
        self.characters_dir = self.data_dir / "characters"
        self.sprites_dir = self.data_dir / "sprites"
        self.bosses_dir = self.data_dir / "story_bosses"

    def save_character_image(self,
                             src_path: str,
                             character_id: str,
                             image_type: str = "original") -> str:
        """キャラクター画像を保存

        Args:
            src_path: 元ファイルパス
            character_id: キャラクターID
            image_type: "original" or "sprite"

        Returns:
            保存先パス
        """

    def delete_character_files(self, character_id: str):
        """キャラクター関連ファイルを削除

        Args:
            character_id: キャラクターID
        """
```

---

## 9.4 使用例

### 9.4.1 キャラクター登録フロー

```python
from src.services.sheets_manager import SheetsManager
from src.services.ai_analyzer import AIAnalyzer
from src.services.image_processor import ImageProcessor
from src.models.character import Character
import uuid
from datetime import datetime

# 1. 画像処理
processor = ImageProcessor()
original_path, sprite_path = processor.process_character_image(
    "scanned_image.jpg",
    str(uuid.uuid4())
)

# 2. AI解析
analyzer = AIAnalyzer()
stats = analyzer.analyze_character(sprite_path)

# 3. Characterモデル作成
character = Character(
    id=str(uuid.uuid4()),
    name="勇者くん",
    image_path=original_path,
    sprite_path=sprite_path,
    hp=stats['hp'],
    attack=stats['attack'],
    defense=stats['defense'],
    speed=stats['speed'],
    magic=stats['magic'],
    luck=stats['luck'],
    description=stats['description'],
    created_at=datetime.now()
)

# 4. データ保存
manager = SheetsManager()
if manager.online_mode:
    # オンライン: Driveに画像アップロード
    sprite_url = manager.upload_image_to_drive(sprite_path, f"{character.id}_sprite.png")
    character.sprite_path = sprite_url

manager.save_character(character)
```

### 9.4.2 バトル実行フロー

```python
from src.services.battle_engine import BattleEngine
from src.services.sheets_manager import SheetsManager

# キャラクター取得
manager = SheetsManager()
characters = manager.get_all_characters()
char1 = characters[0]
char2 = characters[1]

# バトル実行
engine = BattleEngine(char1, char2, battle_speed=1.0)
battle = engine.execute_battle()

# 結果表示
print(f"Winner: {battle.winner_name}")
print(f"Turns: {battle.total_turns}")

# 戦績更新
if battle.winner_id == char1.id:
    char1.wins += 1
    char2.losses += 1
else:
    char2.wins += 1
    char1.losses += 1

manager.update_character(char1)
manager.update_character(char2)

# バトル履歴保存
manager.save_battle_history(battle)

# ランキング更新
manager.update_rankings()
```

### 9.4.3 ストーリーモード実行フロー

```python
from src.services.story_mode_engine import StoryModeEngine

# エンジン初期化
story_engine = StoryModeEngine(manager, character)

# ボス読み込み
story_engine.load_bosses()

# ストーリーモード開始
cleared = story_engine.start_story_mode()

if cleared:
    print("クリアおめでとうございます！")
else:
    print("ゲームオーバー")
```

---

## 9.5 設定定数

**ファイル:** `config/settings.py`

```python
# Google API
GOOGLE_API_KEY: str
MODEL_NAME: str = "gemini-2.5-flash-lite-preview-06-17"
GOOGLE_CREDENTIALS_PATH: str = "credentials.json"
SPREADSHEET_ID: str
DRIVE_FOLDER_ID: Optional[str]

# ワークシート名
WORKSHEET_NAME: str = "Characters"
BATTLE_HISTORY_SHEET: str = "BattleHistory"
RANKING_SHEET: str = "Rankings"
STORY_BOSSES_SHEET: str = "StoryBosses"
STORY_PROGRESS_SHEET: str = "StoryProgress"

# バトル設定
MAX_BATTLE_TURNS: int = 100
DEFAULT_BATTLE_SPEED: float = 1.0  # 秒/ターン

# 画像処理設定
MAX_SPRITE_SIZE: tuple = (300, 300)
BACKGROUND_THRESHOLD: int = 240

# データベース
DATABASE_PATH: str = "data/database.db"
```

---

## まとめ

このAPIリファレンスでは、お絵描きバトラーシステムの主要なクラスとメソッドを網羅しました。実装の詳細は各ソースファイルを参照してください。
