# 05. ストーリーモード

## 5.1 ストーリーモード概要

### 5.1.1 基本仕様

**目的:**
- プレイヤーキャラクターでLv1～Lv5のボスを連続撃破
- Lv5ボスを倒すとクリア
- 1度でも敗北するとゲームオーバー

**特徴:**
- ✅ ノンストップ実行 (Lv1→Lv5まで自動進行)
- ✅ ボス挑戦前に2秒間のチャレンジ画面表示
- ✅ 進行状況はGoogle Sheetsに保存 (オンラインモード)
- ✅ キャラクター毎に独立した進行管理
- ✅ いつでもリセット可能

**ファイル:**
- `src/services/story_mode_engine.py` - ストーリーモードエンジン
- `src/ui/story_boss_manager.py` - ボス管理UI
- `src/models/story_boss.py` - ボス・進行状況モデル

---

## 5.2 ストーリーボスモデル

### 5.2.1 StoryBoss クラス

**ファイル:** `src/models/story_boss.py`

```python
from pydantic import BaseModel, Field
from typing import Optional

class StoryBoss(BaseModel):
    level: int = Field(ge=1, le=5, description="ボスレベル 1-5")
    name: str = Field(min_length=1, max_length=50, description="ボス名")

    # ステータス (プレイヤーキャラより高い上限)
    hp: int = Field(ge=50, le=300, description="体力")
    attack: int = Field(ge=30, le=200, description="攻撃力")
    defense: int = Field(ge=20, le=150, description="防御力")
    speed: int = Field(ge=40, le=180, description="速さ")
    magic: int = Field(ge=10, le=150, description="魔力")
    luck: int = Field(ge=0, le=100, description="運")

    description: str = Field(description="ボスの説明")
    image_path: Optional[str] = Field(default=None, description="オリジナル画像")
    sprite_path: Optional[str] = Field(default=None, description="スプライト画像")

    @property
    def total_stats(self) -> int:
        """総合ステータス"""
        return self.hp + self.attack + self.defense + self.speed + self.magic + self.luck
```

### 5.2.2 ステータス制約

| ステータス | 最小値 | 最大値 | プレイヤー最大値との比較 |
|-----------|--------|--------|------------------------|
| HP | 50 | 300 | +100 (プレイヤー: 200) |
| Attack | 30 | 200 | +50 (プレイヤー: 150) |
| Defense | 20 | 150 | +50 (プレイヤー: 100) |
| Speed | 40 | 180 | +80 (プレイヤー: 100) |
| Magic | 10 | 150 | +50 (プレイヤー: 100) |
| Luck | 0 | 100 | 同じ |

**総合制約:**
- **合計値上限:** 最大500 (プレイヤー: 350)
- ボスは強力だが、総合値制限は緩い

### 5.2.3 推奨ステータス配分 (レベル別)

| レベル | HP | Attack | Defense | Speed | Magic | 総合 | 難易度 |
|-------|-----|--------|---------|-------|-------|------|-------|
| Lv1 | 100 | 50 | 40 | 50 | 40 | 280 | ★☆☆☆☆ |
| Lv2 | 120 | 70 | 50 | 60 | 50 | 350 | ★★☆☆☆ |
| Lv3 | 150 | 90 | 60 | 70 | 60 | 430 | ★★★☆☆ |
| Lv4 | 180 | 110 | 70 | 80 | 70 | 510 | ★★★★☆ |
| Lv5 | 220 | 130 | 90 | 100 | 90 | 630 | ★★★★★ |

---

## 5.3 ストーリー進行状況モデル

### 5.3.1 StoryProgress クラス

