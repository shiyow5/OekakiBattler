# お絵描きバトラー システム詳細マニュアル (完全版)

**生成日時:** 2025年10月08日 12:32:02

**バージョン:** 1.0.0

---

このドキュメントは、お絵描きバトラーシステムの全マニュアルを統合したものです。

---



================================================================================

# お絵描きバトラー システム詳細マニュアル

## マニュアル目次

本マニュアルは、お絵描きバトラーシステムの全機能と仕様を網羅した技術文書です。

### マニュアル構成

1. **[01_SYSTEM_OVERVIEW.md](01_SYSTEM_OVERVIEW.md)** - システム概要
   - システムアーキテクチャ
   - 技術スタック
   - データフロー
   - コンポーネント構成

2. **[02_INSTALLATION.md](02_INSTALLATION.md)** - インストールとセットアップ
   - 必要な環境
   - 依存関係のインストール
   - 環境変数の設定
   - Google API設定
   - プラットフォーム別セットアップ

3. **[03_CHARACTER_MANAGEMENT.md](03_CHARACTER_MANAGEMENT.md)** - キャラクター管理
   - キャラクターデータモデル
   - 画像処理パイプライン
   - AI分析システム
   - キャラクター登録フロー
   - ステータス生成ロジック

4. **[04_BATTLE_SYSTEM.md](04_BATTLE_SYSTEM.md)** - バトルシステム
   - バトルエンジン仕様
   - ダメージ計算式
   - 特殊効果（クリティカル、ガードブレイク等）
   - ターン処理フロー
   - バトル統計データ

5. **[05_STORY_MODE.md](05_STORY_MODE.md)** - ストーリーモード
   - ストーリーモード仕様
   - ボス管理システム
   - 進行状況管理
   - ボス作成・編集

6. **[06_DATA_MANAGEMENT.md](06_DATA_MANAGEMENT.md)** - データ管理
   - オンライン/オフラインモード
   - Google Sheets統合
   - SQLiteデータベース
   - 画像ストレージ
   - データ同期

7. **[07_LINE_BOT.md](07_LINE_BOT.md)** - LINE Bot連携
   - LINE Bot アーキテクチャ
   - Webhook設定
   - Google Apps Script連携
   - 画像アップロードフロー

8. **[08_TROUBLESHOOTING.md](08_TROUBLESHOOTING.md)** - トラブルシューティング
   - よくある問題と解決方法
   - エラーメッセージ一覧
   - デバッグ方法
   - ログ解析

9. **[09_API_REFERENCE.md](09_API_REFERENCE.md)** - API リファレンス
   - クラス・メソッド仕様
   - パラメータ詳細
   - 戻り値定義
   - 使用例

---

## マニュアルの使い方

### 初めてのユーザー
1. [01_SYSTEM_OVERVIEW.md](01_SYSTEM_OVERVIEW.md)でシステム全体を理解
2. [02_INSTALLATION.md](02_INSTALLATION.md)で環境構築
3. [03_CHARACTER_MANAGEMENT.md](03_CHARACTER_MANAGEMENT.md)でキャラクター作成方法を学習

### 開発者
- [09_API_REFERENCE.md](09_API_REFERENCE.md)で各クラス・メソッドの仕様を確認
- [01_SYSTEM_OVERVIEW.md](01_SYSTEM_OVERVIEW.md)でアーキテクチャを理解
- [08_TROUBLESHOOTING.md](08_TROUBLESHOOTING.md)でデバッグ方法を確認

### 機能別リファレンス
- バトルシステムの詳細 → [04_BATTLE_SYSTEM.md](04_BATTLE_SYSTEM.md)
- ストーリーモードの使い方 → [05_STORY_MODE.md](05_STORY_MODE.md)
- データ管理の仕組み → [06_DATA_MANAGEMENT.md](06_DATA_MANAGEMENT.md)

---

## バージョン情報

- **マニュアルバージョン**: 1.0.0
- **対応システムバージョン**: お絵描きバトラー v1.x
- **最終更新日**: 2025-10-08

---

## 記号の意味

| 記号 | 意味 |
|------|------|
| ✅ | 正常動作・推奨事項 |
| ⚠️ | 注意事項 |
| ❌ | 非推奨・禁止事項 |
| 💡 | ヒント・Tips |
| 🔧 | 設定・調整が必要 |
| 📊 | データ・統計情報 |
| 🔒 | セキュリティ関連 |

---

## サポート情報

### 問題報告
バグや不具合を発見した場合は、以下の情報を含めて報告してください：
- エラーメッセージ
- 再現手順
- 環境情報（OS、Pythonバージョン等）
- ログファイル

### 開発環境
- **Python**: 3.11+
- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **必須ライブラリ**: requirements.txt参照

---

## ライセンス

本マニュアルは、お絵描きバトラーシステムの一部として提供されます。


================================================================================

# 01. システム概要

## 1.1 システムの目的

お絵描きバトラーは、手描きのキャラクターイラストをAI解析によってRPG風のステータスに変換し、自動対戦させるシステムです。

### 主な特徴
- 📝 **アナログ描画対応**: 紙に描いたキャラクターをスキャン・撮影して利用可能
- 🤖 **AI自動解析**: Google Gemini AIがイラストからステータスを生成
- ⚔️ **完全自動バトル**: ユーザー操作なしで戦闘が進行
- 📊 **データ永続化**: Google SheetsまたはSQLiteでデータ管理
- 📱 **LINE Bot連携**: LINEからキャラクター画像を直接登録可能

---

## 1.2 システムアーキテクチャ

### 1.2.1 レイヤー構成

```
┌─────────────────────────────────────────────────────┐
│                 UI Layer (Tkinter/Pygame)           │
│  - メインメニュー (main_menu.py)                      │
│  - バトル画面 (Pygameフルスクリーン)                   │
│  - ストーリーボス管理UI (story_boss_manager.py)       │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│              Services Layer (ビジネスロジック)        │
│  - AIアナライザー (ai_analyzer.py)                    │
│  - 画像プロセッサー (image_processor.py)              │
│  - バトルエンジン (battle_engine.py)                  │
│  - ストーリーモードエンジン (story_mode_engine.py)     │
│  - エンドレスバトルエンジン (endless_battle_engine.py) │
│  - シートマネージャー (sheets_manager.py)             │
│  - データベースマネージャー (database_manager.py)      │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│              Models Layer (データ定義)                │
│  - Character (Pydantic)                             │
│  - Battle (Pydantic)                                │
│  - StoryBoss (Pydantic)                             │
│  - StoryProgress (Pydantic)                         │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│          Data Storage Layer (永続化)                 │
│  - Google Sheets (オンラインモード)                   │
│  - Google Drive (画像保存)                           │
│  - SQLite (オフラインモード)                          │
│  - ローカルファイルシステム (画像キャッシュ)            │
└─────────────────────────────────────────────────────┘
```

### 1.2.2 外部システム連携

```
┌──────────────┐
│  LINE Bot    │
│  (Node.js)   │
└──────┬───────┘
       │ Webhook
       ↓
┌──────────────────┐
│ Google Apps      │
│ Script (GAS)     │
│ - 画像保存        │
│ - Sheets書き込み  │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐        ┌──────────────────┐
│ Google Drive     │←───────│ Google Sheets    │
│ (画像保存)        │        │ (データ管理)      │
└──────────────────┘        └──────────────────┘
       ↑                             ↑
       │                             │
       └─────────────┬───────────────┘
                     │
              ┌──────┴───────┐
              │ Main App     │
              │ (Python)     │
              └──────────────┘
```

---

## 1.3 技術スタック

### 1.3.1 コア技術

| カテゴリ | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| 言語 | Python | 3.11+ | メインアプリケーション |
| GUI | Tkinter | 標準ライブラリ | メニューUI |
| グラフィックス | Pygame | 2.x | バトル画面描画 |
| 画像処理 | Pillow | 10.x | 画像操作 |
| 画像処理 | OpenCV | 4.x | 背景除去・スプライト抽出 |
| データ検証 | Pydantic | 2.x | モデル定義・バリデーション |
| AI | Google Generative AI | 最新 | キャラクター解析 |
| データベース | SQLAlchemy + SQLite | 2.x | オフラインデータ管理 |

### 1.3.2 外部サービス

| サービス | 用途 | API |
|---------|------|-----|
| Google Gemini AI | イラストからステータス生成 | Generative AI API |
| Google Sheets | オンラインデータ管理 | Sheets API v4 |
| Google Drive | 画像保存・共有 | Drive API v3 |
| LINE Messaging API | LINE Bot連携 | Messaging API |

