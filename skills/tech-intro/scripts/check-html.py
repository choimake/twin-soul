#!/usr/bin/env python3
"""tech-intro の単一 HTML を、機械的に判定できる項目だけ検査する。

Python 3 の標準ライブラリだけで動く。終了コード 0 は指摘なし。
指摘があるときは 1 で、id と理由を 1 行ずつ出す。
出典（data-scope 以外の details）にある強さの語（normally、may、should など）を含む文も一覧に出す。
これは本文と照らす材料で、終了コードには影響しない。

見ないもの: 公式と本文の一致、読み手が説明できるか、用語の訳、章の理解順、
図のラベルが本文の語か。

ルールを足す手順は checks.py の冒頭に書いた。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# python3 -I はスクリプトのディレクトリを sys.path に入れないので、同じディレクトリのモジュールを読めるように足す
sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import check_html  # noqa: E402
from hedges import hedged_quotes  # noqa: E402
from selftest import run_self_test  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="tech-intro の HTML を機械的に検査する")
    parser.add_argument("html", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    if not args.html:
        parser.error("HTML ファイルか --self-test を指定する")
    failed = False
    for path in args.html:
        html = path.read_text(encoding="utf-8")
        findings = check_html(html)
        quotes = hedged_quotes(html)
        if findings:
            failed = True
            print(f"{path}:")
            for item in findings:
                print(f"  {item}")
        if quotes:
            print(f"{path}: 強さの語を含む引用（合否に数えない）")
            for heading, sentence in quotes:
                print(f"  {heading}: {sentence}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
