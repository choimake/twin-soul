#!/usr/bin/env python3
"""tech-intro の単一 HTML を、機械的に判定できる項目だけ検査する。

Python 3 の標準ライブラリだけで動く。終了コード 0 は指摘なし。
指摘があるときは 1 で、id と理由を 1 行ずつ出す。

見ないもの: 公式と本文の一致、読み手が説明できるか、用語の訳、章の理解順、
図のラベルが本文の語か。
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

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

POSITION_PROPS = {"left", "top", "right", "bottom", "offset-distance", "transform"}
ANIMATION_KEYWORDS = {
    "none",
    "linear",
    "ease",
    "ease-in",
    "ease-out",
    "ease-in-out",
    "infinite",
    "forwards",
    "backwards",
    "both",
    "alternate",
    "reverse",
    "alternate-reverse",
    "paused",
    "running",
    "normal",
    "step-start",
    "step-end",
}
BANNED_PHRASES = (
    "正本",
    "日本語の公式ページは見つからなかった",
    "日本語の公式ドキュメントは見つからなかった",
    "日本語の公式ページは無い",
    "日本語版は見つからなかった",
)
CDN_HOSTS = ("unpkg.com", "cdn.jsdelivr.net", "cdnjs.cloudflare.com", "esm.sh")
NUMBER_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
PATH_TOKEN_RE = re.compile(
    r"[MmLlHhVvCcSsQqTtAaZz]|" + NUMBER_RE.pattern
)


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


class Rule:
    def __init__(self, selectors: list[str], decls: dict[str, str]) -> None:
        self.selectors = selectors
        self.decls = decls


class Sheet:
    def __init__(self) -> None:
        self.rules: list[Rule] = []
        self.keyframes: dict[str, list[dict[str, str]]] = {}
        self.motion_bodies: list[str] = []


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


def contains(ancestor: Node, node: Node) -> bool:
    current: Node | None = node
    while current is not None:
        if current is ancestor:
            return True
        current = current.parent
    return False


def norm_heading(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"^[0-9０-９]+[.．、]\s*", "", collapsed)


def label_of(node: Node) -> str:
    classes = node.attrs.get("class", "").split()
    if classes:
        return f"{node.tag}.{classes[0]}"
    return node.tag


def looks_like_node(node: Node) -> bool:
    return any(re.search(r"box|node|card", name) for name in node.classes)


def labeled_children(node: Node, skip: Node | None = None) -> list[Node]:
    found = []
    for child in node.elements():
        if skip is not None and contains(child, skip):
            continue
        if visible_text(child).strip() and looks_like_node(child):
            found.append(child)
    return found


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def parse_blocks(css: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    index = 0
    length = len(css)
    while index < length:
        while index < length and css[index].isspace():
            index += 1
        if index >= length:
            break
        start = index
        while index < length and css[index] != "{":
            index += 1
        if index >= length:
            break
        prelude = css[start:index].strip()
        index += 1
        depth = 1
        body_start = index
        while index < length and depth:
            if css[index] == "{":
                depth += 1
            elif css[index] == "}":
                depth -= 1
            index += 1
        blocks.append((prelude, css[body_start : index - 1]))
    return blocks


def split_csv(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(char)
    if buf:
        parts.append("".join(buf).strip())
    return [part for part in parts if part]


def parse_decls(body: str) -> dict[str, str]:
    decls: dict[str, str] = {}
    for part in body.split(";"):
        if ":" not in part:
            continue
        prop, value = part.split(":", 1)
        decls[prop.strip().lower()] = value.strip()
    return decls


def consume(prelude: str, body: str, sheet: Sheet) -> None:
    lowered = prelude.strip().lower()
    if lowered.startswith("@keyframes") or lowered.startswith("@-webkit-keyframes"):
        name = prelude.split()[1]
        sheet.keyframes[name] = [parse_decls(step_body) for _, step_body in parse_blocks(body)]
        return
    if lowered.startswith("@media"):
        if "prefers-reduced-motion" in lowered:
            sheet.motion_bodies.append(body)
            return
        if "max-width" in lowered:
            return
        for inner_prelude, inner_body in parse_blocks(body):
            consume(inner_prelude, inner_body, sheet)
        return
    if lowered.startswith("@"):
        return
    sheet.rules.append(Rule(split_csv(prelude), parse_decls(body)))


def parse_sheet(css: str) -> Sheet:
    sheet = Sheet()
    for prelude, body in parse_blocks(strip_comments(css)):
        if prelude:
            consume(prelude, body, sheet)
    return sheet


def element_selector(selector: str) -> str | None:
    if "::" in selector or "+" in selector or "~" in selector:
        return None
    stripped = re.sub(r":[a-zA-Z-]+(?:\([^)]*\))?", "", selector).strip()
    return stripped or None


def compounds_of(selector: str) -> list[tuple[str, str]] | None:
    cleaned = element_selector(selector)
    if not cleaned:
        return None
    tokens: list[str] = []
    for piece in re.split(r"(\s*>\s*|\s+)", cleaned):
        if piece.strip() == ">":
            tokens.append(">")
        elif piece.strip():
            tokens.append(piece.strip())
        elif piece:
            tokens.append(" ")
    if not tokens or tokens[0] in {">", " "}:
        return None
    compounds = [("", tokens[0])]
    index = 1
    while index < len(tokens):
        combinator = " "
        if tokens[index] in {">", " "}:
            combinator = tokens[index]
            index += 1
        if index >= len(tokens):
            return None
        compounds.append((combinator, tokens[index]))
        index += 1
    return compounds


def match_compound(node: Node, compound: str) -> bool:
    if node.tag == "document":
        return False
    if compound == "*":
        return True
    rest = compound
    tag_match = re.match(r"^[a-zA-Z][\w-]*", rest)
    if tag_match:
        if node.tag != tag_match.group(0).lower():
            return False
        rest = rest[tag_match.end() :]
    classes = re.findall(r"\.([_a-zA-Z][\w-]*)", rest)
    if any(name not in node.classes for name in classes):
        return False
    rest = re.sub(r"\.([_a-zA-Z][\w-]*)", "", rest)
    id_match = re.search(r"#([_a-zA-Z][\w-]*)", rest)
    if id_match and node.attrs.get("id") != id_match.group(1):
        return False
    rest = re.sub(r"#([_a-zA-Z][\w-]*)", "", rest)
    return rest == ""


def matches(node: Node, selector: str) -> bool:
    compounds = compounds_of(selector)
    if not compounds:
        return False
    index = len(compounds) - 1
    current: Node | None = node
    if current is None or not match_compound(current, compounds[index][1]):
        return False
    while index > 0:
        combinator = compounds[index][0]
        index -= 1
        compound = compounds[index][1]
        if combinator == ">":
            parent = current.parent if current else None
            if parent is None or not match_compound(parent, compound):
                return False
            current = parent
            continue
        parent = current.parent if current else None
        found = False
        while parent is not None:
            if match_compound(parent, compound):
                current = parent
                found = True
                break
            parent = parent.parent
        if not found:
            return False
    return True


def styles_for(node: Node, rules: list[Rule]) -> dict[str, str]:
    decls: dict[str, str] = {}
    for rule in rules:
        for selector in rule.selectors:
            if matches(node, selector):
                decls.update(rule.decls)
    decls.update(parse_decls(node.attrs.get("style", "")))
    return decls


def animation_names(decls: dict[str, str]) -> list[str]:
    if "animation-name" in decls:
        return [
            name.strip()
            for name in decls["animation-name"].split(",")
            if name.strip() and name.strip() != "none"
        ]
    shorthand = decls.get("animation", "")
    if not shorthand:
        return []
    names: list[str] = []
    for chunk in shorthand.split(","):
        for token in chunk.split():
            if token in ANIMATION_KEYWORDS or re.match(r"^-?\d", token):
                continue
            if token.endswith("ms") or re.fullmatch(r"\d+(?:\.\d+)?s", token):
                continue
            names.append(token)
            break
    return [name for name in names if name != "none"]


def moves_position(names: list[str], keyframes: dict[str, list[dict[str, str]]]) -> bool:
    for name in names:
        for decls in keyframes.get(name, []):
            if any(prop in POSITION_PROPS for prop in decls):
                return True
    return False


def style_text(root: Node) -> str:
    chunks = []
    for node in walk(root):
        if node.tag == "style":
            chunks.append(visible_text_raw(node))
    return "\n".join(chunks)


def visible_text_raw(node: Node) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, Text):
            parts.append(child.data)
        elif isinstance(child, Node):
            parts.append(visible_text_raw(child))
    return "".join(parts)


def find_toc(root: Node) -> Node | None:
    fallback = None
    for node in walk(root):
        if "toc" in node.classes:
            return node
        if node.attrs.get("aria-label") == "目次":
            fallback = fallback or node
    return fallback


def split_tracks(value: str) -> list[str]:
    tracks: list[str] = []
    buf: list[str] = []
    depth = 0
    for char in value.strip():
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char.isspace() and depth == 0:
            if buf:
                tracks.append("".join(buf))
                buf = []
            continue
        buf.append(char)
    if buf:
        tracks.append("".join(buf))
    return tracks


def check_external(html: str, findings: list[str]) -> None:
    if re.search(r"<script\b[^>]*\bsrc\s*=", html, flags=re.I):
        findings.append("external: 外部 script がある。確認クイズの採点もファイル内に書く")
    if re.search(r"<link\b[^>]*\brel\s*=\s*['\"]stylesheet", html, flags=re.I):
        findings.append("external: 外部 stylesheet がある。CSS はファイル内に書く")
    for host in CDN_HOSTS:
        if host in html:
            findings.append(f"external: CDN がある ({host})")
    if re.search(r"\bmermaid(?:\.min)?\.js\b", html, flags=re.I) or re.search(
        r"class\s*=\s*['\"][^'\"]*\bmermaid\b", html, flags=re.I
    ):
        findings.append("external: Mermaid がある")


def check_motion(sheet: Sheet, findings: list[str]) -> None:
    animated = False
    for rule in sheet.rules:
        if animation_names(rule.decls):
            animated = True
            break
    if not animated:
        return
    if not sheet.motion_bodies:
        findings.append("motion: 動きがあるのに prefers-reduced-motion: reduce が無い")
        return
    for body in sheet.motion_bodies:
        compact = re.sub(r"\s+", "", body.lower())
        if (
            "animation:none" in compact
            or "animation-name:none" in compact
            or "animation-play-state:paused" in compact
            or "display:none" in compact
        ):
            return
    findings.append("motion: prefers-reduced-motion: reduce で点の動きが止まらない")


def check_toc(root: Node, sheet: Sheet, findings: list[str]) -> None:
    toc = find_toc(root)
    headings = [
        norm_heading(visible_text(node))
        for node in walk(root)
        if node.tag == "h2" and (toc is None or not contains(toc, node))
    ]
    if toc is None:
        if headings:
            findings.append("toc-text: 目次が無い")
        return
    links = [norm_heading(visible_text(node)) for node in walk(toc) if node.tag == "a"]
    if links != headings:
        findings.append(f"toc-text: 目次と見出しが違う。目次={links} 見出し={headings}")
    check_toc_side(toc, sheet, findings)


def check_toc_side(toc: Node, sheet: Sheet, findings: list[str]) -> None:
    parent = toc.parent
    if parent is None:
        findings.append("toc-side: 目次の親が無い")
        return
    parent_style = styles_for(parent, sheet.rules)
    if parent_style.get("display") != "grid":
        findings.append("toc-side: 目次の親が横並びの grid でない")
        return
    tracks = split_tracks(parent_style.get("grid-template-columns", ""))
    if len(tracks) < 2:
        findings.append("toc-side: 目次を右に分ける列が無い")
        return
    order = styles_for(toc, sheet.rules).get("order", "0").strip()
    if re.match(r"^-\d", order):
        findings.append("toc-side: デスクトップで目次が本文より前に出る")
        return
    children = parent.elements()
    if toc not in children:
        findings.append("toc-side: 目次が grid の直下に無い")
        return
    index = children.index(toc)
    grid_column = styles_for(toc, sheet.rules).get("grid-column", "")
    on_last = re.match(r"^(-?\d+)", grid_column.strip())
    if on_last and int(on_last.group(1)) in {len(tracks), -1}:
        return
    if index != len(children) - 1 or index == 0:
        findings.append("toc-side: 目次が右の列に無い")


def check_banned(root: Node, findings: list[str]) -> None:
    text = visible_text(root)
    for phrase in BANNED_PHRASES:
        if phrase in text:
            findings.append(f"banned: 「{phrase}」がある")
    if "§" in text:
        findings.append("banned: § がある。章番号は「4章」「7章の3」と書く")


def first_token(value: str, default: str = "") -> str:
    parts = value.split()
    return parts[0] if parts else default


def is_spanning_line(decls: dict[str, str]) -> bool:
    if first_token(decls.get("position", "")) != "absolute":
        return False
    height = decls.get("height", "").strip()
    height_match = re.match(r"^(\d+(?:\.\d+)?)px$", height)
    if not height_match or float(height_match.group(1)) > 4:
        return False
    left = decls.get("left")
    right = decls.get("right")
    width = decls.get("width", "")
    spans = (left not in {None, "auto"} and right not in {None, "auto"}) or "100%" in width
    return spans


def check_dot_line(root: Node, sheet: Sheet, findings: list[str]) -> None:
    for rule in sheet.rules:
        if not is_spanning_line(rule.decls):
            continue
        for selector in rule.selectors:
            if "::before" not in selector and "::after" not in selector:
                continue
            subject = selector.split("::", 1)[0].strip()
            if not subject:
                continue
            for node in walk(root):
                if not matches(node, subject):
                    continue
                if len(labeled_children(node)) < 2:
                    continue
                if moving_dot_inside(node, sheet):
                    findings.append(
                        f"dot-line: 線が箱の並びを端から端まで貫いている（{selector}）。"
                        "線は箱の縁から次の箱の縁までにする"
                    )


def moving_dot_inside(node: Node, sheet: Sheet) -> bool:
    for descendant in walk(node):
        if descendant is node or visible_text(descendant).strip():
            continue
        names = animation_names(styles_for(descendant, sheet.rules))
        if names and moves_position(names, sheet.keyframes):
            return True
    return False


def offset_parent(node: Node, rules: list[Rule]) -> Node | None:
    position = first_token(styles_for(node, rules).get("position", "static"), "static")
    parent = node.parent
    if position not in {"absolute", "fixed"}:
        return parent
    while parent is not None and parent.tag != "document":
        parent_position = first_token(styles_for(parent, rules).get("position", "static"), "static")
        if parent_position in {"relative", "absolute", "fixed", "sticky"}:
            return parent
        parent = parent.parent
    return node.parent


def check_dot_travel(root: Node, sheet: Sheet, findings: list[str]) -> None:
    for node in walk(root):
        if visible_text(node).strip():
            continue
        names = animation_names(styles_for(node, sheet.rules))
        if not names or not moves_position(names, sheet.keyframes):
            continue
        parent = offset_parent(node, sheet.rules)
        if parent is None:
            continue
        if len(labeled_children(parent, skip=node)) >= 2:
            findings.append(
                f"dot-travel: 点が箱の上を動いている（{label_of(node)} の基準が {label_of(parent)}）。"
                "点は箱と箱のあいだの要素の中だけを動かす"
            )
            continue
        if looks_like_node(parent) and visible_text(parent).strip():
            findings.append(
                f"dot-travel: 点が箱の中を動いている（{label_of(parent)}）。"
                "点は箱の外の線だけを動かす"
            )


def path_points(d: str) -> list[tuple[float, float]]:
    tokens = PATH_TOKEN_RE.findall(d)
    index = 0
    cx = cy = 0.0
    start_x = start_y = 0.0
    prev_cmd = ""
    prev_cx = prev_cy = 0.0
    points: list[tuple[float, float]] = []

    def read_number() -> float:
        nonlocal index
        if index >= len(tokens) or not NUMBER_RE.fullmatch(tokens[index]):
            raise ValueError("path")
        value = float(tokens[index])
        index += 1
        return value

    def add_line(x: float, y: float) -> None:
        nonlocal cx, cy
        points.extend(densify([(cx, cy), (x, y)]))
        cx, cy = x, y

    def add_curve(p1: tuple[float, float], p2: tuple[float, float], p3: tuple[float, float]) -> None:
        nonlocal cx, cy, prev_cx, prev_cy
        samples = cubic((cx, cy), p1, p2, p3)
        points.extend(densify(samples))
        prev_cx, prev_cy = p2
        cx, cy = p3

    while index < len(tokens):
        token = tokens[index]
        if not NUMBER_RE.fullmatch(token):
            command = token
            index += 1
        else:
            command = "L" if prev_cmd in {"M", "L"} else "l" if prev_cmd in {"m", "l"} else prev_cmd
        prior = prev_cmd
        prev_cmd = command
        relative = command.islower()
        cmd = command.upper()
        if cmd == "M":
            x, y = read_number(), read_number()
            if relative:
                x += cx
                y += cy
            cx, cy = start_x, start_y = x, y
            points.append((cx, cy))
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                x, y = read_number(), read_number()
                if relative:
                    x += cx
                    y += cy
                add_line(x, y)
            prev_cmd = "l" if relative else "L"
        elif cmd == "L":
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                x, y = read_number(), read_number()
                if relative:
                    x += cx
                    y += cy
                add_line(x, y)
        elif cmd == "H":
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                x = read_number()
                if relative:
                    x += cx
                add_line(x, cy)
        elif cmd == "V":
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                y = read_number()
                if relative:
                    y += cy
                add_line(cx, y)
        elif cmd == "C":
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                x1, y1 = read_number(), read_number()
                x2, y2 = read_number(), read_number()
                x, y = read_number(), read_number()
                if relative:
                    x1 += cx
                    y1 += cy
                    x2 += cx
                    y2 += cy
                    x += cx
                    y += cy
                add_curve((x1, y1), (x2, y2), (x, y))
        elif cmd == "S":
            reflected = prior.upper() in {"C", "S"}
            while index < len(tokens) and NUMBER_RE.fullmatch(tokens[index]):
                if reflected:
                    x1, y1 = 2 * cx - prev_cx, 2 * cy - prev_cy
                else:
                    x1, y1 = cx, cy
                x2, y2 = read_number(), read_number()
                x, y = read_number(), read_number()
                if relative:
                    x2 += cx
                    y2 += cy
                    x += cx
                    y += cy
                add_curve((x1, y1), (x2, y2), (x, y))
                reflected = True
        elif cmd in {"Q", "T", "A"}:
            raise ValueError(cmd)
        elif cmd == "Z":
            add_line(start_x, start_y)
        else:
            raise ValueError(command)
    return points


def cubic(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
) -> list[tuple[float, float]]:
    samples = []
    for step in range(25):
        t = step / 24
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        samples.append((x, y))
    return samples


def densify(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if len(points) < 2:
        return list(points)
    dense: list[tuple[float, float]] = []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        steps = max(int(max(abs(x2 - x1), abs(y2 - y1))), 1)
        for step in range(steps):
            t = step / steps
            dense.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
    dense.append(points[-1])
    return dense


def rect_interior(node: Node) -> tuple[float, float, float, float] | None:
    try:
        x = float(node.attrs.get("x") or 0)
        y = float(node.attrs.get("y") or 0)
        width = float(node.attrs.get("width") or 0)
        height = float(node.attrs.get("height") or 0)
    except ValueError:
        return None
    inset = min(4.0, width * 0.2, height * 0.2)
    if width <= inset * 2 or height <= inset * 2:
        return None
    return (x + inset, y + inset, x + width - inset, y + height - inset)


def point_inside(x: float, y: float, interior: tuple[float, float, float, float]) -> bool:
    left, top, right, bottom = interior
    return left < x < right and top < y < bottom


def check_svg(root: Node, sheet: Sheet, findings: list[str]) -> None:
    for svg in walk(root):
        if svg.tag != "svg":
            continue
        interiors = [rect for node in walk(svg) if node.tag == "rect" and (rect := rect_interior(node))]
        for path in walk(svg):
            if path.tag != "path":
                continue
            names = animation_names(styles_for(path, sheet.rules))
            if not names:
                continue
            d = path.attrs.get("d", "")
            try:
                points = path_points(d)
            except ValueError as error:
                findings.append(
                    f"svg-cross: 動く線を検査できない（{error}）。直線か三次曲線だけにする"
                )
                continue
            if any(
                point_inside(x, y, interior) for x, y in points for interior in interiors
            ):
                findings.append(
                    "svg-cross: 動く線が箱の面を横切っている。"
                    "線は箱の外側で止める"
                )


def font_px(node: Node, sheet: Sheet) -> float | None:
    for current in [node, *ancestors(node)]:
        value = current.attrs.get("font-size") or styles_for(current, sheet.rules).get("font-size")
        if not value:
            continue
        value = value.strip()
        try:
            if value.endswith("rem"):
                return float(value[:-3]) * 16
            if value.endswith("px"):
                return float(value[:-2])
            return float(value)
        except ValueError:
            return None
    return 16.0


def text_width(text: str, size: float) -> float:
    return sum(size if unicodedata.east_asian_width(char) in "WF" else size * 0.55 for char in text)


def check_svg_text(root: Node, sheet: Sheet, findings: list[str]) -> None:
    for text in walk(root):
        if text.tag != "text" or text.parent is None or "transform" in text.attrs:
            continue
        label = visible_text(text).strip()
        size = font_px(text, sheet)
        try:
            x = float(text.attrs.get("x") or "nan")
            y = float(text.attrs.get("y") or "nan")
        except ValueError:
            continue
        if not label or size is None or x != x or y != y:
            continue
        width = text_width(label, size)
        anchor = text.attrs.get("text-anchor") or styles_for(text, sheet.rules).get("text-anchor", "start")
        left = {"middle": x - width / 2, "end": x - width}.get(anchor.strip(), x)
        for rect in text.parent.children:
            if not isinstance(rect, Node) or rect.tag != "rect":
                continue
            try:
                rx = float(rect.attrs.get("x") or 0)
                ry = float(rect.attrs.get("y") or 0)
                rw = float(rect.attrs.get("width") or 0)
                rh = float(rect.attrs.get("height") or 0)
            except ValueError:
                continue
            if not (rx < x < rx + rw and ry < y - size / 3 < ry + rh):
                continue
            if left < rx - 2 or left + width > rx + rw + 2:
                findings.append(
                    f"svg-text: 「{label}」が箱の幅（{rw:g}）からはみ出す見込み。"
                    "文字を短くするか、行を分けるか、箱を広げる"
                )
            break


FIG_ROLES = (
    "what",
    "need",
    "cast",
    "resume",
    "struct",
    "branch",
)


def check_fig_roles(root: Node, findings: list[str]) -> None:
    headings = [node for node in walk(root) if node.tag == "h2"]
    if len(headings) < 4:
        return
    present: set[str] = set()
    skipped: set[str] = set()
    for node in walk(root):
        role = node.attrs.get("data-fig", "").strip()
        if role:
            present.add(role)
        for part in re.split(r"[\s,]+", node.attrs.get("data-fig-skip", "")):
            if part:
                skipped.add(part)
    missing = [role for role in FIG_ROLES if role not in present and role not in skipped]
    if missing:
        findings.append("fig-role: 図が無い役がある: " + ", ".join(missing))


NARROW_PX = 360


def px_value(value: str) -> float | None:
    match = re.match(r"^\s*(\d+(?:\.\d+)?)px\s*$", value)
    return float(match.group(1)) if match else None


def ancestors(node: Node):
    current = node.parent
    while current is not None and current.tag != "document":
        yield current
        current = current.parent


def scrolls_x(node: Node, sheet: Sheet) -> bool:
    decls = styles_for(node, sheet.rules)
    return any(first_token(decls.get(prop, "")) in {"auto", "scroll"} for prop in ("overflow-x", "overflow"))


def wraps(node: Node, sheet: Sheet) -> bool:
    for current in [node, *ancestors(node)]:
        decls = styles_for(current, sheet.rules)
        if first_token(decls.get("overflow-wrap", decls.get("word-wrap", ""))) in {"anywhere", "break-word"}:
            return True
        if first_token(decls.get("word-break", "")) in {"break-all", "break-word"}:
            return True
    return False


def check_responsive(root: Node, sheet: Sheet, css: str, findings: list[str]) -> None:
    viewport = [
        node
        for node in walk(root)
        if node.tag == "meta" and node.attrs.get("name", "").lower() == "viewport"
    ]
    if not viewport or "width=device-width" not in viewport[0].attrs.get("content", "").replace(" ", ""):
        findings.append("responsive: meta viewport（width=device-width）が無い")
    if not re.search(r"@media[^{]*max-width", strip_comments(css)):
        findings.append("responsive: 狭い幅の @media (max-width) が無い")
    for node in walk(root):
        if node.tag == "svg":
            if "viewBox" not in node.attrs and "viewbox" not in node.attrs:
                findings.append("responsive: viewBox の無い svg がある。幅に合わせて縮まない")
            raw = node.attrs.get("width", "").strip()
            width = px_value(raw if raw.endswith("px") else raw + "px") if raw else None
            decls = styles_for(node, sheet.rules)
            fluid = "100%" in decls.get("width", "") or "100%" in decls.get("max-width", "")
            if width is not None and width > NARROW_PX and not fluid:
                findings.append(
                    f"responsive: svg の幅が {int(width)}px 固定。CSS で width か max-width を 100% にする"
                )
        if node.tag == "figure":
            overflow = styles_for(node, sheet.rules)
            for prop in ("overflow-x", "overflow"):
                if first_token(overflow.get(prop, "")) in {"auto", "scroll"}:
                    findings.append("responsive: 図が横スクロールする。狭い幅では縮めるか、縦に並べ替える")
                    break
    for node in walk(root):
        if node.tag != "table":
            continue
        if not scrolls_x(node, sheet) and not any(
            scrolls_x(ancestor, sheet) for ancestor in ancestors(node)
        ):
            findings.append("responsive: 表が横スクロールの枠に入っていない。overflow-x: auto の要素で包む")
    for node in walk(root):
        if node.tag != "code" or any(ancestor.tag == "pre" for ancestor in ancestors(node)):
            continue
        if not wraps(node, sheet):
            findings.append(
                "responsive: 本文中のコードが折り返さない。overflow-wrap: anywhere を本文か code に付ける"
            )
        break
    for rule in sheet.rules:
        value = px_value(rule.decls.get("min-width", ""))
        if value is not None and value > NARROW_PX:
            findings.append(
                f"responsive: min-width が {int(value)}px（{', '.join(rule.selectors)}）。狭い画面からはみ出す"
            )


MOTION_ROLES = ("resume", "branch")


def check_motion_figs(root: Node, sheet: Sheet, findings: list[str]) -> None:
    for node in walk(root):
        role = node.attrs.get("data-fig", "").strip()
        if role not in MOTION_ROLES:
            continue
        animated = any(
            animation_names(styles_for(descendant, sheet.rules))
            for descendant in walk(node)
            if descendant is not node
        )
        if not animated:
            findings.append(f"motion-fig: {role} の図に動く点が無い。動きは動く図で見せる")


def check_early_detail(root: Node, findings: list[str]) -> None:
    nodes = list(walk(root))
    headings = [index for index, node in enumerate(nodes) if node.tag == "h2"]
    if len(headings) < 4:
        return
    for node in nodes[headings[0] : headings[2]]:
        if node.tag in {"pre", "code"}:
            findings.append("early-detail: 1章と2章にコードがある。細部は形と一例のあとに出す")
            return


def check_goals(root: Node, findings: list[str]) -> None:
    nodes = list(walk(root))
    headings = [node for node in nodes if node.tag == "h2"]
    if len(headings) < 4:
        return
    first_h2 = nodes.index(headings[0])
    for index, node in enumerate(nodes):
        if "data-goals" not in node.attrs:
            continue
        items = [child for child in walk(node) if child.tag == "li" and visible_text(child).strip()]
        if len(items) < 2:
            findings.append("goals: この入門でわかることの一覧が2項目に満たない")
        elif index > first_h2:
            findings.append("goals: この入門でわかることの一覧が最初の章より後にある")
        return
    findings.append("goals: 冒頭に、この入門でわかることの一覧（data-goals）が無い")


def check_scope(root: Node, findings: list[str]) -> None:
    nodes = list(walk(root))
    headings = [node for node in nodes if node.tag == "h2"]
    if len(headings) < 4:
        return
    marked = [node for node in nodes if "data-scope" in node.attrs]
    if not marked:
        findings.append("scope: 冒頭に、対象・版・確認日・扱わないものの注記（data-scope）が無い")
        return
    node = marked[0]
    if node.tag != "details":
        findings.append("scope: 対象と版の注記は details で折りたたむ")
    elif "open" in node.attrs:
        findings.append("scope: 対象と版の注記は閉じておく（open を付けない）")
    if nodes.index(node) > nodes.index(headings[0]):
        findings.append("scope: 対象と版の注記が最初の章より後にある")


PROSE_SKIP_TAGS = {"figure", "pre", "table", "details", "aside", "nav", "script", "style", "svg", "form", "fieldset"}
PROSE_SKIP_ATTRS = ("data-quiz", "data-goals")


def chapter_prose(root: Node) -> list[tuple[str, int, int]]:
    chapters: list[list] = []

    def visit(node: Node, counting: bool) -> None:
        for child in node.children:
            if isinstance(child, Text):
                if chapters and counting:
                    chapters[-1][1] += len(re.sub(r"\s+", "", child.data))
                continue
            if child.tag == "h2":
                chapters.append([norm_heading(visible_text(child)), 0, 0])
                continue
            if child.tag == "dfn" and chapters:
                chapters[-1][2] += 1
            skip = child.tag in PROSE_SKIP_TAGS or any(attr in child.attrs for attr in PROSE_SKIP_ATTRS)
            visit(child, counting and not skip)

    visit(root, True)
    return [(title, count, terms) for title, count, terms in chapters]


END_CHAPTERS = ("チェックリスト", "確かめられなかったこと", "確認クイズ")
MAX_TERMS = 3


def is_end_chapter(title: str) -> bool:
    return any(phrase in title for phrase in END_CHAPTERS)


def check_endings(root: Node, findings: list[str]) -> None:
    chapters = chapter_prose(root)
    if len(chapters) < 4:
        return
    titles = [title for title, _, _ in chapters]
    minor = [
        norm_heading(visible_text(node)) for node in walk(root) if node.tag in {"h3", "h4", "h5", "h6"}
    ]
    for phrase in END_CHAPTERS:
        if any(phrase in title for title in titles):
            continue
        if any(phrase in title for title in minor):
            findings.append(f"endings: 「{phrase}」が章（h2）になっていない。目次から見つけられるよう h2 にする")
        else:
            findings.append(f"endings: 「{phrase}」の章が無い")


def check_terms(root: Node, findings: list[str]) -> None:
    chapters = chapter_prose(root)
    if len(chapters) < 4:
        return
    if not any(terms for _, _, terms in chapters):
        findings.append("terms: 用語の定義に dfn が無い。初出で定義する語を dfn で囲む")
        return
    for title, _, terms in chapters:
        if terms > MAX_TERMS:
            findings.append(f"terms: 1章で {terms} 語を定義している（{title[:12]}…）。{MAX_TERMS} 語までにし、残りは要る章で出す")


MAX_GOALS = 5
MAX_HEADING = 25
MAX_CHAPTERS = 12
MAX_CHAPTER_PROSE = 600
MAX_TOTAL_PROSE = 4000


def check_volume(root: Node, findings: list[str]) -> None:
    if len(chapter_prose(root)) < 4:
        return
    chapters = [(title, count) for title, count, _ in chapter_prose(root) if not is_end_chapter(title)]
    for node in walk(root):
        if "data-goals" in node.attrs:
            items = [child for child in walk(node) if child.tag == "li"]
            if len(items) > MAX_GOALS:
                findings.append(f"volume: 要点が {len(items)} 個。{MAX_GOALS} 個までに絞る")
            break
    if len(chapters) > MAX_CHAPTERS:
        findings.append(f"volume: 章が {len(chapters)} 個。{MAX_CHAPTERS} 個までにまとめる")
    for title, count in chapters:
        heading = re.sub(r"^\d+[.．]\s*", "", title).replace(" ", "")
        if len(heading) > MAX_HEADING:
            findings.append(f"volume: 見出しが {len(heading)} 字（{heading[:12]}…）。{MAX_HEADING} 字までにする")
        if count > MAX_CHAPTER_PROSE:
            findings.append(f"volume: 章の文章が {count} 字（{heading[:12]}…）。{MAX_CHAPTER_PROSE} 字までにする")
    total = sum(count for _, count in chapters)
    if total > MAX_TOTAL_PROSE:
        findings.append(f"volume: 文章が合計 {total} 字。{MAX_TOTAL_PROSE} 字までに削る")


AGENT_SKILL_STATES = ("ある", "無い", "未確認")


def check_agent_skills(root: Node, findings: list[str]) -> None:
    if sum(1 for node in walk(root) if node.tag == "h2") < 4:
        return
    marked = [node for node in walk(root) if "data-agent-skills" in node.attrs]
    if not marked:
        findings.append("agent-skills: 公式 skill の章（data-agent-skills）が無い。有無は必ず章で書く")
        return
    node = marked[0]
    state = node.attrs.get("data-agent-skills", "").strip()
    if state not in AGENT_SKILL_STATES:
        findings.append(
            f"agent-skills: data-agent-skills は {' / '.join(AGENT_SKILL_STATES)} のどれか（今は「{state}」）"
        )
    if node.tag != "h2" and not any(child.tag == "h2" for child in walk(node)):
        findings.append("agent-skills: data-agent-skills は章（h2 か h2 を含む要素）に付ける")
    if not any(
        child.tag == "a" and child.attrs.get("href", "").startswith("https://") for child in walk(node)
    ):
        findings.append("agent-skills: 公式 skill の章に、確かめた場所の公式リンクが無い")


def check_html(html: str) -> list[str]:
    parser = DocParser()
    parser.feed(html)
    css = style_text(parser.root)
    sheet = parse_sheet(css)
    findings: list[str] = []
    check_responsive(parser.root, sheet, css, findings)
    check_external(html, findings)
    check_motion(sheet, findings)
    check_toc(parser.root, sheet, findings)
    check_banned(parser.root, findings)
    check_dot_line(parser.root, sheet, findings)
    check_dot_travel(parser.root, sheet, findings)
    check_svg(parser.root, sheet, findings)
    check_svg_text(parser.root, sheet, findings)
    check_fig_roles(parser.root, findings)
    check_goals(parser.root, findings)
    check_scope(parser.root, findings)
    check_agent_skills(parser.root, findings)
    check_volume(parser.root, findings)
    check_endings(parser.root, findings)
    check_terms(parser.root, findings)
    check_early_detail(parser.root, findings)
    check_motion_figs(parser.root, sheet, findings)
    return dedupe(findings)


def dedupe(findings: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    order: list[str] = []
    for item in findings:
        if item not in counts:
            order.append(item)
            counts[item] = 0
        counts[item] += 1
    output = []
    for item in order:
        if counts[item] > 1:
            output.append(f"{item}（{counts[item]}箇所）")
        else:
            output.append(item)
    return output


ENDING_BODY = """
<h2 id="x">チェックリスト</h2><p><dfn>topic</dfn> は名前である。</p>
<h2 id="y">確かめられなかったこと</h2>
<h2 id="z">確認クイズ</h2>
"""
ENDING_TOC = '<a href="#x">チェックリスト</a><a href="#y">確かめられなかったこと</a><a href="#z">確認クイズ</a>'
SCOPE_HTML = "<details data-scope><summary>対象と版</summary><p>確認日 2026-10-07。</p></details>"


def page(
    body: str,
    css: str = "",
    *,
    motion: bool = True,
    columns: str = "minmax(0, 1fr) 220px",
    toc_first: bool = False,
    toc_html: str | None = None,
    head_extra: str = "",
    ending: bool = False,
    scope: str | None = None,
) -> str:
    toc = toc_html or '<aside class="toc"><a href="#why">なぜ要るか</a></aside>'
    if scope is None and ending:
        scope = SCOPE_HTML
    if scope:
        body = scope + body
    if ending:
        body += ENDING_BODY
        toc = toc.replace("</aside>", ENDING_TOC + "</aside>")
    article = f"<article>{body}</article>"
    main = f"{toc}{article}" if toc_first else f"{article}{toc}"
    motion_css = ""
    if motion:
        motion_css = """
        @media (prefers-reduced-motion: reduce) {
          .dot, .flow { animation: none; }
        }
        """
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta name="viewport" content="width=device-width, initial-scale=1">{head_extra}<style>
.page {{ display: grid; grid-template-columns: {columns}; }}
{css}
@media (max-width: 820px) {{
  aside.toc {{ order: -1; }}
}}
{motion_css}
</style></head><body><div class="page">{main}</div></body></html>"""