### 1.3.3 LINE Bot (オプション)

| カテゴリ | 技術 | バージョン |
|---------|------|-----------|
| ランタイム | Node.js | 14+ |
| フレームワーク | Express | 4.x |
| LINE SDK | @line/bot-sdk | 最新 |
| トンネリング | ngrok | 3.x |

---

## 1.4 データフロー

### 1.4.1 キャラクター登録フロー

```
[手描きイラスト]
      ↓
[スキャン/撮影] → 画像ファイル (PNG/JPG)
      ↓
[画像アップロード]
      ↓
┌──────────────────────────────────┐
│ 画像処理パイプライン               │
│ 1. 背景除去                       │
│ 2. スプライト抽出                  │
│ 3. リサイズ・最適化                │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│ AI解析 (Google Gemini)            │
│ - イラストの視覚的特徴を分析        │
│ - HP, 攻撃, 防御等のステータス生成  │
│ - キャラクター説明文生成            │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│ データ検証 (Pydantic)              │
│ - ステータス範囲チェック            │
│ - 合計値制限チェック (≤350)        │
│ - 必須フィールド検証                │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│ データ永続化                       │
│ - オンライン: Google Sheets/Drive  │
│ - オフライン: SQLite + ローカル保存 │
└──────────────────────────────────┘
```

### 1.4.2 バトル実行フロー

```
[バトル開始]
      ↓
┌──────────────────────────────────┐
│ キャラクターデータ読み込み          │
│ - DB/Sheetsから取得               │
│ - スプライト画像ロード              │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│ バトルエンジン初期化               │
│ - HP設定                          │
│ - ターン順決定 (速さ依存)          │
│ - 初期配置                         │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│ ターン処理ループ (最大100ターン)    │
│ ┌──────────────────────────────┐ │
│ │ 1. 行動順決定                 │ │
│ │ 2. 攻撃タイプ選択 (物理/魔法)  │ │
│ │ 3. ダメージ計算               │ │
│ │ 4. 特殊効果判定               │ │
│ │    - クリティカル (5-35%)     │ │
│ │    - ガードブレイク (15-30%)  │ │
│ │    - 回避 (速さ・運依存)      │ │
│ │ 5. HP更新                     │ │
│ │ 6. 画面描画                   │ │
│ └──────────────────────────────┘ │
│         ↓                         │
│   [HP ≤ 0 or ターン上限?]         │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│ バトル結果処理                     │
│ - 勝敗判定                         │
│ - 統計データ計算                   │
│ - 戦績更新 (Wins/Losses/Draws)    │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│ データ保存                         │
│ - BattleHistoryシート (オンライン) │
│ - Rankingsシート更新               │
│ - キャラクター戦績更新              │
└──────────────────────────────────┘
```

---

## 1.5 コンポーネント構成

### 1.5.1 ディレクトリ構造

```
OekakiBattler/
├── main.py                     # エントリーポイント
├── img2txt.py                  # スタンドアロン画像解析ツール
├── config/
│   ├── settings.py            # 環境変数・定数管理
│   └── database.py            # SQLAlchemy設定
├── src/
│   ├── models/                # データモデル (Pydantic)
│   │   ├── character.py
│   │   ├── battle.py
│   │   ├── story_boss.py
│   │   └── story_progress.py
│   ├── services/              # ビジネスロジック
│   │   ├── ai_analyzer.py
│   │   ├── image_processor.py
│   │   ├── battle_engine.py
│   │   ├── story_mode_engine.py
│   │   ├── endless_battle_engine.py
│   │   ├── sheets_manager.py
│   │   ├── database_manager.py
│   │   ├── audio_manager.py
│   │   └── settings_manager.py
│   ├── ui/                    # ユーザーインターフェース
│   │   ├── main_menu.py
│   │   └── story_boss_manager.py
│   └── utils/                 # ユーティリティ
│       ├── image_utils.py
│       └── file_utils.py
├── server/                    # LINE Bot (Node.js)
│   ├── server.js
│   └── package.json
├── assets/                    # リソースファイル
│   ├── images/               # 背景画像・UI素材
│   └── sounds/               # 効果音
├── data/                      # データ保存先
│   ├── database.db           # SQLiteデータベース
│   ├── characters/           # オリジナル画像
│   └── sprites/              # スプライト画像
├── tests/                     # テストコード
└── docs/                      # ドキュメント
    └── manual/               # システムマニュアル
```

### 1.5.2 主要クラス関係図

```
┌────────────────┐
│  MainMenu      │ (Tkinter GUI)
└───────┬────────┘
        │ has-a
        ├──→ ┌──────────────────┐
        │    │ SheetsManager    │ (オンラインモード)
        │    └──────────────────┘
        │
        ├──→ ┌──────────────────┐
        │    │ DatabaseManager  │ (オフラインモード)
        │    └──────────────────┘
        │
        ├──→ ┌──────────────────┐
        │    │ AIAnalyzer       │
        │    └──────────────────┘
        │
        ├──→ ┌──────────────────┐
        │    │ ImageProcessor   │
        │    └──────────────────┘
        │
        └──→ ┌──────────────────┐
             │ BattleEngine     │
             └──────────────────┘
                      │ uses
                      ├──→ Character (model)
                      └──→ Battle (model)
```

---

## 1.6 動作モード

### 1.6.1 オンラインモード

**条件:**
- `credentials.json` が存在
- Google Sheets API が有効
- スプレッドシートが共有されている
- インターネット接続あり

**機能:**
- ✅ Google Sheetsでデータ管理
- ✅ Google Driveに画像保存
- ✅ バトル履歴記録
- ✅ ランキング自動更新
- ✅ ストーリーモード進行状況保存
- ✅ 複数デバイスでデータ共有可能

### 1.6.2 オフラインモード

**条件:**
- オンラインモード要件が満たされない場合に自動フォールバック

**機能:**
- ✅ SQLiteでローカルデータ管理
- ✅ ローカルファイルシステムに画像保存
- ✅ キャラクター登録・バトル実行可能
- ❌ バトル履歴記録なし
- ❌ ランキング機能なし
- ❌ ストーリーモード進行状況保存なし
- ❌ デバイス間データ共有不可

### 1.6.3 モード判定ロジック

```python
# config/settings.py または SheetsManager.__init__
try:
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_PATH,
        scopes=SCOPES
    )
    self.client = gspread.authorize(credentials)
    self.sheet = self.client.open_by_key(SPREADSHEET_ID)
    self.online_mode = True
except Exception:
    self.online_mode = False
    # SQLiteモードにフォールバック
```

---

## 1.7 セキュリティ考慮事項

### 1.7.1 機密情報管理

🔒 **環境変数で管理 (`.env`)**
```bash
GOOGLE_API_KEY=xxxxx          # Google Gemini AI
SPREADSHEET_ID=xxxxx
GOOGLE_CREDENTIALS_PATH=credentials.json
```

🔒 **Git除外設定 (`.gitignore`)**
```
.env
server/.env
credentials.json
*.db
```

### 1.7.2 API キー保護

- ⚠️ Google API キーは本番環境では IP 制限・ドメイン制限を設定
- ⚠️ サービスアカウントの権限は最小限に制限
- ⚠️ LINE Bot のチャネルシークレットは必ず環境変数で管理

### 1.7.3 データアクセス制御

- Google Sheets: サービスアカウントメールアドレスに編集権限を付与
- Google Drive: フォルダ共有設定でアクセス制御
- SQLite: ローカルファイルシステムの権限に依存

---

## 1.8 パフォーマンス特性

### 1.8.1 処理時間目安

| 処理 | 所要時間 | 備考 |
|------|---------|------|
| キャラクター登録 (AI解析含む) | 5-15秒 | Google Gemini APIのレスポンス時間に依存 |
| 画像処理 (背景除去・スプライト抽出) | 2-5秒 | 画像サイズに依存 |
| バトル1ターン描画 | 0.1-2.0秒 | 設定で調整可能 |
| 完全バトル (平均30ターン) | 3-60秒 | バトルスピード設定に依存 |
| Google Sheets書き込み | 1-3秒 | ネットワーク速度に依存 |
| Google Drive画像アップロード | 2-10秒 | 画像サイズ・ネットワーク速度に依存 |

### 1.8.2 キャッシュ戦略

**画像キャッシュ:**
- オンラインモードでもスプライト画像はローカルキャッシュ
- オリジナル画像はキャッシュせず、都度Drive URLから取得
- キャッシュ保存先: `data/sprites/{character_id}_sprite.png`

