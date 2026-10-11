"""出典にある強さの語（normally、may、should など）を含む文を一覧にする。合否には使わない。"""

from __future__ import annotations

import re

from htmldoc import DocParser, Node, Text, ancestors, norm_heading, visible_text, walk


QUOTE_TAGS = {"li", "p", "blockquote", "dd"}
HEDGE_RE = re.compile(r"\b(?:normally|typically|usually|may|might|could|can(?!\s+only\b)|in many cases|should|must)\b", re.I)
# e.g.、i.e.、... の後ろでは切らない。… は区切りに入れない
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\.\.\.)\s+|[「」。\n]", re.I)
# 引用の頭に付く省略記号（[...]、[…]、...、…）
LEADING_ELLIPSIS_RE = re.compile(r"^(?:\[(?:\.\.\.|…)\]|\.\.\.|…)\s*")


def is_quote_leaf(node: Node) -> bool:
    """引用を入れる要素で、中に同じ種類の要素を持たないもの。"""
    if node.tag not in QUOTE_TAGS:
        return False
    return not any(sub is not node and sub.tag in QUOTE_TAGS for sub in walk(node))


def source_text(node: Node) -> str:
    """出典の文字。リンク（ページ名）は除き、<q> は「」と同じく前後で区切る。"""
    parts: list[str] = []

    def visit(current: Node | Text) -> None:
        if isinstance(current, Text):
            parts.append(current.data)
            return
        if current.tag in {"style", "script", "a"}:
            return
        if current.tag == "q":
            parts.append("\n")
        for child in current.children:
            visit(child)
        if current.tag == "q":
            parts.append("\n")

    visit(node)
    return "".join(parts)


def hedged_quotes(html: str) -> list[tuple[str, str]]:
    """出典（data-scope 以外の details）にある、強さの語を含む文を (章見出し, 文) で返す。合否には使わない。"""
    parser = DocParser()
    parser.feed(html)
    quotes: list[tuple[str, str]] = []
    heading = ""
    for node in walk(parser.root):
        if node.tag == "h2":
            heading = norm_heading(visible_text(node))
        if node.tag != "details" or "data-scope" in node.attrs:
            continue
        if any(item.tag == "details" for item in ancestors(node)):
            continue
        items = [item for item in walk(node) if is_quote_leaf(item)]
        if not items:
            items = [child for child in node.elements() if child.tag != "summary"]
        body = "\n".join(source_text(item) for item in items)
        for sentence in SENTENCE_SPLIT_RE.split(body):
            sentence = sentence.lstrip(" \t—:/").rstrip(" \t—:")
            sentence = LEADING_ELLIPSIS_RE.sub("", sentence)
            if HEDGE_RE.search(sentence):
                quotes.append((heading, sentence))
    return quotes
