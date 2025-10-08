# お絵描きバトラー システムマニュアル

このディレクトリには、お絵描きバトラーシステムの詳細なマニュアルが含まれています。

## マニュアル構成

マニュアルは10個のファイルに分割されており、それぞれ独立して参照できます:

| ファイル | 内容 | 用途 |
|---------|------|------|
| [00_INDEX.md](00_INDEX.md) | 目次・概要 | マニュアル全体の構成を把握 |
| [01_SYSTEM_OVERVIEW.md](01_SYSTEM_OVERVIEW.md) | システム概要 | アーキテクチャ、技術スタック、データフローの理解 |
| [02_INSTALLATION.md](02_INSTALLATION.md) | インストール・セットアップ | 環境構築、依存関係のインストール |
| [03_CHARACTER_MANAGEMENT.md](03_CHARACTER_MANAGEMENT.md) | キャラクター管理 | キャラクター登録、画像処理、AI解析 |
| [04_BATTLE_SYSTEM.md](04_BATTLE_SYSTEM.md) | バトルシステム | バトルロジック、ダメージ計算、特殊効果 |
| [05_STORY_MODE.md](05_STORY_MODE.md) | ストーリーモード | ボス管理、進行状況、プレイ方法 |
| [06_DATA_MANAGEMENT.md](06_DATA_MANAGEMENT.md) | データ管理 | オンライン/オフラインモード、Google Sheets/SQLite |
| [07_LINE_BOT.md](07_LINE_BOT.md) | LINE Bot連携 | LINE Bot設定、Webhook、GAS統合 |
| [08_TROUBLESHOOTING.md](08_TROUBLESHOOTING.md) | トラブルシューティング | よくある問題と解決方法 |
| [09_API_REFERENCE.md](09_API_REFERENCE.md) | API リファレンス | クラス・メソッド仕様、使用例 |

## 完全版マニュアル

全マニュアルを統合した1ファイルも提供しています:

- **[COMPLETE_MANUAL.md](COMPLETE_MANUAL.md)** - 全マニュアル統合版 (約190KB)

### 完全版マニュアルの生成方法

```bash
# マニュアルディレクトリに移動
cd docs/manual

# 統合スクリプト実行
python combine_manuals.py

# COMPLETE_MANUAL.md が生成されます
```

## 使い方

### 初めての方

1. [00_INDEX.md](00_INDEX.md) で全体像を把握
2. [02_INSTALLATION.md](02_INSTALLATION.md) で環境構築
3. [03_CHARACTER_MANAGEMENT.md](03_CHARACTER_MANAGEMENT.md) でキャラクター作成方法を学習

### 開発者向け

- [01_SYSTEM_OVERVIEW.md](01_SYSTEM_OVERVIEW.md) - アーキテクチャ理解
- [09_API_REFERENCE.md](09_API_REFERENCE.md) - API仕様確認
- [08_TROUBLESHOOTING.md](08_TROUBLESHOOTING.md) - デバッグ方法

### 機能別リファレンス

- **バトルシステム** → [04_BATTLE_SYSTEM.md](04_BATTLE_SYSTEM.md)
- **ストーリーモード** → [05_STORY_MODE.md](05_STORY_MODE.md)
- **データ管理** → [06_DATA_MANAGEMENT.md](06_DATA_MANAGEMENT.md)
- **LINE Bot** → [07_LINE_BOT.md](07_LINE_BOT.md)

## マニュアルの更新

マニュアルを更新した場合は、完全版を再生成してください:

```bash
python combine_manuals.py
```

## ファイル一覧

```
docs/manual/
├── README.md                      # このファイル
├── 00_INDEX.md                    # 目次
├── 01_SYSTEM_OVERVIEW.md         # システム概要
├── 02_INSTALLATION.md            # インストール
├── 03_CHARACTER_MANAGEMENT.md    # キャラクター管理
├── 04_BATTLE_SYSTEM.md           # バトルシステム
├── 05_STORY_MODE.md              # ストーリーモード
├── 06_DATA_MANAGEMENT.md         # データ管理
├── 07_LINE_BOT.md                # LINE Bot
├── 08_TROUBLESHOOTING.md         # トラブルシューティング
├── 09_API_REFERENCE.md           # API リファレンス
├── combine_manuals.py            # 統合スクリプト
└── COMPLETE_MANUAL.md            # 完全版マニュアル (生成物)
```

## ライセンス

このマニュアルは、お絵描きバトラーシステムの一部として提供されます。

---

**バージョン:** 1.0.0
**最終更新:** 2025-10-08