**データキャッシュ:**
- キャラクターリストはメモリ上にキャッシュ (GUIで保持)
- バトル実行時に最新データを再取得

### 1.8.3 API レート制限

| API | 制限 | 対策 |
|-----|------|------|
| Google Sheets API | 100 requests/100 seconds/user | バッチ更新の実装 |
| Google Drive API | 1000 requests/100 seconds/user | 画像キャッシュの活用 |
| Google Gemini API | プロジェクトによる | リトライ処理実装 |

---

## 1.9 制約事項

### 1.9.1 システム制約

| 項目 | 制約 | 理由 |
|------|------|------|
| キャラクター総ステータス | 最大350 | バランス調整 |
| ボス総ステータス | 最大500 | プレイヤーキャラより強力 |
| バトル最大ターン数 | 100ターン | 無限ループ防止 |
| 画像フォーマット | PNG, JPG, JPEG | Pillowサポート形式 |
| 画像最大サイズ | 制限なし (推奨: 10MB以下) | API制限・処理時間考慮 |

### 1.9.2 機能制約

**オフラインモード:**
- ❌ バトル履歴保存不可
- ❌ ランキング機能なし
- ❌ ストーリーモード進行状況保存なし

**LINE Bot:**
- ✅ 画像送信のみサポート
- ❌ テキストコマンドは未実装
- ❌ バトル実行は未実装

---

## 1.10 将来的な拡張性

### 1.10.1 アーキテクチャ上の拡張ポイント

**Webアプリケーション化:**
- UIレイヤーをFlask/FastAPI + Reactに置き換え
- Services/Modelsレイヤーはそのまま流用可能

**マルチプレイヤー対応:**
- WebSocket導入でリアルタイムバトル
- Redisでセッション管理

**モバイルアプリ化:**
- REST API実装
- React Native/Flutterクライアント

### 1.10.2 機能拡張候補

- [ ] キャラクター編集機能
- [ ] トーナメントブラケット表示
- [ ] キャラクター成長システム
- [ ] 高度なAIモデル (GPT-4V, Claude Vision)
- [ ] リアルタイム観戦機能
- [ ] キャラクターマーケットプレイス

---

## 次のセクション

次は [02_INSTALLATION.md](02_INSTALLATION.md) でインストール手順を確認してください。


================================================================================

# 02. インストールとセットアップ

## 2.1 システム要件

### 2.1.1 ハードウェア要件

| 項目 | 最小要件 | 推奨要件 |
|------|---------|---------|
| CPU | 2コア 2GHz | 4コア 3GHz以上 |
| メモリ | 4GB RAM | 8GB RAM以上 |
| ストレージ | 2GB空き容量 | 10GB空き容量 |
| ディスプレイ | 1024x768 | 1920x1080以上 |
| ネットワーク | - | 安定したインターネット接続 (オンラインモード用) |

### 2.1.2 ソフトウェア要件

**必須:**
- Python 3.11 以上
- pip (Pythonパッケージマネージャー)

**オプション (LINE Bot使用時):**
- Node.js 14 以上
- npm
- ngrok

### 2.1.3 対応OS

| OS | バージョン | 状態 |
|----|-----------|------|
| Windows | 10, 11 | ✅ 完全対応 |
| macOS | 10.15 (Catalina) 以上 | ✅ 完全対応 |
| Linux (Ubuntu) | 20.04 LTS 以上 | ✅ 完全対応 |
| Linux (Debian) | 11 以上 | ✅ 完全対応 |

---

## 2.2 Pythonのインストール

### 2.2.1 Windows

**方法1: 公式インストーラー (推奨)**
```powershell
# 1. https://www.python.org/downloads/ から最新版をダウンロード
# 2. インストーラー実行時に "Add Python to PATH" をチェック
# 3. インストール完了後、確認:
python --version
# Python 3.11.x と表示されればOK
```

**方法2: Microsoft Store**
```powershell
# Microsoft StoreからPython 3.11を検索してインストール
python --version
```

### 2.2.2 macOS

**方法1: Homebrew (推奨)**
```bash
# Homebrewがない場合はインストール
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 3.11をインストール
brew install python@3.11

# 確認
python3.11 --version
```

**方法2: 公式インストーラー**
```bash
# https://www.python.org/downloads/macos/ からダウンロード
# インストール後
python3 --version
```

### 2.2.3 Linux (Ubuntu/Debian)

```bash
# システムパッケージを更新
sudo apt-get update

# Python 3.11をインストール
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip

# 確認
python3.11 --version
```

---

## 2.3 プロジェクトのセットアップ

### 2.3.1 リポジトリのクローン

```bash
# GitHubからクローン (プライベートリポジトリの場合)
git clone https://github.com/your-username/OekakiBattler.git
cd OekakiBattler

# または、ZIPファイルを展開してcd
cd OekakiBattler
```

### 2.3.2 仮想環境の作成と有効化

**Windows:**
```powershell
# 仮想環境作成
python -m venv .venv

# 有効化
.venv\Scripts\activate

# プロンプトが (.venv) で始まればOK
```

**macOS/Linux:**
```bash
# 仮想環境作成
python3.11 -m venv .venv

# 有効化
source .venv/bin/activate

# プロンプトが (.venv) で始まればOK
```

### 2.3.3 依存関係のインストール

```bash
# pip を最新版に更新
pip install --upgrade pip

# 全パッケージをインストール
pip install -r requirements.txt

# インストール確認
pip list
```

**主要パッケージ:**
```
pygame>=2.5.0
Pillow>=10.0.0
opencv-python>=4.8.0
google-generativeai>=0.3.0
gspread>=5.10.0
google-auth>=2.22.0
google-api-python-client>=2.95.0
pydantic>=2.0.0
python-dotenv>=1.0.0
SQLAlchemy>=2.0.0
```

---

## 2.4 プラットフォーム別追加セットアップ

### 2.4.1 Windows

**Tkinter確認:**
```python
# Pythonインタープリタで実行
import tkinter
tkinter._test()
# 小さなウィンドウが表示されればOK
```

**Visual C++ 再頒布可能パッケージ (一部依存関係に必要):**
- https://aka.ms/vs/17/release/vc_redist.x64.exe からダウンロード・インストール

### 2.4.2 macOS

**Xcode Command Line Tools:**
```bash
xcode-select --install
```

**Tkinter確認:**
```bash
python3.11 -m tkinter
# 小さなウィンドウが表示されればOK
```

### 2.4.3 Linux (Ubuntu/Debian)

**システムライブラリのインストール:**
```bash
sudo apt-get install -y \
    python3-tk \
    libgl1-mesa-glx \
    libglib2.0-0 \
    fonts-noto-cjk \
    fonts-takao-gothic
```

**Tkinter確認:**
```bash
python3.11 -m tkinter
# 小さなウィンドウが表示されればOK
```

---

## 2.5 環境変数の設定

### 2.5.1 `.env` ファイルの作成

プロジェクトルートに `.env` ファイルを作成:

```bash
# .env.example をコピーして編集
cp .env.example .env

# エディタで開く
nano .env  # または vim, code 等
```

### 2.5.2 必須環境変数

```bash
# Google Generative AI (必須)
GOOGLE_API_KEY=your_google_api_key_here
MODEL_NAME=gemini-2.5-flash-lite-preview-06-17

# Google Sheets (オンラインモード用)
SPREADSHEET_ID=your_spreadsheet_id_here
WORKSHEET_NAME=Characters
BATTLE_HISTORY_SHEET=BattleHistory
RANKING_SHEET=Rankings
GOOGLE_CREDENTIALS_PATH=credentials.json

# Google Drive (オプション: 特定フォルダに保存したい場合)
DRIVE_FOLDER_ID=your_drive_folder_id_here
```

### 2.5.3 環境変数の説明

