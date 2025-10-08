# 03. キャラクター管理

## 3.1 キャラクターデータモデル

### 3.1.1 Character クラス定義

**ファイル:** `src/models/character.py`

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Character(BaseModel):
    id: str = Field(description="UUID形式の一意識別子")
    name: str = Field(min_length=1, max_length=50, description="キャラクター名")
    image_path: str = Field(description="オリジナル画像のパスまたはURL")
    sprite_path: str = Field(description="スプライト画像のパスまたはURL")

    # ステータス (RPG風)
    hp: int = Field(ge=10, le=200, description="体力")
    attack: int = Field(ge=10, le=150, description="攻撃力")
    defense: int = Field(ge=10, le=100, description="防御力")
    speed: int = Field(ge=10, le=100, description="速さ")
    magic: int = Field(ge=10, le=100, description="魔力")
    luck: int = Field(ge=0, le=100, description="運")

    description: str = Field(description="AI生成のキャラクター説明")
    created_at: datetime = Field(default_factory=datetime.now)

    # 戦績
    wins: int = Field(default=0, ge=0)
    losses: int = Field(default=0, ge=0)
    draws: int = Field(default=0, ge=0)

    @property
    def total_stats(self) -> int:
        """ステータス合計値を計算"""
        return self.hp + self.attack + self.defense + self.speed + self.magic + self.luck

    @property
    def win_rate(self) -> float:
        """勝率を計算 (0.0-1.0)"""
        total = self.wins + self.losses + self.draws
        return self.wins / total if total > 0 else 0.0

    @property
    def rating(self) -> int:
        """レーティングを計算 (Wins×3 + Draws)"""
        return self.wins * 3 + self.draws
```

### 3.1.2 ステータス制約

| ステータス | 最小値 | 最大値 | 説明 |
|-----------|--------|--------|------|
| HP | 10 | 200 | 体力。0になると敗北 |
| 攻撃力 (Attack) | 10 | 150 | 物理攻撃・魔法攻撃のダメージに影響 |
| 防御力 (Defense) | 10 | 100 | 受けるダメージを軽減 |
| 速さ (Speed) | 10 | 100 | 行動順・回避率に影響 |
| 魔力 (Magic) | 10 | 100 | 魔法攻撃の発動確率に影響 |
| 運 (Luck) | 0 | 100 | クリティカル率・ガードブレイク率・回避率に影響 |

**総合制約:**
- **合計値上限:** `HP + Attack + Defense + Speed + Magic + Luck ≤ 350`
- **バランス調整:** AI解析時に自動的に調整

### 3.1.3 ステータスの役割

**HP (体力):**
- バトル中のダメージ蓄積
- 0以下になると敗北

**Attack (攻撃力):**
- 物理攻撃ダメージの基礎値
- 魔法攻撃にも影響

**Defense (防御力):**
- 受けるダメージを軽減
- 物理攻撃: `damage = attack - defense`
- 魔法攻撃: `damage = attack - (defense * 0.5)`

**Speed (速さ):**
- ターン行動順を決定 (速い方が先攻)
- 回避率に影響: `evasion_bonus = speed / 500`

**Magic (魔力):**
- 魔法攻撃の発動確率: `magic_chance = magic / 200`
- 魔法攻撃は防御力を50%貫通

**Luck (運):**
- クリティカル率: `5% + (luck / 10)%` (最大35%)
- ガードブレイク率: `15% + (luck / 20)%` (最大30%)
- 防御側の運は攻撃側の命中率を下げる: 最大-30%

---

## 3.2 画像処理パイプライン

### 3.2.1 処理フロー概要

```
[入力画像] (PNG/JPG/JPEG)
      ↓
┌─────────────────────────────────────┐
│ 1. 画像読み込み (Pillow)              │
│    - フォーマット検証                  │
│    - RGBA変換                         │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 2. 背景除去 (OpenCV + Pillow)         │
│    - グレースケール変換                │
│    - 二値化 (閾値: 240)                │
│    - 輪郭検出                          │
│    - マスク生成                        │
│    - アルファチャンネル合成             │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 3. スプライト抽出                      │
│    - バウンディングボックス計算         │
│    - 余白トリミング (10pxマージン)      │
│    - アスペクト比維持                   │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 4. リサイズ・最適化                    │
│    - 最大サイズ: 300x300px            │
│    - アンチエイリアス適用               │
│    - PNG圧縮                          │
└─────────────┬───────────────────────┘
              ↓