```python
from pydantic import BaseModel, Field
from datetime import datetime

class StoryProgress(BaseModel):
    character_id: str = Field(description="プレイヤーキャラクターID")
    current_level: int = Field(default=1, ge=1, le=5, description="現在のレベル")
    completed: bool = Field(default=False, description="Lv5クリア済みか")
    victories: list[int] = Field(default_factory=list, description="撃破済みボスレベル")
    attempts: int = Field(default=0, description="挑戦回数")
    last_played: datetime = Field(default_factory=datetime.now)

    def add_victory(self, level: int):
        """ボス撃破を記録"""
        if level not in self.victories:
            self.victories.append(level)
        self.current_level = level + 1
        if level == 5:
            self.completed = True

    def reset(self):
        """進行状況をリセット"""
        self.current_level = 1
        self.completed = False
        self.victories = []
```

---

## 5.4 ストーリーモードエンジン

### 5.4.1 StoryModeEngine クラス

**ファイル:** `src/services/story_mode_engine.py`

```python
class StoryModeEngine:
    def __init__(self, db_manager, character: Character):
        self.db_manager = db_manager
        self.character = character
        self.bosses: dict[int, StoryBoss] = {}
        self.progress: StoryProgress = None

    def load_bosses(self):
        """全ボスデータを読み込み (Lv1-5)"""
        for level in range(1, 6):
            boss = self.db_manager.get_story_boss(level)
            if boss:
                self.bosses[level] = boss

    def load_progress(self) -> StoryProgress:
        """プレイヤーの進行状況を読み込み"""
        progress = self.db_manager.get_story_progress(self.character.id)
        if not progress:
            # 初回プレイ
            progress = StoryProgress(character_id=self.character.id)
        return progress

    def start_story_mode(self) -> bool:
        """ストーリーモードを開始

        Returns:
            True: Lv5クリア, False: 敗北
        """
        self.progress = self.load_progress()
        self.progress.attempts += 1

        # Lv1から順に挑戦
        for level in range(self.progress.current_level, 6):
            # チャレンジ画面表示 (2秒)
            self._show_challenge_screen(level)

            # ボスバトル実行
            boss = self.bosses[level]
            result = self._battle_boss(boss)

            if result == "win":
                # 勝利
                self.progress.add_victory(level)
                self.db_manager.save_story_progress(self.progress)

                if level == 5:
                    # クリア！
                    self._show_clear_screen()
                    return True
            else:
                # 敗北
                self._show_game_over_screen(level)
                self.db_manager.save_story_progress(self.progress)
                return False

        return True

    def _show_challenge_screen(self, level: int):
        """挑戦画面を2秒表示"""
        boss = self.bosses[level]

        # Tkinterダイアログ
        dialog = tk.Toplevel()
        dialog.title("挑戦！")
        dialog.geometry("400x300")

        tk.Label(dialog, text=f"Lv{level} ボス",
                 font=("Arial", 32, "bold")).pack(pady=20)
        tk.Label(dialog, text=boss.name,
                 font=("Arial", 24)).pack(pady=10)
        tk.Label(dialog, text="挑戦します！",
                 font=("Arial", 20)).pack(pady=20)

        # 2秒後に自動で閉じる
        dialog.after(2000, dialog.destroy)
        dialog.wait_window()

    def _battle_boss(self, boss: StoryBoss) -> str:
        """ボスとバトル

        Returns:
            "win" or "lose"
        """
        # BattleEngineでバトル実行
        battle_engine = BattleEngine(self.character, boss)
        battle = battle_engine.execute_battle()

        if battle.winner_id == self.character.id:
            return "win"
        else:
            return "lose"
```

### 5.4.2 処理フロー図

