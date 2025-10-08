# 04. バトルシステム

## 4.1 バトルエンジン概要

### 4.1.1 基本仕様

**ファイル:** `src/services/battle_engine.py`

**バトル形式:**
- ターン制コマンドバトル (完全自動)
- 1対1の対戦
- 最大100ターン (制限時間)
- HP 0で敗北

**勝利条件:**
1. 相手のHPを0以下にする (KO勝利)
2. 100ターン経過時にHPが多い方 (時間切れ勝利)
3. 100ターン経過時にHP同値 (引き分け)

### 4.1.2 BattleEngine クラス構造

```python
class BattleEngine:
    def __init__(self, character1: Character, character2: Character,
                 battle_speed: float = 1.0):
        self.char1 = character1
        self.char2 = character2
        self.char1_hp = character1.hp
        self.char2_hp = character2.hp
        self.battle_speed = battle_speed  # 0.1-2.0秒/ターン
        self.max_turns = 100
        self.current_turn = 0
        self.battle_log: list[str] = []
        self.turns: list[BattleTurn] = []

        # 統計データ
        self.char1_damage_dealt = 0
        self.char2_damage_dealt = 0

    def execute_battle(self) -> Battle:
        """バトルを実行してBattleモデルを返す"""

    def _execute_turn(self) -> bool:
        """1ターンを実行。Falseで戦闘終了"""

    def _calculate_damage(self, attacker, defender, is_magic: bool) -> int:
        """ダメージを計算"""

    def _check_critical(self, attacker) -> bool:
        """クリティカル判定"""

    def _check_guard_break(self, attacker) -> bool:
        """ガードブレイク判定"""

    def _check_evasion(self, attacker, defender) -> bool:
        """回避判定"""
```

---

## 4.2 ターン処理フロー

### 4.2.1 ターン実行シーケンス

```
[ターン開始]
      ↓
┌──────────────────────────────────────┐
│ 1. 行動順決定                         │
│    - 速さが高い方が先攻               │
│    - 同速の場合はランダム              │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 2. 攻撃タイプ選択 (先攻側)            │
│    - 魔法判定: magic / 200           │
│    - 成功 → 魔法攻撃                  │
│    - 失敗 → 物理攻撃                  │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 3. 回避判定 (防御側)                  │
│    - 基本回避率: speed / 500         │
│    - 運補正: defender_luck / 1000    │
│    - 運ペナルティ: -attacker_luck/1000│
│    - 成功 → ダメージ0、次の行動へ     │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 4. クリティカル判定 (攻撃側)          │
│    - 基本: 5%                        │
│    - 運補正: +attacker_luck / 10     │
│    - 最大: 35%                       │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 5. ガードブレイク判定 (物理攻撃のみ)   │
│    - 基本: 15%                       │
│    - 運補正: +attacker_luck / 20     │
│    - 最大: 30%                       │
│    - 成功 → 防御力無視                │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 6. ダメージ計算                       │
│    【物理攻撃】                        │
│    - 通常: attack - defense + rand   │
│    - GB時: attack - 0 + rand         │
│    【魔法攻撃】                        │
│    - attack - (defense * 0.5) + rand │
│    - GB判定なし                       │
│    【共通】                           │
│    - クリティカル時: ×1.5            │
│    - 最低ダメージ: 1                  │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 7. HP更新                            │
│    - defender_hp -= damage          │
│    - 統計データ更新                   │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 8. 画面描画                          │
│    - HPバー更新                      │
│    - エフェクト表示                   │
│    - ログ追加                        │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ 9. 勝敗判定                          │
│    - HP ≤ 0 → KO勝利                 │
│    - 100ターン経過 → 時間切れ判定     │
│    - 継続 → 後攻側の行動へ            │
└──────────────────────────────────────┘
               ↓
         [ターン終了]
```

### 4.2.2 コード実装

