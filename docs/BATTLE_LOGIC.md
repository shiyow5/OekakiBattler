# 🎮 お絵描きバトラー - バトルロジック詳細仕様書

## 📋 目次
1. [概要](#概要)
2. [キャラクターステータス](#キャラクターステータス)
3. [バトルフロー](#バトルフロー)
4. [ダメージ計算](#ダメージ計算)
5. [特殊システム](#特殊システム)
6. [バランス調整](#バランス調整)
7. [実装詳細](#実装詳細)

---

## 概要

お絵描きバトラーのバトルシステムは、ターンベースの戦闘システムです。各キャラクターは5つの基本ステータスを持ち、これらの数値に基づいて自動的に戦闘が進行します。

### 基本原則
- **ターンベース**: 素早さによって行動順が決定
- **自動戦闘**: AIが行動を選択（プレイヤーの介入なし）
- **ステータス重視**: キャラクターの個性がバトルに直接影響
- **運要素**: ランダム要素により予測不可能性を確保

---

## キャラクターステータス

### 📊 ステータス構成

| ステータス | 範囲 | 効果 |
|---|---|---|
| **HP（体力）** | 50-150 | 生命力。0になると敗北 |
| **Attack（攻撃力）** | 30-120 | 物理攻撃のダメージに影響 |
| **Defense（防御力）** | 20-100 | 受けるダメージを軽減 |
| **Speed（素早さ）** | 40-130 | 行動順と命中率に影響 |
| **Magic（魔力）** | 10-100 | 魔法攻撃のダメージと使用頻度に影響 |

### 計算式
```python
# 総合ステータス
total_stats = hp + attack + defense + speed + magic

# 勝率（戦績がある場合）
win_rate = (win_count / battle_count) * 100
```

---

## バトルフロー

### 1. 🚀 バトル開始フェーズ

```python
# 初期化処理
char1_current_hp = char1.hp
char2_current_hp = char2.hp
battle = Battle(character1_id=char1.id, character2_id=char2.id)

# ログ記録
battle.add_log_entry(f"🥊 バトル開始！ {char1.name} VS {char2.name}")
battle.add_log_entry(f"💚 {char1.name} HP: {char1_current_hp} / {char2.name} HP: {char2_current_hp}")
```

### 2. ⚡ ターン順序決定

```python
def determine_turn_order(char1: Character, char2: Character):
    # 素早さに±5のランダム要素を追加
    char1_speed = char1.speed + random.randint(-5, 5)
    char2_speed = char2.speed + random.randint(-5, 5)
    
    # 先攻・後攻を決定
    if char1_speed >= char2_speed:
        return [(char1, char2), (char2, char1)]
    else:
        return [(char2, char1), (char1, char2)]
```

### 3. 🎯 行動選択システム

```python
def _choose_action(attacker: Character, defender: Character, defender_hp: int):
    # 基本魔法確率（魔力依存、最大40%）
    magic_prob = min(0.4, attacker.magic / 200)
    
    # 戦術的調整
    if defender.defense > 70:  # 高防御相手
        magic_prob += 0.2      # 魔法確率+20%
    
    if defender_hp < defender.hp * 0.3:  # 相手瀕死
        magic_prob += 0.15     # フィニッシュ魔法+15%
    
    return "magic" if random.random() < magic_prob else "attack"
```

### 4. 💥 戦闘実行ループ

```python
while turn_number <= MAX_TURNS:  # 最大50ターン
    if char1_current_hp <= 0 or char2_current_hp <= 0:
        break  # 決着
    
    turn_order = determine_turn_order(char1, char2)
    
    for attacker, defender in turn_order:
        # ターン実行
        turn = execute_turn(attacker, defender, turn_number)
        battle.add_turn(turn)
        
        # HP更新とログ記録
        update_hp_and_log(turn)
        
        # ビジュアル更新
        if visual_mode:
            update_battle_display()
            time.sleep(1.0 * battle_speed)
    
    turn_number += 1
```

---

## ダメージ計算

### 🎲 命中判定

```python
def calculate_hit_chance(attacker: Character, defender: Character):
    speed_diff = attacker.speed - defender.speed
    hit_chance = max(0.8, min(0.95, 0.85 + speed_diff * 0.001))
    
    # 命中率範囲: 80% - 95%
    return random.random() <= hit_chance
```

### ⚔️ 物理攻撃ダメージ

```python
def calculate_physical_damage(attacker: Character, defender: Character):
    # 基本ダメージ（±15の変動）
    base_damage = attacker.attack + random.randint(-15, 15)
    
    # 防御力適用
    effective_defense = defender.defense
    damage = max(1, base_damage - effective_defense + random.randint(-5, 5))
    
    return damage
```

### 🔮 魔法攻撃ダメージ

```python
def calculate_magic_damage(attacker: Character, defender: Character):
    # 基本ダメージ（±10の変動）
    base_damage = attacker.magic + random.randint(-10, 10)
    
    # 防御力半減効果
    effective_defense = max(0, defender.defense * 0.5)
    damage = max(1, base_damage - effective_defense + random.randint(-5, 5))
    
    return damage
```

### ⭐ クリティカルヒット

```python
def check_critical_hit(action_type: str):
    critical_chance = 0.05  # 基本5%
    
    if action_type == "magic":
        critical_chance *= 0.7  # 魔法は3.5%
    
    is_critical = random.random() < critical_chance
    multiplier = 2.0 if is_critical else 1.0
    
    return is_critical, multiplier
```

---

## 特殊システム

### 🛡️ 防御力システム

| 攻撃タイプ | 防御力効果 |
|---|---|
| **物理攻撃** | フル防御力適用 |
| **魔法攻撃** | 防御力50%軽減 |

### 🎯 命中率システム

```python
# 素早さ差による命中率変動
base_hit_rate = 85%
speed_bonus = (attacker_speed - defender_speed) * 0.1%
final_hit_rate = clamp(base_hit_rate + speed_bonus, 80%, 95%)
```

### 🎪 確率テーブル

| 要素 | 基本確率 | 条件修正 |
|---|---|---|
| **魔法使用** | `min(40%, magic/200)` | 高防御相手+20%, 瀕死相手+15% |
| **クリティカル** | 5% | 魔法時は3.5% |
| **命中** | 85% | 素早さ差で80-95%の範囲 |

---

## バランス調整

### 💪 ステータス影響度

```python
# 各ステータスの重要度
HP:      生存時間に直結（高重要度）
Attack:  物理ダメージの主力（中重要度）
Defense: 被ダメージ軽減（中重要度）
Speed:   先手＋命中率（高重要度）
Magic:   防御貫通＋行動選択（中重要度）
```

### 🎮 戦略的要素

1. **高攻撃型**: 素早い決着を狙う
2. **高防御型**: 持久戦で相手を消耗させる
3. **高素早さ型**: 先手と命中率で有利を取る
4. **高魔力型**: 防御力を無視した安定ダメージ
5. **バランス型**: 安定した戦績を残す

---

## 実装詳細

### 🗃️ データ構造

```python
class BattleTurn:
    turn_number: int
    attacker_id: str
    defender_id: str
    action_type: str     # "attack" or "magic"
    damage: int
    is_critical: bool
    is_miss: bool
    attacker_hp_after: int
    defender_hp_after: int

class Battle:
    id: str
    character1_id: str
    character2_id: str
    winner_id: Optional[str]
    battle_log: List[str]
    turns: List[BattleTurn]
    duration: float
    created_at: datetime
```

### 🎨 ログメッセージテンプレート

```python
# ミス
"💨 {attacker.name}の攻撃は外れた！"

# 物理攻撃
"⚔️ {attacker.name}の攻撃！ {defender.name}に{damage}ダメージ！"
"💥 {attacker.name}のクリティカル攻撃！ {defender.name}に{damage}ダメージ！"

# 魔法攻撃
"🔮 {attacker.name}の魔法攻撃！ {defender.name}に{damage}ダメージ！"
"✨ {attacker.name}のクリティカル魔法！ {defender.name}に{damage}ダメージ！"

# 勝敗
"🏆 {winner.name}の勝利！"
"⏰ 時間切れ！ {winner.name}の判定勝ち！"
```

### ⚙️ 設定値

```python
# config/settings.py
MAX_TURNS = 50
CRITICAL_CHANCE = 0.05
CRITICAL_MULTIPLIER = 2.0

# バトルスピード（秒）
battle_speed = 0.5  # ターン間の待機時間
```

### 🎵 視覚・音響演出

- **Pygame**: リアルタイム戦闘画面表示
- **BGM**: バトル中の背景音楽
- **効果音**: 攻撃・魔法・クリティカルの音響効果
- **アニメーション**: キャラクタースプライトの動き

---

## 📚 関連ファイル

| ファイル | 役割 |
|---|---|
| `src/services/battle_engine.py` | メインバトルロジック |
| `src/models/character.py` | キャラクターモデル |
| `src/models/battle.py` | バトル・ターンモデル |
| `config/settings.py` | バトル設定値 |
| `src/services/database_manager.py` | バトル結果保存 |

---

*このドキュメントは お絵描きバトラー v1.0 の仕様に基づいています。*
*最終更新: 2025年1月*