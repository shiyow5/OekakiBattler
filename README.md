# 🎨 お絵描きバトラー (Oekaki Battler)

**Hand-drawn Character Battle System**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)

お絵描きバトラーは、手描きキャラクターをデジタル化し、AIが見た目を分析して自動生成したステータスで対戦させる革新的なゲームシステムです。

## ✨ 主な機能

- 🎨 **手描きキャラクター取り込み**: スキャンまたは写真撮影で簡単にデジタル化
- 🤖 **AI自動ステータス生成**: Google Gemini AIがキャラクターの見た目を分析
- ⚔️ **自動バトルシステム**: Pygameベースのリアルタイム戦闘表示
- ♾️ **エンドレスバトルモード**: トーナメント形式の勝ち抜き戦、新キャラ自動検出
- 📊 **詳細統計管理**: 戦績、勝率、キャラクター性能の追跡
- 🎲 **ランダムマッチ**: 自動でキャラクターをマッチング
- 💾 **データ永続化**: Google Spreadsheetsによるクラウドベースのデータ管理
- 📱 **LINE Bot連携**: LINEから画像を送信してキャラクター登録・Google Drive保存

## 🚀 クイックスタート

### 必要環境
- Python 3.11+
- Google AI API キー
- Node.js 14+ (LINE Bot機能を使用する場合)
- ngrok (ローカル開発用)

### インストール

1. **リポジトリをクローン**
```bash
git clone https://github.com/shiyow5/OekakiBattler.git
cd OekakiBattler
```

2. **仮想環境を作成・有効化**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate     # Windows
```

3. **依存関係をインストール**
```bash
pip install -r requirements.txt
```

4. **Google Sheets APIを設定**

Google Spreadsheetsを使用するため、Google Cloud Platformでの設定が必要です：

##### 4-1. Google Cloud Projectの作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（例：「OekakiBattler」）
3. プロジェクトを選択

##### 4-2. Google Sheets APIの有効化

1. 「APIとサービス」→「ライブラリ」に移動
2. 「Google Sheets API」を検索して有効化
3. 「Google Drive API」も同様に有効化

##### 4-3. サービスアカウントの作成

1. 「APIとサービス」→「認証情報」に移動
2. 「認証情報を作成」→「サービスアカウント」を選択
3. サービスアカウント名を入力（例：「oekaki-battler-sheets」）
4. 作成完了後、サービスアカウントをクリック
5. 「キー」タブ→「鍵を追加」→「新しい鍵を作成」
6. JSONキーをダウンロード
7. ダウンロードしたJSONファイルをプロジェクトルートに`credentials.json`として配置

##### 4-4. Google Driveフォルダの作成（オプション）

画像を整理するための専用フォルダを作成できます：

1. [Google Drive](https://drive.google.com/)で新しいフォルダを作成（例：「OekakiBattler Images」）
2. フォルダを開き、URLからフォルダIDをコピー
   - URL: `https://drive.google.com/drive/folders/【ここがフォルダID】`
3. フォルダを「共有」→サービスアカウントのメールアドレスを追加（編集者権限）

**注意**: フォルダIDを指定しない場合、画像はDriveのルートにアップロードされます。

##### 4-5. Google Spreadsheetの作成