[出力スプライト] (透過PNG)
```

### 3.2.2 ImageProcessor クラス

**ファイル:** `src/services/image_processor.py`

**主要メソッド:**

```python
class ImageProcessor:
    def __init__(self):
        self.max_sprite_size = (300, 300)
        self.background_threshold = 240

    def remove_background(self, image_path: str, output_path: str) -> str:
        """背景を除去して透過PNGを生成"""

    def extract_sprite(self, image_path: str, output_path: str) -> str:
        """キャラクタースプライトを抽出"""

    def process_character_image(self,
                                 original_path: str,
                                 character_id: str) -> tuple[str, str]:
        """オリジナル画像からスプライトを生成

        Returns:
            (original_save_path, sprite_save_path)
        """
```

### 3.2.3 背景除去アルゴリズム

**手法:** 白背景検出 + マスク生成

```python
import cv2
import numpy as np
from PIL import Image

def remove_background(image_path: str, threshold: int = 240) -> Image:
    # 1. 画像読み込み
    img = Image.open(image_path).convert("RGBA")
    img_array = np.array(img)

    # 2. グレースケール変換
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)

    # 3. 二値化 (白背景を検出)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    # 4. マスク反転 (白背景を透明に)
    mask = cv2.bitwise_not(binary)

    # 5. アルファチャンネルに適用
    img_array[:, :, 3] = mask

    return Image.fromarray(img_array)
```

**パラメータ調整:**
- `threshold`: 背景判定の閾値 (デフォルト: 240)
  - 高い値 (250-255): より白い部分のみ除去
  - 低い値 (200-239): 薄いグレーも除去

### 3.2.4 スプライト抽出アルゴリズム

**手法:** 輪郭検出 + バウンディングボックス

```python
def extract_sprite(image: Image) -> Image:
    # 1. アルファチャンネルから輪郭検出
    alpha = np.array(image.split()[-1])
    contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 2. 最大の輪郭を取得
    if not contours:
        return image
    largest_contour = max(contours, key=cv2.contourArea)

    # 3. バウンディングボックス計算
    x, y, w, h = cv2.boundingRect(largest_contour)

    # 4. マージン追加
    margin = 10
    x = max(0, x - margin)
    y = max(0, y - margin)
    w = min(image.width - x, w + margin * 2)
    h = min(image.height - y, h + margin * 2)

    # 5. クロップ
    return image.crop((x, y, x + w, y + h))
```

### 3.2.5 リサイズ処理

**アスペクト比維持リサイズ:**

```python
def resize_sprite(image: Image, max_size: tuple = (300, 300)) -> Image:
    # アスペクト比を維持してリサイズ
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image
```

**最適化オプション:**
- **リサンプリング:** `LANCZOS` (高品質)
- **PNG最適化:** `optimize=True`
- **圧縮レベル:** `compress_level=9`

---

## 3.3 AI解析システム

### 3.3.1 Google Gemini 統合

**ファイル:** `src/services/ai_analyzer.py`

**使用モデル:** `gemini-2.5-flash-lite-preview-06-17` (設定で変更可能)

```python
import google.generativeai as genai
from PIL import Image

class AIAnalyzer:
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)

    def analyze_character(self, image_path: str) -> dict:
        """キャラクター画像を解析してステータスを生成"""
```

### 3.3.2 プロンプト設計

**システムプロンプト:**

```text
あなたはRPGのキャラクターステータスを生成するAIです。
提供された手描きイラストから、以下のステータスを生成してください。

【ステータス生成ルール】
1. HP (体力): 10-200
   - 大柄・頑丈そう → 高め
   - 小柄・華奢 → 低め

2. Attack (攻撃力): 10-150
   - 武器を持っている → 高め
   - 筋肉質・戦闘的 → 高め
   - 非戦闘的・平和的 → 低め

3. Defense (防御力): 10-100
   - 鎧・防具あり → 高め
   - 露出が多い → 低め
   - 硬そうな見た目 → 高め

4. Speed (速さ): 10-100
   - スリムな体型 → 高め
   - 軽装 → 高め
   - 重装備 → 低め
   - 飛行可能そう → 高め

5. Magic (魔力): 10-100
   - 魔法のアイテム・杖 → 高め
   - 神秘的な見た目 → 高め
   - 物理的な武器のみ → 低め

6. Luck (運): 0-100
   - 幸運そう・明るい → 高め
   - 不運そう・暗い → 低め

【重要な制約】
- 合計値は必ず350以下にすること
- 各ステータスは上記範囲内にすること
- バランスよく配分すること

