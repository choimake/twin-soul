"""図のルール（SVG の線と文字、図の役、動く図と無限の繰り返し）。"""

from __future__ import annotations

import re

from css import Sheet, animation_names, strip_comments, style_text, styles_for
from geometry import path_points, point_inside, rect_interior, text_width
from htmldoc import Node, ancestors, visible_text, walk


def check_motion_stop(root: Node, sheet: Sheet, findings: list[str]) -> None:
    sources = [style_text(root)]
    sources.extend(node.attrs["style"] for node in walk(root) if "style" in node.attrs)
    for source in sources:
        values = re.findall(
            r"(?:^|[;{}])\s*animation(?:-iteration-count)?\s*:\s*([^;{}]*)",
            strip_comments(source), flags=re.I,
        )
        for value in values:
            if re.search(r"(?<![\w-])infinite(?![\w-])", value, flags=re.I):
                findings.append("motion-stop: infinite は使わない。アニメーションは繰り返さない")


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
        has_step_button = any(
            descendant.tag == "button" and "data-step" in descendant.attrs
            for descendant in walk(node)
        )
        if not has_step_button:
            findings.append(f"motion-fig: {role} の図に button[data-step] が無い。図の中に「1本ずつ見る」ボタンを置く")