1. [Google Sheets](https://sheets.google.com/)で新しいスプレッドシートを作成
2. スプレッドシート名を「OekakiBattler Characters」などに設定
3. URLから**スプレッドシートID**をコピー
   - URL: `https://docs.google.com/spreadsheets/d/【ここがスプレッドシートID】/edit`
4. スプレッドシートを開き、「共有」をクリック
5. 先ほど作成したサービスアカウントのメールアドレス（`xxxxx@xxxxxx.iam.gserviceaccount.com`）を追加
6. 権限を「編集者」に設定して共有

##### 4-6. 環境変数を設定

メインアプリケーション用の`.env`ファイルを作成：
```bash
# メインアプリケーション用の環境変数
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
echo "MODEL_NAME=gemini-2.5-flash-lite-preview-06-17" >> .env
echo "SPREADSHEET_ID=your_spreadsheet_id_here" >> .env
echo "WORKSHEET_NAME=Characters" >> .env
echo "GOOGLE_CREDENTIALS_PATH=credentials.json" >> .env
echo "DRIVE_FOLDER_ID=your_drive_folder_id_here" >> .env  # オプション
```

**重要**: 実際の値に置き換えてください：
- `your_google_api_key_here`: [Google AI Studio](https://aistudio.google.com/app/apikey)で取得したAPIキー
- `your_spreadsheet_id_here`: 上記で作成したスプレッドシートのID
- `your_drive_folder_id_here`: （オプション）Google Driveフォルダのid（指定すると画像が整理される）

LINE Bot機能を使用する場合は、`server/.env`ファイルも作成：
```bash
# server/.envファイルを作成
mkdir -p server
cat > server/.env << EOF
PORT=3000
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
GAS_WEBHOOK_URL=https://script.google.com/macros/s/XXXXX/exec
SHARED_SECRET=some_random_shared_secret_for_gas
EOF
```

**重要**: 実際の値に置き換えてください：
- `your_google_api_key_here`: Google AI APIキー
- `your_line_channel_secret`: LINE Developers Consoleで取得したChannel Secret
- `your_channel_access_token`: LINE Developers Consoleで取得したChannel Access Token
- `https://script.google.com/macros/s/XXXXX/exec`: Google Apps ScriptのWebアプリURL
- `some_random_shared_secret_for_gas`: GASとの認証用のランダムな文字列

5. **アプリケーションを起動**
```bash
python main.py
```

### オンライン/オフラインモードの自動切り替え

アプリケーションは起動時にGoogle Sheets/Driveへの接続を試みます：

**オンラインモード（Google Sheets利用可能）:**
- Google Spreadsheetsでキャラクターデータを管理
- Google Driveに画像を自動アップロード
- バトル履歴を記録
- ランキングを自動更新
- ステータスバーに「Online Mode - Google Sheets」と表示

**オフラインモード（接続失敗時の自動フォールバック）:**
- ローカルSQLiteデータベースを使用
- 画像はローカル保存のみ
- バトル履歴・ランキング機能は無効
- ステータスバーに「Offline Mode - Local Database」と表示

**接続失敗の理由:**
- インターネット接続がない
- credentials.jsonが設定されていない
- Google Sheets/Drive APIが有効化されていない
- スプレッドシートが共有されていない
- 環境変数（SPREADSHEET_ID）が未設定

**注意:** オフラインモードでもキャラクター登録・編集・バトルは正常に動作します。Google Sheets固有の機能（履歴記録・ランキング）のみが無効になります。

### Google Spreadsheet構造

アプリケーションが自動的に3つのワークシートを作成します：

#### 1. Characters（キャラクターデータ）

| 列 | 項目 | 説明 |
|---|---|---|
| A | ID | キャラクターの一意識別子（自動採番） |
| B | Name | キャラクター名 |
| C | Image URL | 元画像のURL（Google Driveなど） |
| D | Sprite URL | 処理済みスプライトのURL |
| E | HP | 体力値（50-150） |
| F | Attack | 攻撃力（30-120） |
| G | Defense | 防御力（20-100） |
| H | Speed | 素早さ（40-130） |
| I | Magic | 魔法力（10-100） |
| J | Description | キャラクター説明 |
| K | Created At | 作成日時（ISO形式） |
| L | Wins | 勝利数 |
| M | Losses | 敗北数 |
| N | Draws | 引き分け数 |

#### 2. BattleHistory（バトル履歴）

バトル終了後に自動的に記録されます：

| 列 | 項目 | 説明 |
|---|---|---|
| A | Battle ID | バトルの一意識別子 |
| B | Date | バトル実施日時 |
| C | Fighter 1 ID | ファイター1のID |
| D | Fighter 1 Name | ファイター1の名前 |
| E | Fighter 2 ID | ファイター2のID |
| F | Fighter 2 Name | ファイター2の名前 |
| G | Winner ID | 勝者のID |
| H | Winner Name | 勝者の名前 |
| I | Total Turns | 総ターン数 |
| J | Duration (s) | バトル時間（秒） |
| K | F1 Final HP | ファイター1の最終HP |
| L | F2 Final HP | ファイター2の最終HP |
| M | F1 Damage Dealt | ファイター1の与ダメージ |
| N | F2 Damage Dealt | ファイター2の与ダメージ |
| O | Result Type | 決着タイプ（KO/Time Limit/Draw） |

#### 3. Rankings（ランキング）

バトル終了後に自動更新されます：

| 列 | 項目 | 説明 |
|---|---|---|
| A | Rank | 順位 |
| B | Character ID | キャラクターID |
| C | Character Name | キャラクター名 |
| D | Total Battles | 総バトル数 |
| E | Wins | 勝利数 |
| F | Losses | 敗北数 |
| G | Draws | 引き分け数 |
| H | Win Rate (%) | 勝率（%） |
| I | Avg Damage Dealt | 平均与ダメージ |
| J | Rating | レーティング（勝利×3＋引き分け） |

**注意**:
- 初回起動時にヘッダーが自動生成されます
- Image URLとSprite URLは自動的にGoogle Drive URLとして保存されます
- キャラクター読み込み時にURLから画像を自動ダウンロード・キャッシュします
- 手動でスプレッドシートを編集する場合は、データ形式に注意してください

### Google Drive連携の動作

#### キャラクター登録時
1. ローカルの画像ファイル（元画像・スプライト）をGoogle Driveにアップロード
2. 公開URLを取得
3. URLをスプレッドシートのImage URL / Sprite URL列に記録
4. ローカルファイルは削除されずそのまま保持

#### キャラクター読み込み時
1. スプレッドシートからURLを取得
2. URLがhttp/httpsで始まる場合、自動的にダウンロード
3. `data/characters/char_{ID}_original.png`にキャッシュ
4. `data/sprites/char_{ID}_sprite.png`にキャッシュ
5. 以降はキャッシュから読み込み（再ダウンロード不要）

#### バトル終了後の自動処理
1. **バトル履歴の記録**: BattleHistoryシートにバトル結果を詳細記録
   - 対戦カード、勝者、ターン数、時間、最終HP、与ダメージなど
2. **ランキングの自動更新**: Rankingsシートを最新の戦績で更新
   - 勝率、平均与ダメージ、レーティングを自動計算
   - レーティング順にソート

#### 利点
- ✅ クラウドに画像を保存、どこからでもアクセス可能
- ✅ 複数デバイス間で画像を共有
- ✅ ローカルストレージの節約
- ✅ バックアップが自動的に保管される
- ✅ スプレッドシートから画像URLを直接確認可能
- ✅ バトル履歴を永続的に記録・分析可能
- ✅ リアルタイムのランキング自動更新
- ✅ スプレッドシートでデータの可視化・分析が容易

## 📱 LINE Bot機能

LINE Bot機能を使用すると、LINEから画像を送信してキャラクターを登録し、Google Driveに自動保存できます。手動でステータスを入力するか、AI自動生成から選択できます。

### LINE Bot設定手順

#### 1. LINE Developers Console設定

1. [LINE Developers](https://developers.line.biz/) にログイン
2. Providerを作成 → **Messaging APIチャンネル**を作成
3. **Channel Secret**と**Channel Access Token**を取得
4. Webhook URLを設定（後述のngrok URLを使用）

#### 2. Google Apps Script (GAS) 設定

Google Apps Scriptは、画像のアップロード・削除・キャラクター登録を処理するWebアプリとして機能します。

##### 2-1. スクリプト作成

1. [Google Apps Script](https://script.google.com/) にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを使用）
3. `server/googlesheet_apps_script_with_properties.js`の内容をコピー＆ペースト
4. **Deploy > New deployment** → **Web app**として公開
   - 「次のユーザーとして実行」→「自分」を選択
   - 「アクセスできるユーザー」→「全員」を選択
5. 発行されたWebアプリURLをメモ（例: `https://script.google.com/macros/s/XXXXX/exec`）

##### 2-2. スクリプトプロパティの設定（推奨）

スクリプトプロパティを使用すると、APIキーやIDをコード内に直接書かずに安全に管理できます。

**設定手順:**

1. Google Apps Scriptエディタで**「プロジェクトの設定」**（⚙️アイコン）をクリック
2. 「スクリプト プロパティ」タブを選択
3. 「プロパティを追加」をクリックして以下を設定:

| プロパティ名 | 説明 | 必須/オプション | 例 |
|---|---|---|---|
| `SHARED_SECRET` | GASとの認証用シークレット（ランダムな文字列） | **必須** | `oekaki_battler_secret_xyz123` |
| `SPREADSHEET_ID` | Google SpreadsheetsのスプレッドシートID | **必須** | `1asfRGrWkPRszQl4IUDO20o9Z7cgnV1bEVKVNt6cmKfM` |
| `DRIVE_FOLDER_ID` | Google DriveフォルダID（画像保存先） | オプション | `1JT7QnTcSrLo2AC4p580V7fa_MScuVd4G` |
| `GOOGLE_API_KEY` | Google Gemini APIキー（現在は未使用） | オプション | - |

4. 「プロパティを追加」を繰り返して、必要なプロパティをすべて追加

**プロパティ値の取得方法:**
- **SHARED_SECRET**: 任意のランダムな文字列を生成（例: `openssl rand -base64 32`）。`.env`ファイルと同じ値を使用
- **SPREADSHEET_ID**: Google SheetsのURLから取得
  - URL: `https://docs.google.com/spreadsheets/d/【ここがスプレッドシートID】/edit`
- **DRIVE_FOLDER_ID**: Google DriveフォルダのURLから取得
  - URL: `https://drive.google.com/drive/folders/【ここがフォルダID】`

**スクリプトプロパティのメリット:**
- ✅ **セキュリティ向上**: APIキーやIDをコード内に直接書かない
- ✅ **更新が簡単**: スクリプトを再デプロイせずに設定を変更可能
- ✅ **コード共有が安全**: スクリプトを共有しても秘密情報が漏れない
- ✅ **環境ごとの管理**: テスト環境と本番環境で異なる値を使用可能

**ハードコード版との比較:**

スクリプトプロパティを使用せず、コード内に直接値を書くこともできます（`server/googlesheet_apps_script_updated.js`）:

```javascript
// ハードコード版（非推奨）
var SHARED_SECRET = 'YOUR_SHARED_SECRET_HERE';
var SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID';
var DRIVE_FOLDER_ID = 'YOUR_DRIVE_FOLDER_ID';
```

しかし、**スクリプトプロパティの使用を強く推奨**します。ハードコード版は設定が簡単ですが、セキュリティリスクがあります。

#### 3. 環境変数設定

LINE Bot機能用の`server/.env`ファイルを作成：

```bash
# server/.envファイルを作成
mkdir -p server
cat > server/.env << EOF
PORT=3000
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
GAS_WEBHOOK_URL=https://script.google.com/macros/s/XXXXX/exec
SHARED_SECRET=some_random_shared_secret_for_gas
EOF
```

**設定値の取得方法**：
- `LINE_CHANNEL_SECRET`: LINE Developers Console > チャンネル > Basic settings
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Developers Console > チャンネル > Messaging API settings
- `GAS_WEBHOOK_URL`: Google Apps Script > Deploy > Web app で発行されたURL
- `SHARED_SECRET`: 任意のランダムな文字列（GAS側でも同じ値を使用）

#### 4. サーバー起動

`server_up.sh`スクリプトを使用してサーバーを起動：

```bash
# 実行権限を付与
chmod +x server_up.sh

# サーバー起動（ngrokも同時に起動）
./server_up.sh
```

このスクリプトは以下を実行します：
- Node.jsサーバーの起動
- ngrokによるHTTPSトンネルの作成
- プロセス終了時のクリーンアップ

#### 5. LINE Bot設定完了

1. ngrokが表示するHTTPS URLをコピー
2. LINE Developers ConsoleのWebhook URLに設定
3. Verify → 成功したら「Use webhook」を有効化
4. LINE Botを友だち追加して画像を送信してテスト

### 使用方法

#### 基本フロー

1. LINE Botを友だち追加
2. キャラクター画像を送信
3. 画像がGoogle Driveに自動アップロード
4. ボットが「ステータスを手動で入力しますか？」と質問
5. 2つの登録方法から選択：

#### 方法1: 手動入力

1. 「はい（手動入力）」を選択
2. 対話形式で以下を入力：
   - キャラクター名
   - HP（50-150）
   - 攻撃力（30-120）
   - 防御力（20-100）
   - 素早さ（40-130）
   - 魔力（10-100）
   - キャラクターの説明
3. 入力完了後、自動的にスプレッドシートに登録
4. メインアプリケーションで即座に使用可能

#### 方法2: AI自動生成（遅延生成方式）

1. 「いいえ（AI自動生成）」を選択
2. 画像が登録され、ステータスは空の状態でスプレッドシートに保存
3. ボットから「アプリを開いて確認してください」とメッセージ
4. **お絵描きバトラーアプリを起動**
5. アプリが空ステータスのキャラクターを自動検出
6. Google Gemini AIが画像を分析してステータス自動生成
7. 生成したステータスをスプレッドシートに反映
8. メインアプリケーションで使用可能

**メリット:**
- ✅ **手動入力**: 完全なカスタマイズ、意図通りのステータス設定
- ✅ **AI自動生成**: 既存のPython AIコードを活用、安定した処理
- ✅ **遅延生成**: GASのタイムアウトを気にせず、確実に生成

### セキュリティ注意事項

- **環境変数の管理**: `.env`ファイルは絶対にGitにコミットしない（`.gitignore`に追加済み）
- **APIキーの保護**: Channel Access Token / Channel Secretは絶対に公開しない
- **認証の実装**: GASのShared Secretで簡易認証を実装
- **HTTPSの使用**: 本番環境では適切なHTTPS証明書を使用
- **画像制限**: 画像サイズ制限と保存ポリシーを設計

### 環境変数ファイルの管理

プロジェクトには以下の環境変数ファイルがあります：

1. **`.env`** (ルートディレクトリ): メインアプリケーション用
   - `GOOGLE_API_KEY`: Google AI APIキー
   - `MODEL_NAME`: 使用するAIモデル名
   - `SPREADSHEET_ID`: Google SpreadsheetsのスプレッドシートID
   - `WORKSHEET_NAME`: ワークシート名（デフォルト: "Characters"）
   - `GOOGLE_CREDENTIALS_PATH`: サービスアカウントJSONファイルのパス
   - `DRIVE_FOLDER_ID`: Google Driveフォルダid（オプション）

2. **`server/.env`** (serverディレクトリ): LINE Bot機能用
   - `PORT`: サーバーポート番号
   - `LINE_CHANNEL_SECRET`: LINEチャンネルシークレット
   - `LINE_CHANNEL_ACCESS_TOKEN`: LINEチャンネルアクセストークン
   - `GAS_WEBHOOK_URL`: Google Apps ScriptのWebアプリURL
   - `SHARED_SECRET`: GAS認証用シークレット

**注意**: これらのファイルは機密情報を含むため、`.gitignore`に追加されており、Gitにコミットされません。`credentials.json`も同様にGitから除外されています。

## 📖 使い方

### 1. キャラクター登録

1. 紙にキャラクターを描く（白い紙に黒いペン推奨）
2. スキャナーまたはスマートフォンで撮影
3. アプリで「📷 Register Character」をクリック
4. 画像を選択し、「Analyze Image」でAI分析
5. キャラクター名を入力して登録完了

### 2. バトル開始

#### 通常バトル
1. Fighter 1とFighter 2を選択
2. Visual Modeを有効にしてリアルタイム表示
3. 「⚔️ START BATTLE!」をクリック
4. 自動戦闘を観戦

#### ランダムバトル
- 「🎲 Random Battle」をクリックでランダムにマッチング

#### エンドレスバトル
1. 「♾️ Endless Battle」をクリック
2. ランダムに選ばれたチャンピオンが挑戦者と自動対戦
3. チャンピオンが防衛を続ける勝ち抜き戦形式
4. 新しいキャラクターを登録すると自動的に検出され対戦再開
5. バトルログで戦況をリアルタイム確認
6. 一時停止/再開可能
7. 終了時に最終統計を表示

### 3. 統計確認

- キャラクター一覧で戦績を確認
- 「📊 View Statistics」で詳細統計
- 「🏟️ Battle History」で戦闘履歴

### 4. キャラクター削除

1. キャラクター一覧から削除したいキャラクターを選択
2. 「🗑️ Delete Character」をクリック
3. 確認ダイアログで「はい」を選択

**削除されるデータ:**
- ✅ キャラクター本体（Google Sheets / SQLite）
- ✅ バトル履歴レコード（該当キャラクターが参加した全バトル）
- ✅ ランキングレコード
- ✅ Google Drive画像（元画像とスプライト）※GAS設定時のみ
- ✅ ローカルキャッシュ画像（`data/characters/`と`data/sprites/`）

**注意:**
- バトル履歴があるキャラクターを削除する場合、確認ダイアログが表示されます
- 削除は取り消せません
- GAS経由で画像をアップロードした場合、Google Driveからも自動的に削除されます

## 🏗️ プロジェクト構成

```
OekakiBattler/
├── main.py                 # メインアプリケーション
├── config/                 # 設定ファイル
│   ├── settings.py         # 全体設定
│   └── database.py         # データベース設定
├── src/
│   ├── models/             # データモデル
│   │   ├── character.py    # キャラクターモデル
│   │   └── battle.py       # バトルモデル
│   ├── services/           # ビジネスロジック
│   │   ├── image_processor.py       # 画像処理
│   │   ├── ai_analyzer.py           # AI分析
│   │   ├── battle_engine.py         # バトルエンジン
│   │   ├── endless_battle_engine.py # エンドレスバトルエンジン
│   │   └── sheets_manager.py        # Google Sheets管理
│   ├── ui/                 # ユーザーインターフェース
│   │   └── main_menu.py    # メインGUI
│   └── utils/              # ユーティリティ
├── credentials.json        # Google サービスアカウント認証情報（要作成）
├── server/                 # LINE Botサーバー
│   ├── server.js           # Node.jsサーバー
│   └── .env                # 環境変数設定
├── server_up.sh            # サーバー起動スクリプト
├── assets/                 # アセットファイル
│   ├── images/            # 画像ファイル
│   │   ├── battle_arena.png    # バトル背景画像
│   │   └── vs.jpg              # バトル開始画面背景
│   └── sounds/            # サウンドファイル
├── data/                   # データファイル
│   ├── characters/         # 元画像
│   └── sprites/           # 処理済みスプライト
├── docs/                   # ドキュメント
│   ├── USER_MANUAL.md      # ユーザーマニュアル
│   └── API_REFERENCE.md    # API仕様書
└── requirements.txt        # 依存関係
```

## 🎨 カスタマイズ可能な要素

### バトル背景画像
バトル画面の外側背景を自由に変更できます：

- **画像パス**: `assets/images/battle_arena.png`
- **推奨サイズ**: 1024×768ピクセル（画面サイズに自動調整）
- **対応形式**: PNG（透過対応）、JPG
- **自動スケール**: 画面サイズに自動的に調整されます

画像を配置するだけで自動的に読み込まれます。ファイルがない場合は、デフォルトの水色背景が使用されます。アリーナ内部は常に白色で統一されます。

### サウンドファイル
カスタムサウンドを使用できます（詳細は`assets/sounds/README.md`参照）

## 🤖 AI分析システム

AIは以下の観点でキャラクターを分析します：

- **体力 (HP)**: 体格、頑丈さから判定 (50-150)
- **攻撃力**: 武器、筋肉質な描写から判定 (30-120)
- **防御力**: 鎧、盾などの防具から判定 (20-100)
- **素早さ**: 体型、手足の長さから判定 (40-130)
- **魔法力**: 杖、魔法的装飾から判定 (10-100)

## ⚔️ バトルシステム

### 通常バトル
- **ターン制**: 素早さ順で行動決定
- **ダメージ計算**: 攻撃力 - 防御力 + ランダム要素
- **特殊効果**: クリティカル（5%）、回避、魔法攻撃
- **勝利条件**: 相手のHP0または50ターン経過で判定

### エンドレスバトル（NEW!）
- **トーナメント形式**: ランダムに選ばれたチャンピオンが挑戦者と連戦
- **勝ち抜き戦**: チャンピオンが勝利し続ける限り防衛継続
- **チャンピオン交代**: 挑戦者が勝利すると新チャンピオン誕生
- **新キャラ自動検出**: 3秒ごとに新規登録キャラを自動検出
- **自動再開**: 新キャラクター検出時に自動でバトル再開
- **連勝記録**: チャンピオンの防衛記録を追跡
- **一時停止機能**: いつでもバトルを停止・再開可能
- **最終統計**: 終了時に総バトル数、最終チャンピオン、連勝数を表示

## 📊 技術仕様

- **言語**: Python 3.11+ / Node.js 14+
- **AI**: Google Gemini AI
- **GUI**: Tkinter + Pygame
- **画像処理**: OpenCV + PIL
- **データ管理**: Google Spreadsheets (gspread)
- **LINE Bot**: Express + @line/bot-sdk
- **クラウド連携**: Google Apps Script + Google Drive
- **アーキテクチャ**: レイヤード・アーキテクチャ

## 🔧 開発者向け

### アーキテクチャ

- **Models**: Pydanticベースのデータ検証
- **Services**: ビジネスロジックの分離
- **UI**: Tkinter/Pygameによるデスクトップアプリ
- **Config**: 設定の一元管理

### Drive操作の実装について

**画像アップロード・削除の仕組み:**
- Google Apps Script (GAS)経由でのみ実行
- サービスアカウントの直接操作は廃止
- GASがユーザー権限で実行されるため、アップロード・削除の両方が可能

**理由:**
- サービスアカウントはストレージクォータがない（アップロード不可）
- サービスアカウントはユーザー所有ファイルを削除できない（権限不足）
- GAS経由の統一で実装がシンプルに

**実装箇所:**
- `src/services/sheets_manager.py`: `upload_to_drive()`, `delete_from_drive()`
- `server/googlesheet_apps_script_updated.js`: `doPost()`, `handleDelete()`

### 拡張可能性

- 新しいステータス項目の追加
- カスタムバトル演出
- 追加AI分析モデル
- ネットワーク対戦機能

詳細は [API_REFERENCE.md](docs/API_REFERENCE.md) をご覧ください。

## 📚 ドキュメント

- [ユーザーマニュアル](docs/USER_MANUAL.md) - 使用方法とトラブルシューティング
- [API仕様書](docs/API_REFERENCE.md) - 開発者向け技術資料
- [プロジェクト仕様書](SPECIFICATION.md) - 詳細な要件定義

## 🐛 トラブルシューティング

### Google Sheets関連

**問題**: `FileNotFoundError: Please place your Google credentials JSON file`
- **原因**: サービスアカウントのJSONファイルが見つからない
- **解決**: `credentials.json`をプロジェクトルートに配置し、`.env`の`GOOGLE_CREDENTIALS_PATH`が正しいか確認

**問題**: `gspread.exceptions.APIError: PERMISSION_DENIED`
- **原因**: スプレッドシートがサービスアカウントと共有されていない
- **解決**: スプレッドシートの「共有」からサービスアカウントのメールアドレスを追加（編集者権限）

**問題**: `gspread.exceptions.SpreadsheetNotFound`
- **原因**: スプレッドシートIDが間違っているか、アクセス権限がない
- **解決**: `.env`の`SPREADSHEET_ID`を確認し、スプレッドシートのURLからIDをコピー

**問題**: APIクォータ超過エラー
- **原因**: Google Sheets APIの利用制限に達した
- **解決**: リクエスト頻度を減らす、またはGoogle Cloud Consoleでクォータ増加をリクエスト

**問題**: 画像アップロードが失敗する
- **原因**: Google Drive APIが有効化されていない、またはサービスアカウントの権限不足
- **解決**: Google Drive APIを有効化し、Driveフォルダをサービスアカウントと共有（編集者権限）

**問題**: `storageQuotaExceeded` エラーが発生する
- **エラー内容**: `Service Accounts do not have storage quota`
- **原因**: サービスアカウントがファイルを作成すると、サービスアカウント自身が所有者になりますが、サービスアカウントには独自のストレージ容量が割り当てられていません
- **解決方法（3つの選択肢）**:

  **方法1: 共有ドライブを使用【推奨・Google Workspaceユーザー向け】**
  1. Google Workspace管理者として[Google Drive](https://drive.google.com/)にアクセス
  2. 左メニューの「共有ドライブ」→「新規」をクリック
  3. 名前を入力（例: "OekakiBattler"）して作成
  4. 共有ドライブを開き、新しいフォルダを作成（例: "Images"）
  5. フォルダを右クリック→「共有」→サービスアカウントのメールアドレスを追加（コンテンツ管理者権限）
  6. フォルダのURLから共有ドライブのフォルダIDをコピー
  7. `.env`ファイルの`DRIVE_FOLDER_ID`を共有ドライブのフォルダIDに更新

  **方法2: Google Apps Scriptを使用【個人アカウント向け・推奨】**

  既存のLINE Bot用Google Apps Scriptを利用して、あなたのアカウントのストレージに画像を保存・削除できます。

  1. **Google Apps Scriptのデプロイ**
     - [Google Apps Script](https://script.google.com/)にアクセス
     - 新しいプロジェクトを作成（または既存のLINE Bot用プロジェクトを使用）
     - `server/googlesheet_apps_script_updated.js`の内容をコピー＆ペースト
     - スクリプト内の以下を設定:
       ```javascript
       var SHARED_SECRET = 'oekaki_battler_line_to_gas_secret_shiyow5'; // シークレット
       var folderId = '1JT7QnTcSrLo2AC4p580V7fa_MScuVd4G'; // あなたのDriveフォルダID
       ```
     - 「デプロイ」→「新しいデプロイ」→「ウェブアプリ」を選択
     - 「次のユーザーとして実行」→「自分」を選択
     - 「アクセスできるユーザー」→「全員」を選択
     - デプロイ後、ウェブアプリのURLをコピー

  2. **環境変数を設定**
     `.env`ファイルに以下を追加:
     ```bash
     GAS_WEBHOOK_URL="https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec"
     SHARED_SECRET="oekaki_battler_line_to_gas_secret_shiyow5"
     ```

  3. アプリケーションを再起動

  **メリット**:
  - あなたのアカウントのストレージを使用（容量エラーなし）
  - 画像のアップロードと削除の両方に対応
  - 設定が簡単
  - LINE BotとPythonアプリの両方で使用可能
  - サービスアカウントの権限問題を回避（GASがユーザー権限で実行）

  **デメリット**:
  - GASのリクエスト制限あり（1日20,000回）

  **注意**:
  - この方法では、キャラクター削除時にGoogle Driveからも画像が自動削除されます
  - GASの`handleDelete()`関数が削除リクエストを処理します

  **方法3: ローカルストレージのみ使用**
  1. `.env`ファイルから`DRIVE_FOLDER_ID`と`GAS_WEBHOOK_URL`の行を削除:
     ```bash
     # DRIVE_FOLDER_ID="..."  # コメントアウト
     # GAS_WEBHOOK_URL="..."  # コメントアウト
     ```
  2. アプリケーションを再起動
  3. 画像はローカル（`data/characters/`と`data/sprites/`）にのみ保存されます

  **方法4: OAuth 2.0認証を使用【上級者向け】**
  - サービスアカウントの代わりにOAuth 2.0ユーザー認証を使用
  - 実装には`google-auth-oauthlib`と認証フローの変更が必要
  - 詳細は[Google Drive API OAuth 2.0ドキュメント](https://developers.google.com/drive/api/guides/about-auth)を参照

- **現在の動作**: 画像アップロードが失敗しても、ローカルパスでスプレッドシートに保存され、機能は継続します

**問題**: 画像ダウンロードが失敗する
- **原因**: Google DriveのURLがprivateになっている、またはネットワーク接続の問題
- **解決**: ファイルの共有設定を確認（リンクを知っている全員が閲覧可）、インターネット接続を確認

その他の問題と解決法は [USER_MANUAL.md](docs/USER_MANUAL.md#トラブルシューティング) をご確認ください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルをご覧ください。

## 🙋‍♀️ コントリビューション

プロジェクトへの貢献を歓迎します！

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ✨ 今後の予定

- [x] LINE Bot連携機能
- [ ] Web版の開発
- [ ] モバイルアプリ対応
- [ ] オンライン対戦機能
- [ ] 追加のAI分析モデル
- [ ] キャラクター編集機能
- [ ] LINE Botからの直接バトル機能

## 📞 サポート

質問やサポートが必要な場合は、[Issues](https://github.com/shiyow5/OekakiBattler/issues) にてお気軽にお問い合わせください。

---

**お絵描きバトラーで、あなたの想像力を戦わせよう！** 🎨⚔️