| 変数名 | 説明 | 取得方法 |
|--------|------|---------|
| `GOOGLE_API_KEY` | Google Gemini AI APIキー | [2.6.1](#261-google-gemini-ai-api) 参照 |
| `MODEL_NAME` | 使用するGeminiモデル | デフォルト値使用推奨 |
| `SPREADSHEET_ID` | Google SheetsのID | [2.6.2](#262-google-sheets-api) 参照 |
| `WORKSHEET_NAME` | キャラクターシート名 | デフォルト: `Characters` |
| `BATTLE_HISTORY_SHEET` | バトル履歴シート名 | デフォルト: `BattleHistory` |
| `RANKING_SHEET` | ランキングシート名 | デフォルト: `Rankings` |
| `GOOGLE_CREDENTIALS_PATH` | サービスアカウントJSON | [2.6.2](#262-google-sheets-api) 参照 |
| `DRIVE_FOLDER_ID` | DriveフォルダID (オプション) | [2.6.3](#263-google-drive-api) 参照 |

---

## 2.6 Google API設定

### 2.6.1 Google Gemini AI API

**1. Google AI Studioにアクセス:**
- https://makersuite.google.com/app/apikey

**2. APIキーを作成:**
- "Get API Key" または "APIキーを作成" をクリック
- 新しいプロジェクトを作成、または既存プロジェクトを選択
- APIキーが生成される (例: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

**3. `.env` に設定:**
```bash
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**⚠️ セキュリティ注意:**
- APIキーは絶対にGitにコミットしない
- 本番環境ではIP制限を設定
- 定期的にキーをローテーション

### 2.6.2 Google Sheets API

**1. Google Cloud Consoleでプロジェクト作成:**
- https://console.cloud.google.com/
- 新しいプロジェクトを作成 (例: "OekakiBattler")

**2. 必要なAPIを有効化:**
```
Google Sheets API
Google Drive API
```
- 「APIとサービス」→「ライブラリ」から検索して有効化

**3. サービスアカウントを作成:**
- 「APIとサービス」→「認証情報」→「認証情報を作成」→「サービスアカウント」
- サービスアカウント名: `oekaki-battler-service`
- 役割: `編集者` (Editor)

**4. JSONキーをダウンロード:**
- 作成したサービスアカウントをクリック
- 「キー」タブ→「鍵を追加」→「新しい鍵を作成」
- 形式: JSON
- ダウンロードしたファイルを `credentials.json` としてプロジェクトルートに配置

**5. スプレッドシートを作成・共有:**
```bash
# 1. Google Sheetsで新しいスプレッドシートを作成
# 2. URLからスプレッドシートIDを取得
#    例: https://docs.google.com/spreadsheets/d/1AbC123XyZ.../edit
#    → スプレッドシートID = 1AbC123XyZ...
# 3. サービスアカウントのメールアドレス (credentials.jsonの "client_email") と共有
#    権限: 編集者
```

**6. `.env` に設定:**
```bash
SPREADSHEET_ID=1AbC123XyZ...
GOOGLE_CREDENTIALS_PATH=credentials.json
```

### 2.6.3 Google Drive API

**前提:** Google Sheets API設定が完了していること (2.6.2)

**1. Drive APIを有効化:**
- Google Cloud Consoleで「Google Drive API」を有効化 (2.6.2で実施済み)

**2. 保存先フォルダを作成 (オプション):**
```bash
# 1. Google Driveで新しいフォルダを作成 (例: "OekakiBattler_Images")
# 2. URLからフォルダIDを取得
#    例: https://drive.google.com/drive/folders/1XyZ987AbC...
#    → フォルダID = 1XyZ987AbC...
# 3. サービスアカウントと共有 (編集者権限)
```

**3. `.env` に設定 (オプション):**
```bash
DRIVE_FOLDER_ID=1XyZ987AbC...
```

💡 **ヒント:** `DRIVE_FOLDER_ID` を設定しない場合、画像はマイドライブのルートに保存されます。

---

## 2.7 データベースの初期化

### 2.7.1 Google Sheets (オンラインモード)

アプリケーション初回起動時に自動的にシートが作成されます:

**作成されるシート:**
1. `Characters` (15列) - キャラクターデータ
2. `BattleHistory` (15列) - バトル履歴
3. `Rankings` (10列) - ランキング
4. `StoryBosses` (11列) - ストーリーボスデータ
5. `StoryProgress` (6列) - ストーリー進行状況

**手動で作成する場合:**
```bash
python -c "from src.services.sheets_manager import SheetsManager; SheetsManager().initialize_sheets()"
```

### 2.7.2 SQLite (オフラインモード)

初回起動時に自動的に `data/database.db` が作成されます。

**手動で作成する場合:**
```bash
python -c "from config.database import init_db; init_db()"
```

**データベース構造確認:**
```bash
sqlite3 data/database.db
.schema characters
.schema battles
.exit
```

---

## 2.8 LINE Bot セットアップ (オプション)

### 2.8.1 Node.js のインストール

**Windows:**
- https://nodejs.org/ から LTS版をダウンロード・インストール

**macOS:**
```bash
brew install node
```

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**確認:**
```bash
node --version  # v14.x 以上
npm --version   # 6.x 以上
```

### 2.8.2 LINE Developersでチャネル作成

**1. LINE Developersコンソールにアクセス:**
- https://developers.line.biz/console/

**2. 新規プロバイダー作成:**
- プロバイダー名: 任意 (例: "OekakiBattler")

**3. Messaging APIチャネル作成:**
- チャネル名: 任意 (例: "お絵描きバトラー")
- チャネル説明: 任意
- 業種: 任意
- メールアドレス: 自分のメールアドレス

**4. 必要な情報を取得:**
```
チャネルシークレット: [基本設定] タブ
チャネルアクセストークン: [Messaging API設定] タブ → [チャネルアクセストークン (長期)] 発行
```

### 2.8.3 ngrok のインストール

**公式サイトからダウンロード:**
- https://ngrok.com/download

**またはパッケージマネージャー:**
```bash
# macOS
brew install ngrok

# Linux
snap install ngrok

# Windows
choco install ngrok
```

**認証トークン設定:**
```bash
# ngrokにサインアップ後、ダッシュボードから認証トークン取得
ngrok authtoken YOUR_AUTH_TOKEN
```

### 2.8.4 LINE Bot サーバーのセットアップ

**1. サーバーディレクトリに移動:**
```bash
cd server
```

**2. 依存パッケージをインストール:**
```bash
npm install
```

**3. `.env` ファイルを作成:**
```bash
# server/.env
PORT=3000
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
GAS_WEBHOOK_URL=https://script.google.com/macros/s/YOUR_GAS_ID/exec
SHARED_SECRET=your_shared_secret_for_gas_authentication
```

**4. Google Apps Script (GAS) の設定:**

**GASコードをデプロイ:**
```javascript
// Google Apps Scriptエディタで以下を作成
// 詳細は 07_LINE_BOT.md 参照

function doPost(e) {
  // LINEから受信した画像をDriveに保存
  // Sheetsに記録
  // 詳細実装は 07_LINE_BOT.md
}
```

**5. サーバー起動スクリプト:**

**Windows (`server_up.bat`):**
```batch
@echo off
cd server
start ngrok http 3000
timeout /t 5
node server.js
```

**macOS/Linux (`server_up.sh`):**
```bash
#!/bin/bash
cd server
ngrok http 3000 &
sleep 5
node server.js
```

**6. サーバー起動:**
```bash
# プロジェクトルートで
./server_up.sh  # macOS/Linux
# または
server_up.bat   # Windows
```

**7. Webhook URLの設定:**
```bash
# ngrokが表示するHTTPS URL (例: https://xxxx-xx-xx-xxx-xxx.ngrok.io)
# LINE Developers Console → Messaging API設定 → Webhook URL に設定
# 例: https://xxxx-xx-xx-xxx-xxx.ngrok.io/webhook
```

---

## 2.9 インストール確認

### 2.9.1 基本動作確認

```bash
# 仮想環境を有効化
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate     # Windows

# メインアプリケーションを起動
python main.py
```

**確認項目:**
- ✅ Tkinterウィンドウが表示される
- ✅ ステータスバーに「オンラインモード」または「オフラインモード」が表示される
- ✅ 「キャラクター登録」ボタンがクリック可能

### 2.9.2 Google API接続確認

**オンラインモード確認:**
```python
# Pythonインタープリタで実行
from src.services.sheets_manager import SheetsManager

manager = SheetsManager()
print(f"Online Mode: {manager.online_mode}")
# True なら成功

# キャラクターリスト取得
characters = manager.get_all_characters()
print(f"Characters: {len(characters)}")
```

**AI解析確認:**
```bash
# スタンドアロン画像解析ツールで確認
python img2txt.py path/to/test_image.png
# ステータスが表示されればOK
```

### 2.9.3 LINE Bot接続確認

**1. サーバー起動:**
```bash
./server_up.sh
```

**2. LINE Developersコンソールで検証:**
- Messaging API設定 → Webhook設定 → 検証ボタン
- "Success" と表示されればOK

**3. 実際に画像送信:**
- LINE公式アカウントに画像を送信
- Google Sheetsに記録されるか確認

---

## 2.10 アップデート手順

### 2.10.1 コードのアップデート

```bash
# Gitから最新版を取得
git pull origin main

# 仮想環境を有効化
source .venv/bin/activate

# 依存パッケージを更新
pip install --upgrade -r requirements.txt

# LINE Botサーバー更新 (使用している場合)
cd server
npm install
cd ..
```

### 2.10.2 データベースマイグレーション

**SQLite:**
```bash
# マイグレーションスクリプトがある場合
python scripts/migrate_db.py
```

**Google Sheets:**
- 新しいシートが追加された場合、アプリ起動時に自動作成されます

### 2.10.3 設定ファイルの更新

```bash
# 新しい環境変数が追加された場合
# .env.example と自分の .env を比較
diff .env.example .env

# 不足している変数を追加
nano .env
```

---

## 2.11 アンインストール

### 2.11.1 アプリケーションの削除

```bash
# 1. 仮想環境を無効化
deactivate

# 2. プロジェクトディレクトリを削除
cd ..
rm -rf OekakiBattler

# Windows:
# rmdir /s /q OekakiBattler
```

### 2.11.2 Google API設定のクリーンアップ

**1. Google Cloud Console:**
- プロジェクトを削除 (課金が発生している場合)
- または、APIを無効化

**2. Google Sheets:**
- スプレッドシートを削除
- Google Driveのフォルダを削除

**3. LINE Developers:**
- チャネルを削除
- プロバイダーを削除 (他に使用していない場合)

### 2.11.3 ngrok のクリーンアップ

```bash
# プロセスを停止
pkill ngrok  # macOS/Linux
taskkill /F /IM ngrok.exe  # Windows

# アンインストール (オプション)
brew uninstall ngrok  # macOS
snap remove ngrok     # Linux
choco uninstall ngrok # Windows
```

---

## 2.12 よくあるインストール問題

### 2.12.1 Pythonパッケージのインストールエラー

**エラー: `Microsoft Visual C++ 14.0 is required`**
```powershell
# Windows: Visual Studio Build Toolsをインストール
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**エラー: `error: command 'gcc' failed`**
```bash
# Linux: ビルドツールをインストール
sudo apt-get install build-essential python3-dev
```

### 2.12.2 Tkinter が見つからない

**Linux:**
```bash
sudo apt-get install python3-tk
```

**macOS:**
```bash
# Homebrewで入れたPythonにはTkinterが含まれています
# システムPythonを使用している場合は、Homebrewで再インストール
brew install python-tk@3.11
```

### 2.12.3 OpenCV エラー

**エラー: `ImportError: libGL.so.1`**
```bash
# Linux
sudo apt-get install libgl1-mesa-glx libglib2.0-0
```

### 2.12.4 日本語フォントが表示されない

**Linux:**
```bash
sudo apt-get install fonts-noto-cjk fonts-takao-gothic
```

**macOS/Windows:**
- システムに日本語フォントが標準で含まれています

---

## 次のセクション

次は [03_CHARACTER_MANAGEMENT.md](03_CHARACTER_MANAGEMENT.md) でキャラクター管理の詳細を確認してください。


================================================================================

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


================================================================================

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


================================================================================

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


================================================================================

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


================================================================================

# 07. LINE Bot連携

## 7.1 LINE Bot アーキテクチャ

### 7.1.1 システム構成図

```
[LINEユーザー]
      ↓ 画像送信
┌──────────────────┐
│ LINE Platform    │
└─────┬────────────┘
      ↓ Webhook (HTTPS)
┌──────────────────┐
│ ngrok Tunnel     │
│ (ローカル開発用)  │
└─────┬────────────┘
      ↓ HTTP
┌──────────────────────────┐
│ Node.js Server           │
│ (Express + LINE SDK)     │
│ - Webhook受信            │
│ - 画像バイナリ取得        │
│ - GASへ転送              │
└─────┬────────────────────┘
      ↓ HTTPS POST
┌──────────────────────────┐
│ Google Apps Script (GAS) │
│ - 画像をDriveに保存       │
│ - Sheetsに記録            │
└──────────────────────────┘
```

### 7.1.2 データフロー

```
1. ユーザーがLINEで画像送信
   ↓
2. LINE Platformがwebhookを送信
   {
     "type": "message",
     "message": {
       "type": "image",
       "id": "message_id"
     }
   }
   ↓
3. Node.jsサーバーがWebhook受信
   ↓
4. LINE Messaging APIから画像取得
   GET https://api-data.line.me/v2/bot/message/{messageId}/content
   ↓
5. 画像をBase64エンコード
   ↓
6. GASにPOST
   {
     "image": "data:image/jpeg;base64,/9j/4AAQ...",
     "userId": "U1234567890abcdef...",
     "timestamp": "2025-10-08T10:30:00Z"
   }
   ↓
7. GASが画像をDriveに保存
   ↓
8. GASがSheetsに記録
   ↓
9. ユーザーに完了通知 (オプション)
```

---

## 7.2 Node.js サーバー

### 7.2.1 server.js 実装

**ファイル:** `server/server.js`

```javascript
const express = require('express');
const line = require('@line/bot-sdk');
const axios = require('axios');
require('dotenv').config();

// 環境変数
const config = {
  channelSecret: process.env.LINE_CHANNEL_SECRET,
  channelAccessToken: process.env.LINE_CHANNEL_ACCESS_TOKEN
};

const GAS_WEBHOOK_URL = process.env.GAS_WEBHOOK_URL;
const SHARED_SECRET = process.env.SHARED_SECRET;
const PORT = process.env.PORT || 3000;

// Express アプリ
const app = express();

// LINE SDK クライアント
const client = new line.Client(config);

// Webhook エンドポイント
app.post('/webhook', line.middleware(config), (req, res) => {
  Promise
    .all(req.body.events.map(handleEvent))
    .then((result) => res.json(result))
    .catch((err) => {
      console.error(err);
      res.status(500).end();
    });
});

// イベントハンドラー
async function handleEvent(event) {
  // メッセージイベントのみ処理
  if (event.type !== 'message') {
    return Promise.resolve(null);
  }

  // 画像メッセージのみ処理
  if (event.message.type !== 'image') {
    return client.replyMessage(event.replyToken, {
      type: 'text',
      text: '画像を送信してください'
    });
  }

  try {
    // 画像取得
    const imageBuffer = await getImageContent(event.message.id);

    // Base64エンコード
    const base64Image = imageBuffer.toString('base64');
    const dataUrl = `data:image/jpeg;base64,${base64Image}`;

    // GASに送信
    const gasResponse = await sendToGAS({
      image: dataUrl,
      userId: event.source.userId,
      timestamp: new Date(event.timestamp).toISOString()
    });

    // ユーザーに返信
    return client.replyMessage(event.replyToken, {
      type: 'text',
      text: `画像を受け取りました！\nDriveに保存しました。\nファイル名: ${gasResponse.fileName}`
    });

  } catch (error) {
    console.error('画像処理エラー:', error);
    return client.replyMessage(event.replyToken, {
      type: 'text',
      text: 'エラーが発生しました。もう一度試してください。'
    });
  }
}

// LINE Messaging APIから画像を取得
async function getImageContent(messageId) {
  const url = `https://api-data.line.me/v2/bot/message/${messageId}/content`;

  const response = await axios.get(url, {
    headers: {
      'Authorization': `Bearer ${config.channelAccessToken}`
    },
    responseType: 'arraybuffer'
  });

  return Buffer.from(response.data);
}

// GASに画像データを送信
async function sendToGAS(data) {
  const response = await axios.post(GAS_WEBHOOK_URL, {
    ...data,
    secret: SHARED_SECRET  // 認証用
  }, {
    headers: {
      'Content-Type': 'application/json'
    }
  });

  return response.data;
}

// サーバー起動
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
  console.log(`Webhook URL: http://localhost:${PORT}/webhook`);
});
```

### 7.2.2 package.json

```json
{
  "name": "oekaki-battler-line-bot",
  "version": "1.0.0",
  "description": "LINE Bot for OekakiBattler",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "@line/bot-sdk": "^7.5.0",
    "express": "^4.18.2",
    "axios": "^1.4.0",
    "dotenv": "^16.0.3"
  },
  "devDependencies": {
    "nodemon": "^2.0.22"
  }
}
```

### 7.2.3 環境変数設定

**ファイル:** `server/.env`

```bash
# LINEチャネル設定
LINE_CHANNEL_SECRET=your_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here

# Google Apps Script Webhook
GAS_WEBHOOK_URL=https://script.google.com/macros/s/YOUR_GAS_ID/exec

# 共有シークレット (GAS認証用)
SHARED_SECRET=your_shared_secret_here

# サーバーポート
PORT=3000
```

---

## 7.3 Google Apps Script (GAS)

### 7.3.1 GAS コード

**Google Apps Scriptエディタで作成:**

```javascript
// スプレッドシートID
const SPREADSHEET_ID = 'your_spreadsheet_id';
const SHEET_NAME = 'LINE_Uploads';

// DriveフォルダID
const DRIVE_FOLDER_ID = 'your_drive_folder_id';

// 共有シークレット (Node.jsサーバーと同じ値)
const SHARED_SECRET = 'your_shared_secret_here';

function doPost(e) {
  try {
    // リクエストボディ解析
    const data = JSON.parse(e.postData.contents);

    // 認証チェック
    if (data.secret !== SHARED_SECRET) {
      return ContentService.createTextOutput(JSON.stringify({
        error: 'Unauthorized'
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // 画像データ取得
    const imageData = data.image;  // data:image/jpeg;base64,xxxxx
    const userId = data.userId;
    const timestamp = data.timestamp;

    // Base64デコード
    const base64Data = imageData.split(',')[1];
    const blob = Utilities.newBlob(
      Utilities.base64Decode(base64Data),
      'image/jpeg',
      `line_${userId}_${Date.now()}.jpg`
    );

    // Driveに保存
    const folder = DriveApp.getFolderById(DRIVE_FOLDER_ID);
    const file = folder.createFile(blob);

    // 公開設定
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

    // ファイルURL
    const fileUrl = file.getUrl();
    const fileName = file.getName();

    // スプレッドシートに記録
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    let sheet = ss.getSheetByName(SHEET_NAME);

    // シートが存在しない場合は作成
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow(['Timestamp', 'User ID', 'File Name', 'File URL']);
    }

    // データ追加
    sheet.appendRow([
      timestamp,
      userId,
      fileName,
      fileUrl
    ]);

    // レスポンス
    return ContentService.createTextOutput(JSON.stringify({
      success: true,
      fileName: fileName,
      fileUrl: fileUrl
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    Logger.log('Error: ' + error.toString());

    return ContentService.createTextOutput(JSON.stringify({
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
```

### 7.3.2 GAS デプロイ手順

**1. Google Apps Script作成:**
```
1. https://script.google.com/ にアクセス
2. 「新しいプロジェクト」をクリック
3. プロジェクト名を「OekakiBattler LINE Bot」に変更
4. 上記コードを貼り付け
5. SPREADSHEET_ID, DRIVE_FOLDER_ID, SHARED_SECRET を設定
```

**2. Webアプリとしてデプロイ:**
```
1. 「デプロイ」→「新しいデプロイ」
2. 種類: Webアプリ
3. 説明: LINE Bot Webhook
4. 次のユーザーとして実行: 自分
5. アクセスできるユーザー: 全員
6. 「デプロイ」をクリック
7. Webアプリ URL をコピー (例: https://script.google.com/macros/s/XXXXX/exec)
```

**3. URLを環境変数に設定:**
```bash
# server/.env
GAS_WEBHOOK_URL=https://script.google.com/macros/s/XXXXX/exec
```

---

## 7.4 ngrok 設定

### 7.4.1 ngrok とは

- **目的:** ローカルサーバーを外部からHTTPSでアクセス可能にする
- **用途:** LINE WebhookはHTTPS必須のため、開発環境で必要

### 7.4.2 ngrok起動

```bash
# ngrokインストール済みの場合
ngrok http 3000

# 出力例:
# Forwarding  https://xxxx-xx-xx-xxx-xxx.ngrok.io -> http://localhost:3000
```

### 7.4.3 Webhook URL設定

**LINE Developers Console:**
```
1. https://developers.line.biz/console/ にアクセス
2. チャネルを選択
3. 「Messaging API設定」タブ
4. Webhook設定 → Webhook URL
5. ngrokのHTTPS URLを入力
   例: https://xxxx-xx-xx-xxx-xxx.ngrok.io/webhook
6. 「検証」ボタンで接続確認
7. 「Webhookの利用」をオン
```

### 7.4.4 起動スクリプト

**macOS/Linux (`server_up.sh`):**
```bash
#!/bin/bash

echo "Starting ngrok..."
ngrok http 3000 &

sleep 5

echo "Starting Node.js server..."
cd server
node server.js
```

**Windows (`server_up.bat`):**
```batch
@echo off
echo Starting ngrok...
start ngrok http 3000

timeout /t 5

echo Starting Node.js server...
cd server
node server.js
```

---

## 7.5 使い方

### 7.5.1 サーバー起動

```bash
# プロジェクトルートで
./server_up.sh  # macOS/Linux
# または
server_up.bat   # Windows
```

**確認事項:**
- ✅ ngrokが起動してHTTPS URLが表示される
- ✅ Node.jsサーバーが起動 (`Server listening on port 3000`)
- ✅ LINE Developers ConsoleでWebhook検証が成功

### 7.5.2 画像送信テスト

**手順:**
1. LINE公式アカウントを友だち追加
2. キャラクター画像を送信
3. Botから「画像を受け取りました！」メッセージが返信される
4. Google Driveにファイルが保存されているか確認
5. Google Sheetsの `LINE_Uploads` シートに記録されているか確認

### 7.5.3 トラブルシューティング

**Webhookが届かない:**
```bash
# ngrok URLが変わっていないか確認
# 無料版ngrokは再起動すると URLが変わる
# → LINE Developers ConsoleでWebhook URLを更新
```

**画像が保存されない:**
```bash
# GASログを確認
# Google Apps Script エディタ → 実行ログ
# エラーメッセージを確認
```

**認証エラー:**
```bash
# server/.env と GASの SHARED_SECRET が一致しているか確認
```

---

## 7.6 将来の拡張機能

### 7.6.1 テキストコマンド対応

**例: バトルコマンド**
```javascript
// server.js に追加

if (event.message.type === 'text') {
  const text = event.message.text;

  if (text === 'バトル') {
    // ランダムバトルを実行
    // 結果をLINEに返信
    return client.replyMessage(event.replyToken, {
      type: 'text',
      text: '勇者くん vs 魔王\n勝者: 勇者くん'
    });
  }

  if (text === 'ランキング') {
    // ランキングを取得
    // 結果をLINEに返信
    return client.replyMessage(event.replyToken, {
      type: 'text',
      text: '1位: 勇者くん (Rating: 45)\n2位: 魔王 (Rating: 30)'
    });
  }
}
```

### 7.6.2 リッチメニュー対応

**LINE Developers Consoleで設定:**
```
1. Messaging API設定 → リッチメニュー
2. メニュー項目:
   - キャラクター登録 (画像送信を促す)
   - バトル開始 (テキスト "バトル" 送信)
   - ランキング (テキスト "ランキング" 送信)
   - ストーリーモード (テキスト "ストーリー" 送信)
```

### 7.6.3 Flex Message によるリッチな結果表示

```javascript
// バトル結果をFlex Messageで送信
const flexMessage = {
  type: 'flex',
  altText: 'バトル結果',
  contents: {
    type: 'bubble',
    header: {
      type: 'box',
      layout: 'vertical',
      contents: [
        {
          type: 'text',
          text: 'バトル結果',
          weight: 'bold',
          size: 'xl'
        }
      ]
    },
    body: {
      type: 'box',
      layout: 'vertical',
      contents: [
        {
          type: 'text',
          text: '勝者: 勇者くん',
          size: 'lg',
          color: '#FFD700'
        },
        {
          type: 'text',
          text: 'ターン数: 25'
        },
        {
          type: 'text',
          text: '勇者くん HP: 50 → 15'
        },
        {
          type: 'text',
          text: '魔王 HP: 80 → 0'
        }
      ]
    }
  }
};

return client.replyMessage(event.replyToken, flexMessage);
```

---

## 7.7 セキュリティ考慮事項

### 7.7.1 Webhook検証

**LINE Signature検証 (LINE SDKが自動で実施):**
```javascript
// line.middleware(config) が署名検証を実施
// 不正なリクエストは自動的に拒否される
```

### 7.7.2 GAS認証

**共有シークレット方式:**
```javascript
// GAS側で認証チェック
if (data.secret !== SHARED_SECRET) {
  return ContentService.createTextOutput(JSON.stringify({
    error: 'Unauthorized'
  })).setMimeType(ContentService.MimeType.JSON);
}
```

### 7.7.3 環境変数管理

**⚠️ 絶対にGitにコミットしない:**
```bash
# .gitignore に追加
server/.env
```

**本番環境では環境変数を使用:**
```bash
# Heroku, Render等のPaaSでは環境変数で設定
heroku config:set LINE_CHANNEL_SECRET=xxxxx
```

---

## 7.8 本番デプロイ

### 7.8.1 Heroku デプロイ

**手順:**
```bash
# 1. Herokuアカウント作成・CLIインストール
heroku login

# 2. Herokuアプリ作成
heroku create oekaki-battler-linebot

# 3. 環境変数設定
heroku config:set LINE_CHANNEL_SECRET=xxxxx
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=xxxxx
heroku config:set GAS_WEBHOOK_URL=xxxxx
heroku config:set SHARED_SECRET=xxxxx

# 4. デプロイ
git subtree push --prefix server heroku main

# 5. Webhook URL更新
# LINE Developers Console:
# https://oekaki-battler-linebot.herokuapp.com/webhook
```

### 7.8.2 Render デプロイ

**手順:**
```
1. https://render.com/ にサインアップ
2. New → Web Service
3. リポジトリを接続
4. Root Directory: server
5. Build Command: npm install
6. Start Command: node server.js
7. 環境変数を設定
8. デプロイ
9. Webhook URLを更新
```

---

## 次のセクション

次は [08_TROUBLESHOOTING.md](08_TROUBLESHOOTING.md) でトラブルシューティングの詳細を確認してください。


================================================================================

# 08. トラブルシューティング

## 8.1 インストール関連の問題

### 8.1.1 Python パッケージインストールエラー

**エラー: `Microsoft Visual C++ 14.0 is required`**

**原因:** Windows環境でCコンパイラが必要なパッケージをインストールしようとしている

**解決方法:**
```powershell
# Visual Studio Build Tools をインストール
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
# "C++ build tools" をチェックしてインストール

# インストール後、再度試行
pip install -r requirements.txt
```

---

**エラー: `error: command 'gcc' failed`**

**原因:** Linux環境でビルドツールが不足

**解決方法:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential python3-dev

# Fedora/RHEL
sudo dnf install gcc python3-devel

# 再度インストール
pip install -r requirements.txt
```

---

**エラー: `ImportError: No module named 'tkinter'`**

**原因:** Tkinterがインストールされていない (Linux)

**解決方法:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter

# 確認
python3 -m tkinter
```

---

### 8.1.2 OpenCV 関連エラー

**エラー: `ImportError: libGL.so.1: cannot open shared object file`**

**原因:** OpenCVに必要なシステムライブラリが不足 (Linux)

**解決方法:**
```bash
sudo apt-get install libgl1-mesa-glx libglib2.0-0
```

---

**エラー: `cv2.error: (-215:Assertion failed)`**

**原因:** 画像ファイルが破損している、またはサポートされていない形式

**解決方法:**
```python
# 画像ファイルを確認
from PIL import Image
img = Image.open("your_image.png")
img.verify()  # 破損チェック

# 別の形式で保存してリトライ
img = Image.open("your_image.jpg")
img.save("your_image_converted.png", "PNG")
```

---

## 8.2 Google API 関連の問題

### 8.2.1 Google Sheets 接続エラー

**エラー: `gspread.exceptions.APIError: ... PERMISSION_DENIED`**

**原因:** スプレッドシートがサービスアカウントと共有されていない

**解決方法:**
```
1. credentials.json を開いて "client_email" の値をコピー
   例: oekaki-battler@project-id.iam.gserviceaccount.com

2. Google Sheetsで共有設定
   - スプレッドシートを開く
   - 右上の「共有」をクリック
   - コピーしたメールアドレスを追加
   - 権限: 編集者
   - 「送信」をクリック
```

---

**エラー: `FileNotFoundError: [Errno 2] No such file or directory: 'credentials.json'`**

**原因:** credentials.jsonがプロジェクトルートに存在しない

**解決方法:**
```bash
# ファイルの存在確認
ls credentials.json

# 存在しない場合
# 1. Google Cloud Console → サービスアカウント → キー作成
# 2. ダウンロードしたJSONファイルを credentials.json にリネーム
# 3. プロジェクトルートに配置
cp ~/Downloads/project-xxx-yyy.json ./credentials.json
```

---

**エラー: `gspread.exceptions.SpreadsheetNotFound`**

**原因:** SPREADSHEET_ID が間違っている

**解決方法:**
```bash
# スプレッドシートのURLから正しいIDを取得
# URL例: https://docs.google.com/spreadsheets/d/1AbC123XyZ.../edit
# SPREADSHEET_ID = 1AbC123XyZ...

# .env ファイルを確認・修正
nano .env

# 正しいIDを設定
SPREADSHEET_ID=1AbC123XyZ...
```

---

### 8.2.2 Google Drive エラー

**エラー: `HttpError 403: The user does not have sufficient permissions`**

**原因:** Drive APIが有効化されていない

**解決方法:**
```
1. Google Cloud Console にアクセス
   https://console.cloud.google.com/

2. プロジェクトを選択

3. APIとサービス → ライブラリ

4. "Google Drive API" を検索

5. 「有効にする」をクリック
```

---

**エラー: 画像アップロードが遅い**

**原因:** 大きな画像ファイルをアップロードしている

**解決方法:**
```python
# 画像を事前にリサイズ
from PIL import Image

img = Image.open("large_image.png")
img.thumbnail((1000, 1000))  # 最大1000x1000にリサイズ
img.save("resized_image.png", optimize=True)
```

---

### 8.2.3 Google Gemini AI エラー

**エラー: `google.api_core.exceptions.PermissionDenied: ... API_KEY_INVALID`**

**原因:** API キーが無効または設定されていない

**解決方法:**
```bash
# .env ファイルを確認
cat .env | grep GOOGLE_API_KEY

# API キーが正しいか確認
# Google AI Studio で新しいキーを生成
# https://makersuite.google.com/app/apikey

# .env を更新
nano .env
GOOGLE_API_KEY=AIzaSy...
```

---

**エラー: `google.api_core.exceptions.ResourceExhausted: ... QUOTA_EXCEEDED`**

**原因:** APIクォータ(使用量制限)を超過

**解決方法:**
```
1. Google Cloud Console → APIとサービス → ダッシュボード
2. "Generative Language API" の使用状況を確認
3. 翌日まで待つ、または有料プランにアップグレード
```

---

**エラー: AI解析が失敗してデフォルト値が使用される**

**原因:** 画像が小さすぎる、または不鮮明

**解決方法:**
```python
# より高解像度の画像を使用
# 最小推奨サイズ: 300x300px

# 手動でステータスを設定
# (将来実装予定のキャラクター編集機能)
```

---

## 8.3 バトル関連の問題

### 8.3.1 バトル画面が表示されない

**エラー: `pygame.error: No available video device`**

**原因:** ディスプレイが検出されない (リモートサーバー等)

**解決方法:**
```bash
# Linuxでヘッドレス環境の場合
export SDL_VIDEODRIVER=dummy

# または仮想ディスプレイを使用
sudo apt-get install xvfb
xvfb-run python main.py
```

---

**エラー: Pygameウィンドウが開かない (macOS)**

**原因:** Retina ディスプレイのスケーリング問題

**解決方法:**
```python
# main_menu.py の Pygame初期化部分を修正
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"

# または解像度を調整
screen = pygame.display.set_mode((1024, 768), pygame.SCALED)
```

---

### 8.3.2 バトルがフリーズする

**症状:** バトル中に画面が固まる

**原因:** 無限ループまたはイベント処理の問題

**解決方法:**
```python
# バトルエンジンのイベント処理を確認
def _execute_turn(self):
    # Pygameイベント処理を追加
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

    # ... (バトル処理)
```

---

**症状:** バトルログが表示されない

**原因:** フォントの読み込み失敗

**解決方法:**
```python
# 日本語フォントを明示的に指定
import pygame.font

# Windowsの場合
font_path = "C:/Windows/Fonts/msgothic.ttc"

# macOSの場合
font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc"

# Linuxの場合
font_path = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"

if os.path.exists(font_path):
    self.font_jp = pygame.font.Font(font_path, 28)
else:
    # フォールバック
    self.font_jp = pygame.font.SysFont('arial', 28)
```

---

## 8.4 データ関連の問題

### 8.4.1 オンラインモードで起動しない

**症状:** 常にオフラインモードになる

**診断:**
```python
# Pythonインタープリタで確認
from src.services.sheets_manager import SheetsManager

manager = SheetsManager()
print(f"Online Mode: {manager.online_mode}")

# エラーメッセージを確認
import logging
logging.basicConfig(level=logging.DEBUG)
manager = SheetsManager()
```

**解決方法:**
```
1. credentials.json の存在確認
2. .env の SPREADSHEET_ID 確認
3. スプレッドシート共有設定確認
4. Google Sheets API 有効化確認
5. インターネット接続確認
```

---

### 8.4.2 キャラクターが表示されない

**症状:** キャラクター一覧が空

**原因1:** データベースが空

**解決方法:**
```python
# データ確認
from src.services.sheets_manager import SheetsManager

manager = SheetsManager()
characters = manager.get_all_characters()
print(f"Characters: {len(characters)}")

# 空の場合、キャラクターを登録
```

---

**原因2:** 画像パスが不正

**解決方法:**
```python
# 画像パスを確認
for char in characters:
    print(f"{char.name}: {char.sprite_path}")
    if not os.path.exists(char.sprite_path):
        print(f"  → 存在しません！")

# パスを修正 (手動またはスクリプト)
```

---

### 8.4.3 バトル履歴が記録されない

**症状:** BattleHistoryシートにデータが追加されない

**原因:** オフラインモードで起動している

**解決方法:**
```python
# モード確認
print(f"Online Mode: {self.db_manager.online_mode}")

# オンラインモードに切り替え
# → 8.4.1 の手順でオンラインモード有効化
```

---

## 8.5 画像処理の問題

### 8.5.1 背景が除去されない

**症状:** 背景除去後も白背景が残る

**原因:** 背景が完全な白ではない

**解決方法:**
```python
# 閾値を調整
# src/services/image_processor.py

def remove_background(self, image_path: str, threshold: int = 230):
    # threshold を 240 → 230 に下げる
    # より広い範囲を背景として認識
```

---

**症状:** キャラクターの一部が透明になる

**原因:** 閾値が低すぎる

**解決方法:**
```python
# 閾値を上げる
def remove_background(self, image_path: str, threshold: int = 245):
    # threshold を上げて、より白い部分のみ除去
```

---

### 8.5.2 スプライト抽出がおかしい

**症状:** キャラクターが切れている

**原因:** バウンディングボックスの計算ミス

**解決方法:**
```python
# マージンを増やす
def extract_sprite(self, image: Image) -> Image:
    # ...
    margin = 20  # 10 → 20 に増やす
    # ...
```

---

**症状:** スプライトが小さすぎる/大きすぎる

**解決方法:**
```python
# リサイズサイズを調整
# src/services/image_processor.py

self.max_sprite_size = (400, 400)  # (300, 300) → (400, 400)
```

---

## 8.6 LINE Bot の問題

### 8.6.1 Webhook が届かない

**症状:** LINEで画像を送信しても反応がない

**診断:**
```bash
# Node.jsサーバーのログを確認
# "POST /webhook" というログが出ているか？

# 出ていない場合:
# → LINE Developers Console で Webhook URL を確認
# → ngrok URL が変わっていないか確認
```

**解決方法:**
```bash
# ngrok を再起動
pkill ngrok
ngrok http 3000

# 新しい URL を LINE Developers Console に設定
# Messaging API設定 → Webhook URL
# 例: https://xxxx-new-url.ngrok.io/webhook
```

---

### 8.6.2 画像が保存されない

**症状:** Botは反応するが、Driveに画像が保存されない

**原因:** GAS のエラー

**診断:**
```
1. Google Apps Script エディタを開く
2. 実行ログを確認 (画面下部)
3. エラーメッセージを確認
```

**よくあるエラー:**
- `PERMISSION_DENIED`: DriveフォルダIDが間違っている
- `Unauthorized`: SHARED_SECRET が一致していない
- `Invalid argument`: 画像データの形式が不正

**解決方法:**
```javascript
// GAS コードでログ追加
function doPost(e) {
  Logger.log('Received data: ' + e.postData.contents);
  try {
    // ...
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    Logger.log('Stack trace: ' + error.stack);
  }
}
```

---

### 8.6.3 ngrok が頻繁に切断される

**症状:** 無料版 ngrok のセッションが2時間で切れる

**解決方法:**
```bash
# ngrok を自動再起動するスクリプト
# watch_ngrok.sh

#!/bin/bash
while true; do
    ngrok http 3000
    echo "ngrok disconnected. Restarting in 5 seconds..."
    sleep 5
done
```

**本番環境の場合:**
```
# Heroku, Render等のPaaSにデプロイ
# → 永続的なHTTPS URLが提供される
```

---

## 8.7 パフォーマンスの問題

### 8.7.1 起動が遅い

**症状:** アプリケーション起動に30秒以上かかる

**原因:** Google Sheets から大量のデータを読み込んでいる

**解決方法:**
```python
# 起動時はデータを読み込まず、必要時に取得
# main_menu.py

def __init__(self):
    # 起動時は接続確認のみ
    self.db_manager = SheetsManager()
    # キャラクターリストは遅延ロード
    self.characters = None

def get_characters(self):
    if self.characters is None:
        self.characters = self.db_manager.get_all_characters()
    return self.characters
```

---

### 8.7.2 バトルが重い

**症状:** バトルアニメーションがカクつく

**解決方法:**
```python
# フレームレート制限
# battle_engine.py

clock = pygame.time.Clock()

while self._execute_turn():
    # ...
    pygame.display.flip()
    clock.tick(30)  # 30 FPSに制限
```

---

### 8.7.3 Google Sheets API制限

**症状:** `RATE_LIMIT_EXCEEDED` エラー

**原因:** 100 requests/100秒の制限を超過

**解決方法:**
```python
# バッチ更新を使用
# sheets_manager.py

def update_multiple_characters(self, characters):
    """複数キャラクターを一括更新"""
    worksheet = self.sheet.worksheet("Characters")

    # 全データを一度に取得
    all_data = worksheet.get_all_records()

    # 更新対象を特定
    updates = []
    for char in characters:
        for i, row in enumerate(all_data, start=2):  # ヘッダー除く
            if row['ID'] == char.id:
                updates.append({
                    'range': f'M{i}:O{i}',
                    'values': [[char.wins, char.losses, char.draws]]
                })

    # 一括更新 (1回のAPI呼び出し)
    worksheet.batch_update(updates)
```

---

## 8.8 デバッグ方法

### 8.8.1 ログ出力

**基本的なログ設定:**
```python
# main.py の冒頭に追加
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oekaki_battler.log'),
        logging.StreamHandler()
    ]
)
```

**各モジュールでログ使用:**
```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("デバッグ情報")
    logger.info("情報")
    logger.warning("警告")
    logger.error("エラー")
```

---

### 8.8.2 対話型デバッグ

```python
# エラー箇所で対話シェルを起動
import pdb

def buggy_function():
    # ...
    pdb.set_trace()  # ここでブレークポイント
    # ...

# 実行すると pdb プロンプトが表示される
# コマンド:
#   n: 次の行
#   s: ステップイン
#   c: 続行
#   p variable: 変数表示
#   q: 終了
```

---

### 8.8.3 例外トレースバック

```python
import traceback

try:
    risky_operation()
except Exception as e:
    logger.error("エラーが発生しました")
    logger.error(traceback.format_exc())
    # トレースバックをファイルに保存
    with open('error_trace.txt', 'w') as f:
        f.write(traceback.format_exc())
```

---

## 8.9 よくある質問 (FAQ)

### Q1: オフラインモードとオンラインモードを切り替えるには？

**A:** 自動判定されます。オンラインモードにするには:
```
1. credentials.json を配置
2. .env に SPREADSHEET_ID を設定
3. スプレッドシートを共有
4. アプリを再起動
```

---

### Q2: キャラクターを削除したい

**A:** 現在は手動削除のみサポート:
```python
# Pythonインタープリタで実行
from src.services.sheets_manager import SheetsManager

manager = SheetsManager()
manager.delete_character("character_id_here")
```

---

### Q3: バトルスピードを変更したい

**A:** メインメニューの設定から変更可能:
```
メインメニュー → 設定 → バトルスピード → スライダーで調整 (0.1-2.0秒)
```

---

### Q4: ストーリーモードの進行状況をリセットしたい

**A:** ストーリーモード画面から:
```
ストーリーモード → キャラクター選択 → 進行状況リセット
```

---

### Q5: エラーログはどこにある？

**A:**
```bash
# アプリケーションログ
cat oekaki_battler.log

# LINE Bot ログ
# サーバーコンソールに表示される

# GAS ログ
# Google Apps Script エディタ → 実行ログ
```

---

## 次のセクション

次は [09_API_REFERENCE.md](09_API_REFERENCE.md) でAPIリファレンスを確認してください。


================================================================================

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
