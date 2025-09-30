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
- 📊 **詳細統計管理**: 戦績、勝率、キャラクター性能の追跡
- 🎲 **ランダムマッチ**: 自動でキャラクターをマッチング
- 💾 **データ永続化**: SQLiteによる確実なデータ保存
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

4. **環境変数を設定**

メインアプリケーション用の`.env`ファイルを作成：
```bash
# メインアプリケーション用の環境変数
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
echo "MODEL_NAME=gemini-2.5-flash-lite-preview-06-17" >> .env
```

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

## 📱 LINE Bot機能

LINE Bot機能を使用すると、LINEから画像を送信してキャラクターを登録し、Google Driveに自動保存できます。

### LINE Bot設定手順

#### 1. LINE Developers Console設定

1. [LINE Developers](https://developers.line.biz/) にログイン
2. Providerを作成 → **Messaging APIチャンネル**を作成
3. **Channel Secret**と**Channel Access Token**を取得
4. Webhook URLを設定（後述のngrok URLを使用）

#### 2. Google Apps Script (GAS) 設定

1. Googleスプレッドシートを作成
2. 拡張機能 > Apps Script を開く
3. 以下のコードを貼り付け：

```javascript
function doPost(e) {
  try {
    if (!e.postData || !e.postData.contents) return ContentService.createTextOutput('no data');

    var payload = JSON.parse(e.postData.contents);
    
    // シークレット確認
    var SHARED_SECRET = 'YOUR_SHARED_SECRET_HERE';
    if (!payload.secret || payload.secret !== SHARED_SECRET) {
      return ContentService.createTextOutput(JSON.stringify({ok:false, error:'forbidden'}))
             .setMimeType(ContentService.MimeType.JSON);
    }

    var b64 = payload.image;
    var mime = payload.mimeType || 'image/jpeg';
    var filename = payload.filename || ('line_' + new Date().getTime() + '.jpg');

    // Base64をデコードしてblobを作成
    var blob = Utilities.newBlob(Utilities.base64Decode(b64), mime, filename);

    // Driveに保存
    var file = DriveApp.createFile(blob);
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    var url = file.getUrl();

    // スプレッドシートに追記
    var ssId = 'YOUR_SPREADSHEET_ID';
    var ss = SpreadsheetApp.openById(ssId);
    var sheet = ss.getSheetByName('Sheet1') || ss.getSheets()[0];
    var now = new Date();
    sheet.appendRow([now, filename, url]);

    return ContentService.createTextOutput(JSON.stringify({ok:true, url:url}))
           .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ok:false, error:err.toString()}))
           .setMimeType(ContentService.MimeType.JSON);
  }
}
```

4. **Deploy > New deployment** → **Web app**として公開
5. 発行されたURLをメモ

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

1. LINE Botを友だち追加
2. キャラクター画像を送信
3. 自動でGoogle Driveに保存され、スプレッドシートに記録
4. メインアプリケーションでキャラクターとして登録可能

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

2. **`server/.env`** (serverディレクトリ): LINE Bot機能用
   - `PORT`: サーバーポート番号
   - `LINE_CHANNEL_SECRET`: LINEチャンネルシークレット
   - `LINE_CHANNEL_ACCESS_TOKEN`: LINEチャンネルアクセストークン
   - `GAS_WEBHOOK_URL`: Google Apps ScriptのWebアプリURL
   - `SHARED_SECRET`: GAS認証用シークレット

**注意**: これらのファイルは機密情報を含むため、`.gitignore`に追加されており、Gitにコミットされません。

## 📖 使い方

### 1. キャラクター登録

1. 紙にキャラクターを描く（白い紙に黒いペン推奨）
2. スキャナーまたはスマートフォンで撮影
3. アプリで「📷 Register Character」をクリック
4. 画像を選択し、「Analyze Image」でAI分析
5. キャラクター名を入力して登録完了

### 2. バトル開始

1. Fighter 1とFighter 2を選択
2. Visual Modeを有効にしてリアルタイム表示
3. 「⚔️ START BATTLE!」をクリック
4. 自動戦闘を観戦

### 3. 統計確認

- キャラクター一覧で戦績を確認
- 「📊 View Statistics」で詳細統計
- 「🏟️ Battle History」で戦闘履歴

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
│   │   ├── image_processor.py    # 画像処理
│   │   ├── ai_analyzer.py        # AI分析
│   │   ├── battle_engine.py      # バトルエンジン
│   │   └── database_manager.py   # データベース管理
│   ├── ui/                 # ユーザーインターフェース
│   │   └── main_menu.py    # メインGUI
│   └── utils/              # ユーティリティ
├── server/                 # LINE Botサーバー
│   ├── server.js           # Node.jsサーバー
│   └── .env                # 環境変数設定
├── server_up.sh            # サーバー起動スクリプト
├── assets/                 # アセットファイル
│   ├── images/            # 画像ファイル
│   │   └── battle_arena.png    # バトル背景画像
│   └── sounds/            # サウンドファイル
├── data/                   # データファイル
│   ├── characters/         # 元画像
│   ├── sprites/           # 処理済みスプライト
│   └── database.db        # SQLiteデータベース
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

- **ターン制**: 素早さ順で行動決定
- **ダメージ計算**: 攻撃力 - 防御力 + ランダム要素
- **特殊効果**: クリティカル（5%）、回避、魔法攻撃
- **勝利条件**: 相手のHP0または50ターン経過で判定

## 📊 技術仕様

- **言語**: Python 3.11+ / Node.js 14+
- **AI**: Google Gemini AI
- **GUI**: Tkinter + Pygame
- **画像処理**: OpenCV + PIL
- **データベース**: SQLite
- **LINE Bot**: Express + @line/bot-sdk
- **クラウド連携**: Google Apps Script + Google Drive
- **アーキテクチャ**: レイヤード・アーキテクチャ

## 🔧 開発者向け

### アーキテクチャ

- **Models**: Pydanticベースのデータ検証
- **Services**: ビジネスロジックの分離
- **UI**: Tkinter/Pygameによるデスクトップアプリ
- **Config**: 設定の一元管理

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

よくある問題と解決法は [USER_MANUAL.md](docs/USER_MANUAL.md#トラブルシューティング) をご確認ください。

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