```python
def _execute_turn(self) -> bool:
    """1ターンを実行。戦闘終了時にFalse"""
    self.current_turn += 1

    # 1. 行動順決定
    if self.char1.speed >= self.char2.speed:
        first, second = (self.char1, self.char1_hp), (self.char2, self.char2_hp)
        first_is_char1 = True
    else:
        first, second = (self.char2, self.char2_hp), (self.char1, self.char1_hp)
        first_is_char1 = False

    # 2. 先攻の行動
    damage = self._perform_attack(first[0], second[0])
    if first_is_char1:
        self.char2_hp -= damage
        self.char1_damage_dealt += damage
    else:
        self.char1_hp -= damage
        self.char2_damage_dealt += damage

    # 3. 勝敗判定
    if self.char1_hp <= 0 or self.char2_hp <= 0:
        return False

    # 4. 後攻の行動
    damage = self._perform_attack(second[0], first[0])
    if first_is_char1:
        self.char1_hp -= damage
        self.char2_damage_dealt += damage
    else:
        self.char2_hp -= damage
        self.char1_damage_dealt += damage

    # 5. 勝敗判定
    if self.char1_hp <= 0 or self.char2_hp <= 0:
        return False

    # 6. ターン上限チェック
    if self.current_turn >= self.max_turns:
        return False

    return True

def _perform_attack(self, attacker: Character, defender: Character) -> int:
    """攻撃を実行してダメージを返す"""
    # 攻撃タイプ決定
    is_magic = random.random() < (attacker.magic / 200)

    # 回避判定
    if self._check_evasion(attacker, defender):
        self._log(f"{defender.name} は攻撃を回避した！")
        return 0

    # クリティカル判定
    is_critical = self._check_critical(attacker)

    # ガードブレイク判定 (物理のみ)
    is_guard_break = False
    if not is_magic:
        is_guard_break = self._check_guard_break(attacker)

    # ダメージ計算
    damage = self._calculate_damage(
        attacker, defender, is_magic, is_critical, is_guard_break
    )

    # ログ
    attack_type = "魔法攻撃" if is_magic else "物理攻撃"
    log_msg = f"{attacker.name} の{attack_type}！"
    if is_critical:
        log_msg += " クリティカル！"
    if is_guard_break:
        log_msg += " ガードブレイク！"
    log_msg += f" {damage}ダメージ！"
    self._log(log_msg)

    return damage
```

---

## 4.3 ダメージ計算

### 4.3.1 基本計算式

**物理攻撃 (通常):**
```
damage = (attack - defense) + random(-5, 5)
damage = max(1, damage)  # 最低1ダメージ
```

**物理攻撃 (ガードブレイク時):**
```
damage = (attack - 0) + random(-5, 5)  # 防御力完全無視
damage = max(1, damage)
```

**魔法攻撃:**
```
damage = (attack - defense * 0.5) + random(-5, 5)  # 防御貫通50%
damage = max(1, damage)
```

**クリティカル時:**
```
damage = damage * 1.5
```

### 4.3.2 実装コード

```python
def _calculate_damage(self, attacker: Character, defender: Character,
                      is_magic: bool, is_critical: bool = False,
                      is_guard_break: bool = False) -> int:
    """ダメージを計算"""
    # 基礎ダメージ
    if is_guard_break:
        # ガードブレイク: 防御力無視
        base_damage = attacker.attack
    elif is_magic:
        # 魔法攻撃: 防御力50%貫通
        base_damage = attacker.attack - (defender.defense * 0.5)
    else:
        # 物理攻撃: 通常計算
        base_damage = attacker.attack - defender.defense

    # ランダム要素
    randomness = random.randint(-5, 5)
    damage = base_damage + randomness

    # クリティカル
    if is_critical:
        damage = damage * 1.5

    # 最低ダメージ保証
    damage = max(1, int(damage))

    return damage
```

### 4.3.3 ダメージ例

**例1: 通常物理攻撃**
- 攻撃側: Attack 100
- 防御側: Defense 40
- ダメージ: 100 - 40 + rand(-5, 5) = 55-65

**例2: ガードブレイク物理攻撃**
- 攻撃側: Attack 100, Luck 80
- 防御側: Defense 40
- ガードブレイク成功 (19%確率)
- ダメージ: 100 - 0 + rand(-5, 5) = 95-105

**例3: クリティカル魔法攻撃**
- 攻撃側: Attack 100, Luck 80
- 防御側: Defense 40
- 魔法攻撃 + クリティカル
- ダメージ: ((100 - 20) + rand(-5, 5)) × 1.5 = 112-127

---

## 4.4 特殊効果

### 4.4.1 クリティカルヒット

**発動条件:**
- 全ての攻撃で判定
- 物理・魔法両方で発動可能

**発動確率:**
```
critical_rate = 5% + (attacker.luck / 10)%
max_rate = 35%
```

**効果:**
- ダメージ1.5倍
- 赤い光エフェクト
- ログに "クリティカル！" 表示

