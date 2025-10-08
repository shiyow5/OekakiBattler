#!/usr/bin/env python3
"""
マニュアル統合スクリプト

全てのマニュアルファイル (00_INDEX.md ~ 09_API_REFERENCE.md) を
1つのMarkdownファイルに統合します。

使用方法:
    python combine_manuals.py

出力:
    COMPLETE_MANUAL.md
"""

import os
from pathlib import Path
from datetime import datetime


def combine_manuals():
    """全マニュアルを統合"""

    # マニュアルディレクトリ
    manual_dir = Path(__file__).parent

    # 統合するファイルのリスト (順番が重要)
    manual_files = [
        "00_INDEX.md",
        "01_SYSTEM_OVERVIEW.md",
        "02_INSTALLATION.md",
        "03_CHARACTER_MANAGEMENT.md",
        "04_BATTLE_SYSTEM.md",
        "05_STORY_MODE.md",
        "06_DATA_MANAGEMENT.md",
        "07_LINE_BOT.md",
        "08_TROUBLESHOOTING.md",
        "09_API_REFERENCE.md"
    ]

    # 出力ファイル
    output_file = manual_dir / "COMPLETE_MANUAL.md"

    print("=" * 60)
    print("お絵描きバトラー システムマニュアル統合")
    print("=" * 60)
    print()

    # ヘッダー作成
    header = f"""# お絵描きバトラー システム詳細マニュアル (完全版)

**生成日時:** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

**バージョン:** 1.0.0

---

このドキュメントは、お絵描きバトラーシステムの全マニュアルを統合したものです。

---

"""

    # 統合処理
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # ヘッダー書き込み
        outfile.write(header)

        # 各マニュアルファイルを結合
        for i, filename in enumerate(manual_files, 1):
            filepath = manual_dir / filename

            if not filepath.exists():
                print(f"⚠️  警告: {filename} が見つかりません。スキップします。")
                continue

            print(f"[{i}/{len(manual_files)}] {filename} を統合中...")

            # ファイル読み込み
            with open(filepath, 'r', encoding='utf-8') as infile:
                content = infile.read()

            # セクション区切りを追加
            outfile.write(f"\n\n{'=' * 80}\n\n")

            # コンテンツ書き込み
            outfile.write(content)

            print(f"    ✓ 完了 ({len(content)} 文字)")

    # 完了メッセージ
    print()
    print("=" * 60)
    print(f"✅ 統合完了！")
    print(f"📄 出力ファイル: {output_file}")
    print(f"📊 ファイルサイズ: {output_file.stat().st_size:,} バイト")
    print("=" * 60)
    print()
    print("統合マニュアルの確認:")
    print(f"    cat {output_file}")
    print(f"    less {output_file}")
    print(f"    code {output_file}  # VS Code")
    print()


def main():
    try:
        combine_manuals()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