【出力形式】
JSON形式で以下を出力:
{
  "hp": 数値,
  "attack": 数値,
  "defense": 数値,
  "speed": 数値,
  "magic": 数値,
  "luck": 数値,
  "description": "日本語でキャラクターの説明 (2-3文)"
}
```

### 3.3.3 レスポンス処理

```python
def analyze_character(self, image_path: str) -> dict:
    # 1. 画像読み込み
    img = Image.open(image_path)

    # 2. プロンプト生成
    prompt = self._build_prompt()

    # 3. Gemini API呼び出し
    response = self.model.generate_content([prompt, img])

    # 4. JSON抽出
    json_str = self._extract_json(response.text)
    stats = json.loads(json_str)

    # 5. バリデーション
    stats = self._validate_stats(stats)

    return stats

def _validate_stats(self, stats: dict) -> dict:
    """ステータスを検証・調整"""
    # 範囲チェック
    stats['hp'] = max(10, min(200, stats['hp']))
    stats['attack'] = max(10, min(150, stats['attack']))
    stats['defense'] = max(10, min(100, stats['defense']))
    stats['speed'] = max(10, min(100, stats['speed']))
    stats['magic'] = max(10, min(100, stats['magic']))
    stats['luck'] = max(0, min(100, stats['luck']))

    # 合計値チェック
    total = sum([stats['hp'], stats['attack'], stats['defense'],
                 stats['speed'], stats['magic'], stats['luck']])

    if total > 350:
        # 比例配分で調整
        ratio = 350 / total
        stats['hp'] = int(stats['hp'] * ratio)
        stats['attack'] = int(stats['attack'] * ratio)
        stats['defense'] = int(stats['defense'] * ratio)
        stats['speed'] = int(stats['speed'] * ratio)
        stats['magic'] = int(stats['magic'] * ratio)
        stats['luck'] = int(stats['luck'] * ratio)

    return stats
```

### 3.3.4 エラーハンドリング

```python
def analyze_character(self, image_path: str, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            response = self.model.generate_content([prompt, img])
            return self._parse_response(response)
        except json.JSONDecodeError:
            # JSON解析失敗 → リトライ
            if attempt < retries - 1:
                continue
            # フォールバック: デフォルト値
            return self._default_stats()
        except Exception as e:
            logging.error(f"AI analysis failed: {e}")
            return self._default_stats()

def _default_stats(self) -> dict:
    """デフォルトステータス (AI解析失敗時)"""
    return {
        'hp': 100,
        'attack': 50,
        'defense': 40,
        'speed': 40,
        'magic': 40,
        'luck': 50,
        'description': 'AIによる解析に失敗しました。デフォルト値を使用しています。'
    }
```

---

## 3.4 キャラクター登録フロー

### 3.4.1 GUI操作フロー

**メインメニュー → キャラクター登録:**

```
1. [キャラクター登録] ボタンをクリック
   ↓
2. ファイル選択ダイアログが開く
   - 対応形式: PNG, JPG, JPEG
   ↓
3. 画像を選択して [開く]
   ↓
4. 処理開始 (プログレスバー表示)
   - 画像処理中...
   - AI解析中...
   ↓
5. 確認ダイアログ表示
   - プレビュー画像
   - 生成されたステータス
   - 説明文
   ↓
6. キャラクター名を入力
   ↓
7. [保存] をクリック
   ↓
8. データ保存 (Google Sheets/SQLite)
   ↓
9. 完了メッセージ表示
```

### 3.4.2 処理シーケンス

**コード例 (MainMenu.register_character()):**

```python
def register_character(self):
    # 1. 画像選択
    file_path = filedialog.askopenfilename(
        title="キャラクター画像を選択",
        filetypes=[
            ("画像ファイル", "*.png *.jpg *.jpeg"),
            ("すべてのファイル", "*.*")
        ]
    )
    if not file_path:
        return

    # 2. プログレスバー表示
    progress = self.show_progress("処理中...")

    try:
        # 3. UUID生成
        character_id = str(uuid.uuid4())

        # 4. 画像処理
        progress.update("画像処理中...")
        original_path, sprite_path = self.image_processor.process_character_image(
            file_path, character_id
        )

        # 5. AI解析
        progress.update("AI解析中...")
        stats = self.ai_analyzer.analyze_character(sprite_path)

        # 6. 確認ダイアログ
        progress.close()
        result = self.show_character_confirm_dialog(
            sprite_path, stats
        )

        if not result:
            return

        # 7. Characterモデル作成
        character = Character(
            id=character_id,
            name=result['name'],
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

        # 8. データ保存
        if self.db_manager.online_mode:
            # Google Sheetsに保存
            self.db_manager.save_character(character)
        else:
            # SQLiteに保存
            self.db_manager.add_character(character)

        # 9. UIリフレッシュ
        self.refresh_character_list()

        messagebox.showinfo("成功", f"{character.name} を登録しました！")

    except Exception as e:
        messagebox.showerror("エラー", f"登録に失敗しました: {e}")
```

### 3.4.3 確認ダイアログUI

**表示内容:**
- スプライト画像プレビュー (200x200px)
- ステータス表示 (プログレスバー形式)
- 説明文テキスト
- 名前入力フィールド
- [保存] / [キャンセル] ボタン

```python
def show_character_confirm_dialog(self, sprite_path, stats):
    dialog = tk.Toplevel(self.root)
    dialog.title("キャラクター確認")

    # スプライト表示
    img = Image.open(sprite_path)
    img.thumbnail((200, 200))
    photo = ImageTk.PhotoImage(img)
    label_img = tk.Label(dialog, image=photo)
    label_img.image = photo  # 参照保持
    label_img.pack(pady=10)

    # ステータス表示
    stats_frame = tk.Frame(dialog)
    stats_frame.pack(pady=10, padx=20, fill=tk.BOTH)

    for stat_name, value in stats.items():
        if stat_name == 'description':
            continue
        self._create_stat_bar(stats_frame, stat_name, value)

    # 説明文
    desc_label = tk.Label(dialog, text=stats['description'],
                          wraplength=300, justify=tk.LEFT)
    desc_label.pack(pady=10)

    # 名前入力
    name_frame = tk.Frame(dialog)
    name_frame.pack(pady=10)
    tk.Label(name_frame, text="名前:").pack(side=tk.LEFT)
    name_entry = tk.Entry(name_frame, width=30)
    name_entry.pack(side=tk.LEFT, padx=5)

    # ボタン
    result = {'confirmed': False, 'name': ''}

    def on_save():
        result['confirmed'] = True
        result['name'] = name_entry.get()
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="保存", command=on_save).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="キャンセル", command=on_cancel).pack(side=tk.LEFT, padx=5)

    dialog.wait_window()
    return result if result['confirmed'] else None
