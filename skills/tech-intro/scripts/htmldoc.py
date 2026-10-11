"""HTML を木に組み、要素をたどって文字を取り出す。"""

from __future__ import annotations

import re
from html.parser import HTMLParser


VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "source",
    "track",
    "wbr",
    "rect",
    "circle",
    "ellipse",
    "line",
    "polyline",
    "polygon",
    "path",
    "use",
    "image",
    "stop",
}


class Text:
    def __init__(self, data: str) -> None:
        self.data = data


class Node:
    def __init__(self, tag: str, attrs: dict[str, str], parent: Node | None) -> None:
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children: list[Node | Text] = []

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def elements(self) -> list[Node]:
        return [child for child in self.children if isinstance(child, Node)]


class DocParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document", {}, None)
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._add(tag, attrs, push=tag not in VOID_TAGS)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._add(tag, attrs, push=False)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                self.stack = self.stack[:index]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(Text(data))

    def _add(self, tag: str, attrs: list[tuple[str, str | None]], push: bool) -> None:
        parent = self.stack[-1]
        element = Node(tag, {key: value or "" for key, value in attrs}, parent)
        parent.children.append(element)
        if push:
            self.stack.append(element)


def walk(node: Node):
    if node.tag != "document":
        yield node
    for child in node.elements():
        yield from walk(child)


def visible_text(node: Node) -> str:
    parts: list[str] = []

    def visit(current: Node | Text) -> None:
        if isinstance(current, Text):
            parts.append(current.data)
            return
        if current.tag in {"style", "script"}:
            return
        for child in current.children:
            visit(child)

    visit(node)
    return "".join(parts)


def visible_text_raw(node: Node) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, Text):
            parts.append(child.data)
        elif isinstance(child, Node):
            parts.append(visible_text_raw(child))
    return "".join(parts)


def contains(ancestor: Node, node: Node) -> bool:
    current: Node | None = node
    while current is not None:
        if current is ancestor:
            return True
        current = current.parent
    return False


def ancestors(node: Node):
    current = node.parent
    while current is not None and current.tag != "document":
        yield current
        current = current.parent


def norm_heading(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"^[0-9０-９]+[.．、]\s*", "", collapsed)