```
[ストーリーモード開始]
      ↓
┌────────────────────────────────────┐
│ 進行状況読み込み                    │
│ - current_level取得                │
│ - 初回ならLv1から開始               │
└──────────┬─────────────────────────┘
           ↓
┌────────────────────────────────────┐
│ ボスデータ読み込み (Lv1-5)          │
└──────────┬─────────────────────────┘
           ↓
     ┌─────────────┐
     │ レベルループ │ (current_level → 5)
     └─────┬───────┘
           ↓
┌────────────────────────────────────┐
│ チャレンジ画面表示 (2秒)            │
│ - Lv○ ボス                         │
│ - ボス名                            │
│ - 「挑戦します！」                   │
└──────────┬─────────────────────────┘
           ↓
┌────────────────────────────────────┐
│ ボスバトル実行                      │
│ - BattleEngine使用                 │
│ - 通常バトルと同じ仕様              │
└──────────┬─────────────────────────┘
           ↓
       【勝敗判定】
           ↓
    ┌──────┴──────┐
    │              │
  勝利           敗北
    │              │
    ↓              ↓
┌─────────┐  ┌─────────────┐
│進行状況  │  │ゲームオーバー│
│更新      │  │画面表示      │
│- 撃破記録│  │- 敗北レベル  │
│- Lv+1    │  │ 表示         │
└────┬────┘  └─────┬───────┘
     │              │
  Lv5クリア?      終了
     │              ↓
   Yes → [クリア画面]
     │
   No → [次のボスへ]
```

---

## 5.5 ボス管理UI

### 5.5.1 Story Boss Manager

**ファイル:** `src/ui/story_boss_manager.py`

**起動方法:**
```
メインメニュー → メニューバー → ゲーム → Story Boss Manager
```

**機能:**
- ✅ Lv1-5のボスを作成・編集
- ✅ オリジナル画像アップロード
- ✅ スプライト画像自動生成 (透過処理)
- ✅ ステータス設定 (範囲チェック付き)
- ✅ Google Sheets保存 (オンラインモード)
- ✅ 画像プレビュー

### 5.5.2 UI レイアウト