**実装:**
```python
def _check_critical(self, attacker: Character) -> bool:
    """クリティカル判定"""
    base_rate = 0.05  # 5%
    luck_bonus = attacker.luck / 1000  # 最大10%
    critical_rate = min(0.35, base_rate + luck_bonus)  # 上限35%

    return random.random() < critical_rate
```

### 4.4.2 ガードブレイク

**発動条件:**
- **物理攻撃のみ** (魔法攻撃では発動しない)

**発動確率:**
```
guard_break_rate = 15% + (attacker.luck / 20)%
max_rate = 30%
```

**効果:**
- 防御力を完全無視 (Defense = 0として計算)
- クリティカルと同時発動可能
- 青い爆発エフェクト
- ログに "ガードブレイク！" 表示

**実装:**
```python
def _check_guard_break(self, attacker: Character) -> bool:
    """ガードブレイク判定 (物理攻撃のみ)"""
    base_rate = 0.15  # 15%
    luck_bonus = attacker.luck / 2000  # 最大5%
    guard_break_rate = min(0.30, base_rate + luck_bonus)  # 上限30%

    return random.random() < guard_break_rate
```

**ガードブレイク + クリティカル同時発動例:**
```
攻撃側: Attack 120, Luck 100
防御側: Defense 60

通常物理: (120 - 60) = 60ダメージ
GB発動: (120 - 0) = 120ダメージ
GB + Crit: 120 × 1.5 = 180ダメージ
```

### 4.4.3 回避

**発動条件:**
- 全ての攻撃に対して判定

**回避確率:**
```
evasion_rate = (defender.speed / 500) + (defender.luck / 1000)
                - (attacker.luck / 1000)
max_rate = 30%
```

**効果:**
- ダメージ0
- ログに "○○は攻撃を回避した！" 表示

**実装:**
```python
def _check_evasion(self, attacker: Character, defender: Character) -> bool:
    """回避判定"""
    # 防御側の速さボーナス
    speed_bonus = defender.speed / 500  # 最大20%

    # 防御側の運ボーナス
    defender_luck_bonus = defender.luck / 1000  # 最大10%

    # 攻撃側の運ペナルティ (防御側の回避率を下げる)
    attacker_luck_penalty = attacker.luck / 1000  # 最大10%

    evasion_rate = speed_bonus + defender_luck_bonus - attacker_luck_penalty
    evasion_rate = max(0, min(0.30, evasion_rate))  # 0-30%

    return random.random() < evasion_rate
```

### 4.4.4 魔法攻撃

**発動条件:**
- 毎ターン自動判定

**発動確率:**
```
magic_rate = attacker.magic / 200
max_rate = 50%
```

**効果:**
- 防御力50%貫通
- ガードブレイク判定なし
- クリティカルは発動可能
- 紫色のエフェクト

**実装:**
```python
def _select_attack_type(self, attacker: Character) -> bool:
    """攻撃タイプを選択。Trueで魔法攻撃"""
    magic_chance = min(0.50, attacker.magic / 200)
    return random.random() < magic_chance
```

---

## 4.5 バトル統計データ

### 4.5.1 Battle モデル

**ファイル:** `src/models/battle.py`

```python
class BattleTurn(BaseModel):
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
    id: str
    character1_id: str
    character1_name: str
    character2_id: str
    character2_name: str
    winner_id: Optional[str]
    winner_name: Optional[str]
    battle_log: list[str]
    turns: list[BattleTurn]
    duration: float  # 秒
    created_at: datetime

    # 統計データ
    total_turns: int
    char1_final_hp: int
    char2_final_hp: int
    char1_damage_dealt: int
    char2_damage_dealt: int
    result_type: str  # "KO", "Time Limit", "Draw"
```

### 4.5.2 記録される統計情報

| 項目 | 説明 |
|------|------|
| total_turns | 総ターン数 |
| char1_final_hp | キャラ1の最終HP |
| char2_final_hp | キャラ2の最終HP |
| char1_damage_dealt | キャラ1が与えた総ダメージ |
| char2_damage_dealt | キャラ2が与えた総ダメージ |
| result_type | 勝敗の種類 (KO/Time Limit/Draw) |
| duration | バトル所要時間 (秒) |

### 4.5.3 統計データの活用

**ランキング計算:**
```python
rating = (wins * 3) + draws
```

**平均ダメージ計算:**
```python
avg_damage = total_damage_dealt / total_battles
```

**勝率計算:**
```python
win_rate = wins / (wins + losses + draws)
```

---

## 4.6 バトル画面UI (Pygame)

### 4.6.1 画面レイアウト