PASS_HTML = page(
    """
    <h2 id="why">なぜ要るか</h2>
    <div class="row">
      <div class="box">event</div>
      <div class="link"><span class="dot"></span></div>
      <div class="box">trigger</div>
    </div>
    <svg viewBox="0 0 260 60">
      <path class="flow" d="M90 30 L160 30"/>
      <rect x="10" y="10" width="80" height="40"/>
      <rect x="160" y="10" width="80" height="40"/>
    </svg>
    """,
    """
    .row { display: flex; align-items: center; }
    .box { border: 1px solid #111; }
    .link { position: relative; width: 48px; height: 16px; }
    .link::before {
      content: "";
      position: absolute;
      left: 0; right: 0; top: 50%;
      height: 2px;
    }
    .dot { position: absolute; top: 0; width: 8px; height: 8px; animation: hop 1s linear infinite; }
    @keyframes hop { from { left: 0; } to { left: 40px; } }
    .flow { animation: dash 1s linear infinite; }
    @keyframes dash { from { stroke-dashoffset: 0; } to { stroke-dashoffset: -100; } }
    """,
)

CASES: list[tuple[str, str, set[str]]] = [
    ("pass", PASS_HTML, set()),
    (
        "dot-travel",
        page(
            """
            <h2 id="why">なぜ要るか</h2>
            <div class="row">
              <span class="dot"></span>
              <div class="box">event</div>
              <div class="box">trigger</div>
            </div>
            """,
            """
            .row { position: relative; }
            .box { border: 1px solid #111; }
            .dot { position: absolute; animation: move 1s linear infinite; }
            @keyframes move { from { left: 0; } to { left: 80px; } }
            """,
        ),
        {"dot-travel"},
    ),
    (
        "dot-line",
        page(
            """
            <h2 id="why">なぜ要るか</h2>
            <div class="row">
              <div class="box">event</div>
              <div class="link"><span class="dot"></span></div>
              <div class="box">trigger</div>
            </div>
            """,
            """
            .row { position: relative; display: flex; }
            .box { border: 1px solid #111; }
            .row::before {
              content: "";
              position: absolute;
              left: 8px; right: 8px; top: 50%;
              height: 2px;
            }
            .link { position: relative; width: 40px; }
            .dot { position: absolute; animation: hop 1s linear infinite; }
            @keyframes hop { from { left: 0; } to { left: 20px; } }
            """,
        ),
        {"dot-line"},
    ),
    (
        "svg-cross",
        page(
            """
            <h2 id="why">なぜ要るか</h2>
            <svg viewBox="0 0 300 80">
              <path class="flow" d="M10 30 L240 30"/>
              <rect x="20" y="10" width="80" height="40"/>
              <rect x="160" y="10" width="80" height="40"/>
            </svg>
            """,
            """
            .flow { animation: dash 1s linear infinite; }
            @keyframes dash { from { stroke-dashoffset: 0; } to { stroke-dashoffset: -100; } }
            """,
        ),
        {"svg-cross"},
    ),
    (
        "svg-text",
        page(
            """
            <h2 id="why">なぜ要るか</h2>
            <svg viewBox="0 0 300 80">
              <rect x="20" y="10" width="124" height="52"/>
              <text x="82" y="36" text-anchor="middle">同じプロセス・別プロセス</text>
              <rect x="160" y="10" width="124" height="52"/>
              <text x="222" y="36" text-anchor="middle">短い名前</text>
            </svg>
            """,
            "svg text { font-size: 12px; }",
        ),
        {"svg-text"},
    ),
    (
        "external",
        page(
            "<h2 id=\"why\">なぜ要るか</h2>",
            head_extra='<script src="https://unpkg.com/mermaid/dist/mermaid.min.js"></script>',
        ),
        {"external"},
    ),
    (
        "motion",
        page(
            "<h2 id=\"why\">なぜ要るか</h2><span class=\"dot\"></span>",
            ".dot { animation: blink 1s infinite; } @keyframes blink { from { opacity: 1; } to { opacity: 0; } }",
            motion=False,
        ),
        {"motion"},
    ),
    (
        "toc-text",
        page(
            "<h2 id=\"why\">なぜ要るか</h2>",
            toc_html='<aside class="toc"><a href="#why">別の見出し</a></aside>',
        ),
        {"toc-text"},
    ),
    (
        "toc-side",
        page(
            "<h2 id=\"why\">なぜ要るか</h2>",
            columns="220px minmax(0, 1fr)",
            toc_first=True,
        ),
        {"toc-side"},
    ),
    (
        "banned",
        page("<h2 id=\"why\">なぜ要るか</h2><p>公式の正本を見る。</p>"),
        {"banned"},
    ),
    (
        "fig-role",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <h2 id="a">なぜ要るか</h2>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">仕組み</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">仕組み</a>
            </aside>""",
            ending=True,
        ),
        {"fig-role"},
    ),
    (
        "fig-skip",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch choice owner compare prod limit">扱わない。</p>
            <h2 id="a">なぜ要るか</h2>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">仕組み</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">仕組み</a>
            </aside>""",
            ending=True,
        ),
        set(),
    ),
    (
        "goals",
        page(
            """
            <p data-fig-skip="what need cast resume struct branch choice owner compare prod limit">扱わない。</p>
            <h2 id="a">なぜ要るか</h2>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">仕組み</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">仕組み</a>
            </aside>""",
            ending=True,
        ),
        {"goals"},
    ),
    (
        "early-detail",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch choice owner compare prod limit">扱わない。</p>
            <h2 id="a">なぜ要るか</h2>
            <pre><code>step.run("load")</code></pre>
            <h2 id="b">登場人物</h2>
            <h2 id="c">仕組み</h2>
            <section data-agent-skills="無い"><h2 id="d">構造</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">仕組み</a>
              <a href="#d">構造</a>
            </aside>""",
            ending=True,
        ),
        {"early-detail"},
    ),
    (
        "motion-fig",
        page(
            """
            <h2 id="why">なぜ要るか</h2>
            <figure data-fig="resume">
              <div class="row"><div class="box">step</div><div class="box">step</div></div>
            </figure>
            """,
        ),
        {"motion-fig"},
    ),
    (
        "responsive",
        page(
            """
            <h2 id="why">なぜ要るか</h2>
            <figure><svg width="800" height="200"><rect x="0" y="0" width="10" height="10"/></svg></figure>
            <table><tr><td>a</td></tr></table>
            <p><code>step.waitForEvent("wait-for-cancellation")</code></p>
            """,
            "figure { overflow-x: auto; } .wide { min-width: 560px; }",
        ),
        {"responsive"},
    ),
    (
        "volume",
        page(
            """
            <ol data-goals><li>一</li><li>二</li><li>三</li><li>四</li><li>五</li><li>六</li></ol>
            <p data-fig-skip="what need cast resume struct branch">扱わない。</p>
            <h2 id="a">送る側と受け取る側を分けて部品を組み合わせるための通信の仕組みである</h2>
            <p>"""
            + "あ" * 700
            + """</p>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">公式 skill</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">送る側と受け取る側を分けて部品を組み合わせるための通信の仕組みである</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">公式 skill</a>
            </aside>""",
            ending=True,
        ),
        {"volume"},
    ),
    (
        "endings",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch">扱わない。</p>
            <h2 id="a">なぜ要るか</h2><p><dfn>node</dfn> は処理の単位である。</p>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">公式 skill</h2><a href="https://example.com/">確かめた場所</a>
            <h3>チェックリスト</h3><h3>確かめられなかったこと</h3><h3>確認クイズ</h3></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">公式 skill</a>
            </aside>""",
            scope=SCOPE_HTML,
        ),
        {"endings"},
    ),
    (
        "scope",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch">扱わない。</p>
            <h2 id="a">なぜ要るか</h2><p><dfn>node</dfn> は処理の単位である。</p>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">公式 skill</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">公式 skill</a>
            </aside>""",
            ending=True,
            scope='<details open data-scope><summary>対象と版</summary></details>',
        ),
        {"scope"},
    ),
    (
        "terms",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch">扱わない。</p>
            <h2 id="a">なぜ要るか</h2>
            <p><dfn>node</dfn>、<dfn>topic</dfn>、<dfn>message</dfn>、<dfn>callback</dfn> を定義する。</p>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="無い"><h2 id="d">公式 skill</h2><a href="https://example.com/">確かめた場所</a></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">公式 skill</a>
            </aside>""",
            ending=True,
        ),
        {"terms"},
    ),
    (
        "agent-skills",
        page(
            """
            <ol data-goals><li>何か</li><li>何ができるか</li></ol>
            <p data-fig-skip="what need cast resume struct branch choice owner compare prod limit">扱わない。</p>
            <h2 id="a">なぜ要るか</h2>
            <h2 id="b">登場人物</h2>
            <h2 id="c">構造</h2>
            <section data-agent-skills="たぶんある"><h2 id="d">公式 skill</h2></section>
            """,
            toc_html="""<aside class="toc">
              <a href="#a">なぜ要るか</a>
              <a href="#b">登場人物</a>
              <a href="#c">構造</a>
              <a href="#d">公式 skill</a>
            </aside>""",
            ending=True,
        ),
        {"agent-skills"},
    ),
]


def ids_of(findings: list[str]) -> set[str]:
    return {item.split(":", 1)[0] for item in findings}


def run_self_test() -> int:
    failed = False
    for name, html, expected in CASES:
        got = ids_of(check_html(html))
        if got != expected:
            failed = True
            print(f"{name}: expected {sorted(expected)} got {sorted(got)}", file=sys.stderr)
            for item in check_html(html):
                print(f"  {item}", file=sys.stderr)
    if failed:
        return 1
    print("self-test ok")
    return 0


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
        findings = check_html(path.read_text(encoding="utf-8"))
        if not findings:
            continue
        failed = True
        print(f"{path}:")
        for item in findings:
            print(f"  {item}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