```

---

## 3.5 キャラクター一覧表示

### 3.5.1 リスト表示UI

**表示項目:**
- スプライト画像サムネイル (50x50px)
- 名前
- 総合ステータス
- 戦績 (W-L-D)
- 勝率

```python
def refresh_character_list(self):
    # 既存リストをクリア
    for widget in self.character_list_frame.winfo_children():
        widget.destroy()

    # キャラクター取得
    characters = self.db_manager.get_all_characters()

    # ソート (レーティング順)
    characters.sort(key=lambda c: c.rating, reverse=True)

    # リスト表示
    for i, character in enumerate(characters):
        self._create_character_row(character, i)

def _create_character_row(self, character: Character, index: int):
    row_frame = tk.Frame(self.character_list_frame,
                         bg='white' if index % 2 == 0 else '#f0f0f0')
    row_frame.pack(fill=tk.X, padx=5, pady=2)

    # スプライト
    img = Image.open(character.sprite_path)
    img.thumbnail((50, 50))
    photo = ImageTk.PhotoImage(img)
    label_img = tk.Label(row_frame, image=photo)
    label_img.image = photo
    label_img.pack(side=tk.LEFT, padx=5)

    # 名前
    tk.Label(row_frame, text=character.name, width=15, anchor='w').pack(side=tk.LEFT)

    # 総合ステータス
    tk.Label(row_frame, text=f"総合: {character.total_stats}", width=10).pack(side=tk.LEFT)

    # 戦績
    record = f"{character.wins}-{character.losses}-{character.draws}"
    tk.Label(row_frame, text=record, width=10).pack(side=tk.LEFT)

    # 勝率
    win_rate = f"{character.win_rate * 100:.1f}%"
    tk.Label(row_frame, text=win_rate, width=8).pack(side=tk.LEFT)

    # 選択ボタン
    tk.Button(row_frame, text="選択",
              command=lambda: self.select_character(character)).pack(side=tk.RIGHT, padx=5)
```

### 3.5.2 フィルタリング・ソート

**ソートオプション:**
- レーティング順 (デフォルト)
- 名前順
- 作成日順
- 総合ステータス順

```python
def sort_characters(self, sort_by: str):
    characters = self.db_manager.get_all_characters()

    if sort_by == 'rating':
        characters.sort(key=lambda c: c.rating, reverse=True)
    elif sort_by == 'name':
        characters.sort(key=lambda c: c.name)
    elif sort_by == 'created_at':
        characters.sort(key=lambda c: c.created_at, reverse=True)
    elif sort_by == 'total_stats':
        characters.sort(key=lambda c: c.total_stats, reverse=True)

    self.display_characters(characters)