```
┌──────────────────────────────────────────────────┐
│                    背景画像                       │
│                                                  │
│  [キャラ1スプライト]              [キャラ2スプライト]│
│    (左側)                           (右側)       │
│                                                  │
│  ┌──────────────┐              ┌──────────────┐  │
│  │キャラ1名      │              │キャラ2名      │  │
│  │HP: ████░░░░  │              │HP: ███████░░ │  │
│  └──────────────┘              └──────────────┘  │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ バトルログ                                  │ │
│  │ ○○の物理攻撃！ 30ダメージ！                │ │
│  │ ××の魔法攻撃！ クリティカル！ 45ダメージ！ │ │
│  │ ...                                         │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│                Turn: 25/100                      │
└──────────────────────────────────────────────────┘
```

### 4.6.2 Pygame初期化

```python
import pygame

class BattleEngine:
    def __init__(self, char1, char2, battle_speed=1.0):
        # Pygame初期化
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("お絵描きバトラー")

        # フォント
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # 日本語フォント (システムフォント使用)
        try:
            self.font_jp = pygame.font.Font("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", 28)
        except:
            self.font_jp = self.font_medium

        # 背景
        self.background = pygame.image.load("assets/images/battle_bg.png")

        # スプライト読み込み
        self.sprite1 = pygame.image.load(char1.sprite_path)
        self.sprite2 = pygame.image.load(char2.sprite_path)

        # HPバー色
        self.hp_bar_bg = (100, 100, 100)
        self.hp_bar_fg = (0, 255, 0)
```

### 4.6.3 描画処理

```python
def _draw_battle_screen(self):
    """バトル画面を描画"""
    # 背景
    self.screen.blit(self.background, (0, 0))

    # キャラクタースプライト
    self.screen.blit(self.sprite1, (100, 300))
    self.screen.blit(self.sprite2, (700, 300))

    # キャラクター名
    name1_surface = self.font_jp.render(self.char1.name, True, (255, 255, 255))
    name2_surface = self.font_jp.render(self.char2.name, True, (255, 255, 255))
    self.screen.blit(name1_surface, (100, 200))
    self.screen.blit(name2_surface, (700, 200))

    # HPバー
    self._draw_hp_bar(100, 240, self.char1_hp, self.char1.hp)
    self._draw_hp_bar(700, 240, self.char2_hp, self.char2.hp)

    # ターン数
    turn_text = f"Turn: {self.current_turn}/{self.max_turns}"
    turn_surface = self.font_medium.render(turn_text, True, (255, 255, 255))
    self.screen.blit(turn_surface, (450, 700))

    # バトルログ
    self._draw_battle_log()

    pygame.display.flip()

def _draw_hp_bar(self, x, y, current_hp, max_hp):
    """HPバーを描画"""
    bar_width = 200
    bar_height = 20

    # 背景
    pygame.draw.rect(self.screen, self.hp_bar_bg, (x, y, bar_width, bar_height))

    # HP (緑色)
    hp_ratio = max(0, current_hp / max_hp)
    filled_width = int(bar_width * hp_ratio)
    pygame.draw.rect(self.screen, self.hp_bar_fg, (x, y, filled_width, bar_height))

    # 枠線
    pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

    # HP数値
    hp_text = f"{max(0, current_hp)}/{max_hp}"
    hp_surface = self.font_small.render(hp_text, True, (255, 255, 255))
    self.screen.blit(hp_surface, (x + bar_width + 10, y))
```

### 4.6.4 エフェクト表示

```python
def _show_effect(self, effect_type: str, x: int, y: int):
    """エフェクトを表示"""
    if effect_type == "critical":
        # 赤い光
        color = (255, 0, 0)
        radius = 50
    elif effect_type == "guard_break":
        # 青い爆発
        color = (0, 100, 255)
        radius = 60
    elif effect_type == "magic":
        # 紫の魔法陣
        color = (200, 0, 255)
        radius = 40
    else:
        return

    # 円形エフェクト
    for i in range(10):
        alpha_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        alpha = int(255 * (1 - i / 10))
        pygame.draw.circle(alpha_surface, (*color, alpha), (radius, radius), radius - i * 5)
        self.screen.blit(alpha_surface, (x - radius, y - radius))
        pygame.display.flip()
        pygame.time.wait(30)
```

---

## 4.7 バトルモード

### 4.7.1 通常バトル (1対1)

**起動方法:**
```python
# メインメニューから
main_menu.start_battle(character1, character2)
```