```
┌──────────────────────────────────────────────────┐
│ Story Boss Manager                               │
├──────────────────────────────────────────────────┤
│                                                  │
│ ┌────────────┐  ┌──────────────────────────────┐ │
│ │ ボス選択    │  │ ボス編集エリア                 │ │
│ │            │  │                               │ │
│ │ ○ Lv1     │  │ 名前: [____________]         │ │
│ │ ○ Lv2     │  │                               │ │
│ │ ○ Lv3     │  │ HP:      [___] / 300         │ │
│ │ ○ Lv4     │  │ 攻撃力:  [___] / 200         │ │
│ │ ○ Lv5     │  │ 防御力:  [___] / 150         │ │
│ │            │  │ 速さ:    [___] / 180         │ │
│ └────────────┘  │ 魔力:    [___] / 150         │ │
│                 │ 運:      [___] / 100         │ │
│                 │                               │ │
│                 │ 総合: ○○○ / 500              │ │
│                 │                               │ │
│                 │ 説明:                         │ │
│                 │ [_____________________________│ │
│                 │  _____________________________│ │
│                 │  ____________________________]│ │
│                 │                               │ │
│                 │ [画像アップロード]             │ │
│                 │ [スプライト生成]               │ │
│                 │                               │ │
│                 │ ┌───────────┐               │ │
│                 │ │プレビュー  │               │ │
│                 │ │           │               │ │
│                 │ └───────────┘               │ │
│                 │                               │ │
│                 │ [保存] [キャンセル]           │ │
│                 └──────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### 5.5.3 ボス作成フロー

```python
class StoryBossManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_boss: Optional[StoryBoss] = None
        self.current_level = 1

    def select_boss_level(self, level: int):
        """ボスレベルを選択"""
        self.current_level = level
        # 既存ボスを読み込み
        boss = self.db_manager.get_story_boss(level)
        if boss:
            self.load_boss_data(boss)
        else:
            self.create_new_boss(level)

    def upload_image(self):
        """オリジナル画像をアップロード"""
        file_path = filedialog.askopenfilename(
            title="ボス画像を選択",
            filetypes=[("画像ファイル", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.original_image_path = file_path
            self.preview_image(file_path)

    def generate_sprite(self):
        """スプライトを生成 (背景除去)"""
        if not self.original_image_path:
            messagebox.showerror("エラー", "先にオリジナル画像をアップロードしてください")
            return

        # 画像処理
        processor = ImageProcessor()
        sprite_path = processor.process_character_image(
            self.original_image_path,
            f"boss_lv{self.current_level}"
        )[1]

        self.sprite_path = sprite_path
        self.preview_image(sprite_path)

    def save_boss(self):
        """ボスデータを保存"""
        # バリデーション
        if not self.validate_boss_stats():
            return

        boss = StoryBoss(
            level=self.current_level,
            name=self.name_entry.get(),
            hp=int(self.hp_entry.get()),
            attack=int(self.attack_entry.get()),
            defense=int(self.defense_entry.get()),
            speed=int(self.speed_entry.get()),
            magic=int(self.magic_entry.get()),
            luck=int(self.luck_entry.get()),
            description=self.desc_text.get("1.0", tk.END),
            image_path=self.original_image_path,
            sprite_path=self.sprite_path
        )

        # Google Sheetsに保存
        self.db_manager.save_story_boss(boss)
        messagebox.showinfo("成功", f"Lv{self.current_level} ボスを保存しました")

    def validate_boss_stats(self) -> bool:
        """ステータスをバリデーション"""
        try:
            hp = int(self.hp_entry.get())
            attack = int(self.attack_entry.get())
            defense = int(self.defense_entry.get())
            speed = int(self.speed_entry.get())
            magic = int(self.magic_entry.get())
            luck = int(self.luck_entry.get())

            # 範囲チェック
            if not (50 <= hp <= 300):
                raise ValueError("HPは50-300の範囲で設定してください")
            if not (30 <= attack <= 200):
                raise ValueError("攻撃力は30-200の範囲で設定してください")
            if not (20 <= defense <= 150):
                raise ValueError("防御力は20-150の範囲で設定してください")
            if not (40 <= speed <= 180):
                raise ValueError("速さは40-180の範囲で設定してください")
            if not (10 <= magic <= 150):
                raise ValueError("魔力は10-150の範囲で設定してください")
            if not (0 <= luck <= 100):
                raise ValueError("運は0-100の範囲で設定してください")

            # 総合値チェック
            total = hp + attack + defense + speed + magic + luck
            if total > 500:
                raise ValueError(f"総合値が上限を超えています ({total}/500)")

            return True

        except ValueError as e:
            messagebox.showerror("エラー", str(e))
            return False
```

---

## 5.6 ストーリーモードプレイ

### 5.6.1 起動方法

**メインメニューから:**
```
メニューバー → ゲーム → ストーリーモード
```

**キャラクター選択:**
1. 登録済みキャラクター一覧が表示される
2. プレイするキャラクターを選択
3. 「バトル開始」ボタンをクリック

### 5.6.2 プレイフロー

```
[キャラクター選択]
      ↓
[バトル開始]
      ↓
┌──────────────────────┐
│ Lv1 挑戦画面 (2秒)   │
│ "Lv1 ボス"            │
│ "○○○"               │
│ "挑戦します！"         │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│ Lv1 バトル実行       │
└──────┬───────────────┘
       ↓
    【勝敗判定】
       ↓
   ┌───┴───┐
 勝利       敗北
   │         │
   ↓         ↓
[Lv2へ]  [ゲームオーバー]
   │
   ↓
[Lv2 挑戦画面]
   ...
   ↓
[Lv5 バトル]
   ↓
 勝利
   ↓
[クリア画面]
```

### 5.6.3 クリア画面

```python
def _show_clear_screen(self):
    """クリア画面を表示"""
    clear_window = tk.Toplevel()
    clear_window.title("クリア！")
    clear_window.geometry("500x400")

    # クリア表示
    tk.Label(clear_window, text="CLEAR!",
             font=("Arial", 48, "bold"), fg="gold").pack(pady=30)

    tk.Label(clear_window, text=f"{self.character.name} は全てのボスを倒しました！",
             font=("Arial", 18)).pack(pady=20)

    # 統計情報
    stats_text = f"""
総挑戦回数: {self.progress.attempts}
クリアレベル: Lv5

おめでとうございます！
    """
    tk.Label(clear_window, text=stats_text,
             font=("Arial", 14), justify=tk.LEFT).pack(pady=20)

    tk.Button(clear_window, text="閉じる",
              font=("Arial", 14),
              command=clear_window.destroy).pack(pady=20)
```

### 5.6.4 ゲームオーバー画面

```python
def _show_game_over_screen(self, level: int):
    """ゲームオーバー画面を表示"""
    game_over_window = tk.Toplevel()
    game_over_window.title("ゲームオーバー")
    game_over_window.geometry("500x400")

    # ゲームオーバー表示
    tk.Label(game_over_window, text="GAME OVER",
             font=("Arial", 48, "bold"), fg="red").pack(pady=30)

    tk.Label(game_over_window, text=f"Lv{level} で敗北しました",
             font=("Arial", 18)).pack(pady=20)

    # 統計情報
    stats_text = f"""
到達レベル: Lv{level}
総挑戦回数: {self.progress.attempts}

もう一度挑戦しますか？
    """
    tk.Label(game_over_window, text=stats_text,
             font=("Arial", 14), justify=tk.LEFT).pack(pady=20)

    button_frame = tk.Frame(game_over_window)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="リトライ",
              font=("Arial", 14),
              command=lambda: self._retry(game_over_window)).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="閉じる",
              font=("Arial", 14),
              command=game_over_window.destroy).pack(side=tk.LEFT, padx=10)

def _retry(self, window):
    """ストーリーモードをリトライ"""
    window.destroy()
    self.start_story_mode()
```

---

## 5.7 進行状況管理

### 5.7.1 進行状況リセット

**UI操作:**
```
ストーリーモード画面 → [進行状況リセット] ボタン
```

**実装:**
```python
def reset_story_progress(self):
    """進行状況をリセット"""
    result = messagebox.askyesno(
        "確認",
        f"{self.character.name} のストーリー進行状況をリセットしますか？\n"
        "Lv1からやり直しになります。"
    )

    if result:
        progress = self.load_progress()
        progress.reset()
        self.db_manager.save_story_progress(progress)
        messagebox.showinfo("成功", "進行状況をリセットしました")
        self.refresh_progress_display()
```

### 5.7.2 進行状況表示

```python
def display_story_progress(self, character: Character):
    """進行状況を表示"""
    progress = self.db_manager.get_story_progress(character.id)
    if not progress:
        return "未プレイ"

    if progress.completed:
        return f"クリア済み (挑戦回数: {progress.attempts})"
    else:
        return f"Lv{progress.current_level} まで到達 (挑戦回数: {progress.attempts})"
```

---

## 5.8 データ保存 (Google Sheets)

### 5.8.1 StoryBosses シート

**列構成 (11列):**
| 列 | 項目 | データ型 |
|----|------|---------|
| A | Level | 1-5 |
| B | Name | 文字列 |
| C | Image URL | URL (Google Drive) |
| D | Sprite URL | URL (Google Drive) |
| E | HP | 50-300 |
| F | Attack | 30-200 |
| G | Defense | 20-150 |
| H | Speed | 40-180 |
| I | Magic | 10-150 |
| J | Luck | 0-100 |
| K | Description | 文字列 |

### 5.8.2 StoryProgress シート

**列構成 (6列):**
| 列 | 項目 | データ型 |
|----|------|---------|
| A | Character ID | UUID |
| B | Current Level | 1-5 |
| C | Completed | TRUE/FALSE |
| D | Victories | カンマ区切り (例: "1,2,3") |
| E | Attempts | 整数 |
| F | Last Played | ISO8601形式 |

---

## 次のセクション

次は [06_DATA_MANAGEMENT.md](06_DATA_MANAGEMENT.md) でデータ管理の詳細を確認してください。
