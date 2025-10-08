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
