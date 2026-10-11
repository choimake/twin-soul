"""図のルール（点と線、SVG の線と文字、図の役、動く図）。"""

from __future__ import annotations

import re

from css import Rule, Sheet, animation_names, first_token, matches, moves_position, styles_for
from geometry import path_points, point_inside, rect_interior, text_width
from htmldoc import Node, ancestors, contains, visible_text, walk


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
