"""<style> の CSS を、検査に要る範囲だけ簡易に解釈する。"""

from __future__ import annotations

import re

from htmldoc import Node, visible_text_raw, walk


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


class Rule:
    def __init__(self, selectors: list[str], decls: dict[str, str]) -> None:
        self.selectors = selectors
        self.decls = decls


class Sheet:
    def __init__(self) -> None:
        self.rules: list[Rule] = []
        self.keyframes: dict[str, list[dict[str, str]]] = {}
        self.motion_bodies: list[str] = []
        self.narrow_rules: list[Rule] = []


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
            inner = Sheet()
            for inner_prelude, inner_body in parse_blocks(body):
                consume(inner_prelude, inner_body, inner)
            sheet.narrow_rules.extend(inner.rules)
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
    for name, value in re.findall(r"\[\s*([\w-]+)\s*(?:=\s*[\"']?([^\"'\]]*)[\"']?\s*)?\]", rest):
        if name not in node.attrs or (value and node.attrs[name] != value):
            return False
    rest = re.sub(r"\[[^\]]*\]", "", rest)
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


def first_token(value: str, default: str = "") -> str:
    parts = value.split()
    return parts[0] if parts else default


def px_value(value: str) -> float | None:
    match = re.match(r"^\s*(\d+(?:\.\d+)?)px\s*$", value)
    return float(match.group(1)) if match else None
