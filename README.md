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

## 🚀 クイックスタート

### 必要環境
- Python 3.11+
- Google AI API キー

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
```bash
# .envファイルを作成
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
echo "MODEL_NAME=gemini-2.5-flash-lite-preview-06-17" >> .env
```

5. **アプリケーションを起動**
```bash
python main.py
```

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
├── data/                   # データファイル
│   ├── characters/         # 元画像
│   ├── sprites/           # 処理済みスプライト
│   └── database.db        # SQLiteデータベース
├── docs/                   # ドキュメント
│   ├── USER_MANUAL.md      # ユーザーマニュアル
│   └── API_REFERENCE.md    # API仕様書
└── requirements.txt        # 依存関係
```

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

- **言語**: Python 3.11+
- **AI**: Google Gemini AI
- **GUI**: Tkinter + Pygame
- **画像処理**: OpenCV + PIL
- **データベース**: SQLite
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

- [ ] Web版の開発
- [ ] モバイルアプリ対応
- [ ] オンライン対戦機能
- [ ] 追加のAI分析モデル
- [ ] キャラクター編集機能

## 📞 サポート

質問やサポートが必要な場合は、[Issues](https://github.com/shiyow5/OekakiBattler/issues) にてお気軽にお問い合わせください。

---

**お絵描きバトラーで、あなたの想像力を戦わせよう！** 🎨⚔️