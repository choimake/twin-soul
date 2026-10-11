"""test_*.py が共通で使う補助。名前を test で始めないので、unittest discover はテストとして読まない。

1 本だけ動かすときは -p でファイルを絞る:
    python3 -I -m unittest discover -s skills/tech-intro/scripts -p test_css.py
"""

from __future__ import annotations

from css import Sheet, parse_sheet, style_text
from htmldoc import DocParser, Node, walk


def parse(html: str) -> Node:
    parser = DocParser()
    parser.feed(html)
    return parser.root


def parse_page(html: str) -> tuple[Node, Sheet, str]:
    """木、style 要素から読んだ規則、style 要素の中身をまとめて返す。"""
    root = parse(html)
    css = style_text(root)
    return root, parse_sheet(css), css


def find(root: Node, key: str) -> Node:
    """タグ名か class 名が key に一致する最初の要素を返す。"""
    return next(node for node in walk(root) if node.tag == key or key in node.classes)
