# お絵描きバトラー マニュアル

このディレクトリには、お絵描きバトラーのマニュアルが含まれています。

---

## 📚 マニュアル一覧（役割別）

お絵描きバトラーには **4つの役割** があります。あなたの役割に合ったマニュアルをご覧ください。

### 🎨 参加者（絵を描いてバトルを見る人）

**[📖 PARTICIPANT_GUIDE.md](PARTICIPANT_GUIDE.md)** - **参加者向けガイド**

イベントで絵を描いて遊ぶ方向け。

- キャラクターの描き方
- ステータスの決まり方
- バトルの見方
- 楽しみ方のヒント

📄 **約150行** - 5分で読めます

---

### 👨‍💼 現場オペレーター（アプリを操作する人）

**[🎮 OPERATOR_MANUAL.md](OPERATOR_MANUAL.md)** - **運営マニュアル** ⭐重要

イベント会場でアプリを操作する担当者向け。

- アプリの起動と終了
- キャラクター登録作業の手順
- バトル実行とモード選択
- トラブル対応と緊急時対応
- 1日の運営フロー

📄 **約600行** - 運営前に必読

---

### 🔧 セットアップ担当（環境構築する人）

**[⚙️ 02_INSTALLATION.md](02_INSTALLATION.md)** - **インストールガイド**

現場でgit cloneして環境を構築する担当者向け。

- 必要な環境とツール
- 依存関係のインストール
- 環境変数の設定
- Google API設定
- プラットフォーム別手順（Windows/Mac/Linux）

📄 **約720行** - 初回セットアップ時に参照

---

### 💻 開発者（コードを書く人）

**技術マニュアル（10ファイル）**

システムの内部仕様やAPI、アーキテクチャを知りたい開発者向け。

| ファイル | 内容 | 対象 |
|---------|------|------|
| [00_INDEX.md](00_INDEX.md) | 技術マニュアル目次 | 全体構成の把握 |
| [01_SYSTEM_OVERVIEW.md](01_SYSTEM_OVERVIEW.md) | システム概要 | アーキテクチャ理解 |
| [02_INSTALLATION.md](02_INSTALLATION.md) | インストール | 環境構築 |
| [03_CHARACTER_MANAGEMENT.md](03_CHARACTER_MANAGEMENT.md) | キャラクター管理 | 実装詳細 |
| [04_BATTLE_SYSTEM.md](04_BATTLE_SYSTEM.md) | バトルシステム | ロジック仕様 |
| [05_STORY_MODE.md](05_STORY_MODE.md) | ストーリーモード | 機能仕様 |
| [06_DATA_MANAGEMENT.md](06_DATA_MANAGEMENT.md) | データ管理 | DB/API設計 |
| [07_LINE_BOT.md](07_LINE_BOT.md) | LINE Bot連携 | 統合仕様 |
| [08_TROUBLESHOOTING.md](08_TROUBLESHOOTING.md) | トラブルシューティング | 問題解決 |
| [09_API_REFERENCE.md](09_API_REFERENCE.md) | API リファレンス | コード仕様 |

**[📘 COMPLETE_MANUAL.md](COMPLETE_MANUAL.md)** - 全技術マニュアル統合版（約6,700行）

---

## 🚀 クイックスタート

### 参加者の方

1. **[PARTICIPANT_GUIDE.md](PARTICIPANT_GUIDE.md)** を読む
2. 紙にキャラクターを描く
3. スタッフに渡す
4. バトルを楽しむ

### 現場オペレーターの方

1. **[OPERATOR_MANUAL.md](OPERATOR_MANUAL.md)** を読む
2. 起動前の準備をする
3. アプリを起動: `python main.py`
4. キャラクター登録とバトルを実行

### セットアップ担当者の方

1. **[02_INSTALLATION.md](02_INSTALLATION.md)** を読む
2. 環境構築を実施
3. 動作確認
4. オペレーターに引き継ぎ

### 開発者の方

1. [00_INDEX.md](00_INDEX.md) で全体構成を確認
2. [01_SYSTEM_OVERVIEW.md](01_SYSTEM_OVERVIEW.md) でアーキテクチャ理解
3. [09_API_REFERENCE.md](09_API_REFERENCE.md) でAPI仕様確認
4. 必要に応じて各マニュアルを参照

---

## 📂 ファイル構成

```
docs/manual/
├── README.md                      # このファイル
│
├── PARTICIPANT_GUIDE.md           # 🎨 参加者向けガイド
├── OPERATOR_MANUAL.md             # 👨‍💼 現場オペレーター向けマニュアル
│
├── 00_INDEX.md                    # 技術マニュアル目次
├── 01_SYSTEM_OVERVIEW.md         # システム概要
├── 02_INSTALLATION.md            # 🔧 インストール（セットアップ担当向け）
├── 03_CHARACTER_MANAGEMENT.md    # キャラクター管理
├── 04_BATTLE_SYSTEM.md           # バトルシステム
├── 05_STORY_MODE.md              # ストーリーモード
├── 06_DATA_MANAGEMENT.md         # データ管理
├── 07_LINE_BOT.md                # LINE Bot
├── 08_TROUBLESHOOTING.md         # トラブルシューティング
├── 09_API_REFERENCE.md           # API リファレンス
├── COMPLETE_MANUAL.md            # 技術マニュアル統合版
│
├── combine_manuals.py            # 統合スクリプト
└── USER_GUIDE.md                 # (旧版・参考用)
```

---

## 🔄 マニュアルの更新（開発者向け）

技術マニュアルを更新した場合は、完全版を再生成してください:

```bash
cd docs/manual
python combine_manuals.py
```

---

## 📞 サポート情報

### 役割別の問い合わせ先

| 役割 | 困ったとき | 参照先 |
|------|----------|--------|
| 🎨 参加者 | 描き方がわからない | スタッフに聞いてください |
| 👨‍💼 オペレーター | 操作方法やエラー | [OPERATOR_MANUAL.md](OPERATOR_MANUAL.md) → [08_TROUBLESHOOTING.md](08_TROUBLESHOOTING.md) |
| 🔧 セットアップ担当 | 環境構築エラー | [02_INSTALLATION.md](02_INSTALLATION.md) → [08_TROUBLESHOOTING.md](08_TROUBLESHOOTING.md) |
| 💻 開発者 | バグや仕様確認 | [COMPLETE_MANUAL.md](COMPLETE_MANUAL.md) → GitHubイシュー |

---

**バージョン:** 1.0.0
**最終更新:** 2025-10-08
