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