**特徴:**
- 2キャラクターを選択して対戦
- バトル終了後に結果表示
- 戦績が更新される
- バトル履歴に記録 (オンラインモード)

### 4.7.2 ランダムバトル

**起動方法:**
```python
# ランダムに2キャラ選択して対戦
main_menu.start_random_battle()
```

**特徴:**
- 全キャラクターからランダムに2体選出
- 通常バトルと同様の処理

### 4.7.3 エンドレスバトル

**ファイル:** `src/services/endless_battle_engine.py`

**起動方法:**
```python
# 全キャラクターでトーナメント
main_menu.start_endless_battle()
```

**特徴:**
- 全キャラクターが自動で総当たり戦
- チャンピオン制: 勝者が次の挑戦者と対戦
- 全バトル終了まで自動進行
- バトル間隔: 2秒
- 全バトル履歴を記録

**処理フロー:**
```
全キャラクターリスト取得
     ↓
ランダムシャッフル
     ↓
┌──────────────────────┐
│ チャンピオン選出      │ (先頭のキャラ)
└──────┬───────────────┘
       ↓
┌──────────────────────────────────┐
│ 挑戦者リストから1体選出           │
│ ┌──────────────────────────────┐ │
│ │ バトル実行                    │ │
│ │  - 勝者がチャンピオンに        │ │
│ │  - 敗者は除外                 │ │
│ └──────────────────────────────┘ │
│      ↓                           │
│ ┌──────────────────────────────┐ │
│ │ 次の挑戦者選出                │ │
│ └──────────────────────────────┘ │
│      ↓                           │
│   (挑戦者リストが空?)             │
│    No → 繰り返し                  │
│    Yes → 終了                     │
└──────────────────────────────────┘
```

---

## 4.8 バトル結果処理

### 4.8.1 勝敗判定

```python
def _determine_winner(self) -> tuple[Optional[str], str]:
    """勝者を判定

    Returns:
        (winner_id, result_type)
    """
    if self.char1_hp <= 0 and self.char2_hp <= 0:
        return None, "Draw"  # 相打ち
    elif self.char1_hp <= 0:
        return self.char2.id, "KO"
    elif self.char2_hp <= 0:
        return self.char1.id, "KO"
    elif self.current_turn >= self.max_turns:
        # 時間切れ: HPが多い方の勝ち
        if self.char1_hp > self.char2_hp:
            return self.char1.id, "Time Limit"
        elif self.char2_hp > self.char1_hp:
            return self.char2.id, "Time Limit"
        else:
            return None, "Draw"
    else:
        return None, "Ongoing"
```

### 4.8.2 戦績更新

```python
def _update_records(self, battle: Battle):
    """キャラクターの戦績を更新"""
    if battle.winner_id == self.char1.id:
        self.char1.wins += 1
        self.char2.losses += 1
    elif battle.winner_id == self.char2.id:
        self.char2.wins += 1
        self.char1.losses += 1
    else:
        # 引き分け
        self.char1.draws += 1
        self.char2.draws += 1

    # データベースに保存
    self.db_manager.update_character(self.char1)
    self.db_manager.update_character(self.char2)
```

### 4.8.3 結果表示

```python
def _show_battle_result(self, battle: Battle):
    """バトル結果を表示"""
    result_window = tk.Toplevel(self.root)
    result_window.title("バトル結果")
    result_window.geometry("500x400")

    # 勝者表示
    if battle.winner_id:
        winner_text = f"勝者: {battle.winner_name}"
        color = "gold"
    else:
        winner_text = "引き分け"
        color = "gray"

    tk.Label(result_window, text=winner_text,
             font=("Arial", 24, "bold"), fg=color).pack(pady=20)

    # 統計情報
    stats_frame = tk.Frame(result_window)
    stats_frame.pack(pady=10)

    stats_text = f"""
ターン数: {battle.total_turns}
所要時間: {battle.duration:.1f}秒
結果タイプ: {battle.result_type}

{battle.character1_name}:
  最終HP: {battle.char1_final_hp}
  与ダメージ: {battle.char1_damage_dealt}

{battle.character2_name}:
  最終HP: {battle.char2_final_hp}
  与ダメージ: {battle.char2_damage_dealt}
    """

    tk.Label(stats_frame, text=stats_text, justify=tk.LEFT).pack()

    # 閉じるボタン
    tk.Button(result_window, text="閉じる",
              command=result_window.destroy).pack(pady=10)
```

---

## 次のセクション

次は [05_STORY_MODE.md](05_STORY_MODE.md) でストーリーモードの詳細を確認してください。
