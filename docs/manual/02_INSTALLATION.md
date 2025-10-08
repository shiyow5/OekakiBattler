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