```

**検索機能:**

```python
def search_characters(self, query: str):
    all_characters = self.db_manager.get_all_characters()

    # 名前で部分一致検索
    results = [c for c in all_characters if query.lower() in c.name.lower()]

    self.display_characters(results)
```

---

## 3.6 キャラクター詳細表示

### 3.6.1 詳細ダイアログ

**表示内容:**
- 大きなスプライト (300x300px)
- 全ステータス (バー表示)
- 説明文
- 詳細戦績
- バトル履歴 (オンラインモードのみ)

```python
def show_character_detail(self, character: Character):
    dialog = tk.Toplevel(self.root)
    dialog.title(f"{character.name} - 詳細")
    dialog.geometry("600x700")

    # スプライト
    img = Image.open(character.sprite_path)
    img.thumbnail((300, 300))
    photo = ImageTk.PhotoImage(img)
    label_img = tk.Label(dialog, image=photo)
    label_img.image = photo
    label_img.pack(pady=10)

    # ステータス
    stats_frame = tk.Frame(dialog)
    stats_frame.pack(pady=10, padx=20, fill=tk.BOTH)

    self._create_stat_bar(stats_frame, "HP", character.hp, 200)
    self._create_stat_bar(stats_frame, "攻撃", character.attack, 150)
    self._create_stat_bar(stats_frame, "防御", character.defense, 100)
    self._create_stat_bar(stats_frame, "速さ", character.speed, 100)
    self._create_stat_bar(stats_frame, "魔力", character.magic, 100)
    self._create_stat_bar(stats_frame, "運", character.luck, 100)

    tk.Label(stats_frame, text=f"総合: {character.total_stats}/350",
             font=("Arial", 12, "bold")).pack(pady=5)

    # 説明文
    tk.Label(dialog, text=character.description,
             wraplength=500, justify=tk.LEFT).pack(pady=10)

    # 戦績
    record_frame = tk.Frame(dialog)
    record_frame.pack(pady=10)

    tk.Label(record_frame, text=f"戦績: {character.wins}勝 {character.losses}敗 {character.draws}分",
             font=("Arial", 12)).pack()
    tk.Label(record_frame, text=f"勝率: {character.win_rate * 100:.1f}%",
             font=("Arial", 12)).pack()
    tk.Label(record_frame, text=f"レーティング: {character.rating}",
             font=("Arial", 12)).pack()

    # バトル履歴 (オンラインモードのみ)
    if self.db_manager.online_mode:
        self._show_battle_history(dialog, character.id)

def _create_stat_bar(self, parent, label, value, max_value):
    frame = tk.Frame(parent)
    frame.pack(fill=tk.X, pady=2)

    tk.Label(frame, text=f"{label}:", width=8, anchor='w').pack(side=tk.LEFT)

    bar_frame = tk.Frame(frame, width=300, height=20, bg='#ddd')
    bar_frame.pack(side=tk.LEFT, padx=5)
    bar_frame.pack_propagate(False)

    filled_width = int(300 * (value / max_value))
    filled_bar = tk.Frame(bar_frame, width=filled_width, bg='#4CAF50')
    filled_bar.pack(side=tk.LEFT, fill=tk.Y)

    tk.Label(frame, text=str(value), width=5, anchor='e').pack(side=tk.LEFT)
```

---

## 3.7 キャラクター削除

### 3.7.1 削除フロー

```python
def delete_character(self, character: Character):
    # 確認ダイアログ
    result = messagebox.askyesno(
        "確認",
        f"{character.name} を削除しますか？\nこの操作は取り消せません。"
    )

    if not result:
        return

    try:
        # データベースから削除
        self.db_manager.delete_character(character.id)

        # ローカルファイル削除
        if os.path.exists(character.sprite_path):
            os.remove(character.sprite_path)
        if os.path.exists(character.image_path):
            os.remove(character.image_path)

        # UIリフレッシュ
        self.refresh_character_list()

        messagebox.showinfo("成功", f"{character.name} を削除しました")

    except Exception as e:
        messagebox.showerror("エラー", f"削除に失敗しました: {e}")
```

### 3.7.2 削除時の注意事項

⚠️ **削除前に確認すべき事項:**
- バトル履歴は保持される (キャラクターIDは残る)
- ランキングからは削除される
- 画像ファイルも削除される (復元不可)
- オンラインモード: Google Sheets/Driveからも削除

---

## 次のセクション

次は [04_BATTLE_SYSTEM.md](04_BATTLE_SYSTEM.md) でバトルシステムの詳細を確認してください。
