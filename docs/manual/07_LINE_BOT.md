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
